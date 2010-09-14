#!/usr/bin/python2.5
#
# Copyright 2010 the Melange authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Appengine Tasks related to GCI Task bulk create.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


import csv
import logging
import StringIO
import time

from django import http

from google.appengine.api.labs import taskqueue
from google.appengine.runtime import DeadlineExceededError

from HTMLParser import HTMLParseError

from htmlsanitizer import HtmlSanitizer
from htmlsanitizer import safe_html

from soc.tasks.helper import error_handler
from soc.tasks.helper.timekeeper import Timekeeper

from soc.modules.gci.logic.models.mentor import logic as mentor_logic
from soc.modules.gci.logic.models.organization import logic as org_logic
from soc.modules.gci.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gci.logic.models.task import logic as task_logic
from soc.modules.gci.models import task as task_model

DATA_HEADERS = ['title', 'description', 'time_to_complete', 'mentors',
                'difficulty', 'task_type', 'arbit_tag']

def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/gci/task/bulk_create_tasks$',
       'soc.modules.gci.tasks.bulk_create.bulkCreateTasks'),]

  return patterns


def spawnBulkCreateTasks(data, admin_key):
  """Spawns a task to bulk post the given data.

  The data given to this method should be in CSV format with the following
  columns:
      title, description, time_to_complete, mentors, difficulty, task_type,
      arbit_tag

  Fields where multiple values are allowed should be comma separated as well.
  These fields are task_type, arbit_tag and mentors. Rows of data which can not
  be properly resolved to form a valid Task will be safely ignored.

  Args:
    data: string with data in csv format
    admin_key: keyname for the GCIOrgAdmin that is uploading these tasks
  """

  task_params = {
      'task_data': data,
      'admin_key': admin_key,
      }
  task_url = '/tasks/gci/task/bulk_create_tasks'

  logging.info('Enqueued bulk_create with: %s' %task_params)
  new_task = taskqueue.Task(params=task_params,
                            url=task_url)
  # add to the gci queue
  new_task.add(queue_name='gci-update')


def bulkCreateTasks(request, *args, **kwargs):
  """Task that creates GCI Tasks from bulk data specified in the POST dict.

  The POST dict should have the following information present:
      admin_key: The keyname for the Org Admin who has uploaded these tasks.
      task_data: The tasks in the CSV format to process.
  """

  # keep track of our own timelimit (20 seconds)
  timelimit = 20000
  timekeeper = Timekeeper(timelimit)

  post_dict = request.POST

  admin_key = post_dict.get('admin_key')
  task_data = post_dict.get('task_data')

  if not admin_key or not task_data:
    error_handler.logErrorAndReturnOK(
        'Not all POST data specified in: %s' % post_dict)

  org_admin = org_admin_logic.getFromKeyName(admin_key)

  if not org_admin or org_admin.status != 'active':
    error_handler.logErrorAndReturnOK(
        'No valid GCIOrgAdmin found for key: %s' % admin_key)

  if not task_data:
    error_handler.logErrorAndReturnOK(
        'Empty or no task data defined in: %s' % post_dict)

  # note that we only query for the quota once
  task_quota = org_logic.getRemainingTaskQuota(org_admin.scope)

  # convert post data on tasks to something that behaves like a file
  task_file = StringIO.StringIO(task_data)
  tasks = csv.DictReader(task_file, fieldnames=DATA_HEADERS)

  completed = True
  for task in tasks:
    try :
      # check if we have time
      timekeeper.ping()

      if task_quota <= 0:
        return error_handler.logErrorAndReturnOK(
            'Task quota reached for %s' %(org_admin.scope.name))

      logging.info('Uncleaned task: %s' %task)
      # clean the data
      if _cleanTask(task, org_admin):
        # set other properties
        task['link_id'] = 't%i' % (int(time.time()*100))
        task['scope'] = org_admin.scope
        task['scope_path'] = org_admin.scope_path
        task['program'] = org_admin.program
        task['status'] = 'Unpublished'
        task['created_by'] = org_admin
        task['modified_by'] = org_admin

        # create a new task
        logging.info('Creating new task with fields: %s' %task)
        task_logic.updateOrCreateFromFields(task)
        task_quota = task_quota -1
      else:
        logging.warning('Invalid Task data: %s' %task)
    except DeadlineExceededError:
      # time to bail out
      completed = False

  if not completed:
    new_task_data = csv.dictWriter(StringIO.StringIO(), DATA_HEADERS)
    for task in tasks:
      new_task_data.write(task)
    spawnBulkCreateTasks(new_task_data.getValue(), admin_key)

  # we're done here
  return http.HttpResponse('OK')


def _cleanTask(task, org_admin):
  """Cleans the data given so that it can be safely stored as a task.

    Args:
      task: Dictionary as constructed by the csv.DictReader().
      org_admin: the Org Admin who is creating these tasks.

    Returns:
        True iff the task dictionary has been successfully cleaned.
  """

  # pop any extra columns added by DictReader.next()
  task.pop(None,None)

  # check title
  if not task['title']:
    logging.warning('No valid title found')
    return False

  # clean description
  try:
    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = task['description']
    cleaner.clean()
  except (HTMLParseError, safe_html.IllegalHTML, TypeError), e:
    logging.warning('Cleaning of description failed with: %s' %e)
    return False
  task['description'] = cleaner.string.strip().replace('\r\n', '\n')

  # clean time to complete
  try:
    task['time_to_complete'] = int(task['time_to_complete'])
  except (ValueError, TypeError), e:
    logging.warning('No valid time to completion found, failed with: %s' %e)
    return False

  # clean mentors
  mentor_ids = set(task['mentors'].split(','))

  mentor_fields = {'scope': org_admin.scope,
                   'status': 'active'}
  mentors = []
  for mentor_id in mentor_ids:
    mentor_fields['link_id'] = mentor_id.strip()
    mentor = mentor_logic.getForFields(mentor_fields, unique=True)
    if mentor:
      mentors.append(mentor.key())

  if not mentors:
    # no valid mentors found
    logging.warning('No valid mentors found')
    return False
  task['mentors'] = mentors

  program_entity = org_admin.program

  # clean task difficulty
  difficulty = task['difficulty'].strip()
  allowed_difficulties = [
      str(x) for x in 
          task_model.TaskDifficultyTag.get_by_scope(program_entity)]
  if not difficulty or difficulty not in allowed_difficulties:
    # no valid difficulty found
    logging.warning('No valid task difficulty found')
    return False
  task['difficulty'] = {
      'tags': task['difficulty'],
      'scope': program_entity
      }

  # clean task types
  task_types = []
  allowed_types = [
      str(x) for x in task_model.TaskTypeTag.get_by_scope(program_entity)]
  for task_type in set(task['task_type'].split(',')):
    task_type = task_type.strip()
    if task_type in allowed_types:
      task_types.append(task_type)

  if not task_types:
    # no valid task types found
    logging.warning('No valid task type found')
    return False
  task['task_type'] = {
      'tags': task_types,
      'scope': program_entity
      }

  # clean task tags
  arbit_tags = []
  for tag in set(task['arbit_tag'].split(',')):
    arbit_tags.append(tag.strip())
  task['arbit_tag'] = {
      'tags': arbit_tags,
      'scope': program_entity
      }

  return True
