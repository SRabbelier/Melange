#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Appengine Tasks related to GHOP Task handling.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


import logging
import os

from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django import http
from django.utils.translation import ugettext

from soc.tasks.helper import error_handler
from soc.views.helper import redirects

from soc.modules.ghop.logic.models import task as ghop_task_logic


DEF_TASK_UPDATE_SUBJECT_FMT = ugettext('[GHOP Task Update] %(title)s')


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/ghop/task/update$',
       'soc.modules.ghop.tasks.task_update.updateGHOPTask'),
      (r'^tasks/ghop/task/update/student_status$',
       'soc.modules.ghop.tasks.task_update.updateTasksPostStudentSignUp')]

  return patterns


def spawnUpdateTask(entity):
  """Spawns a task to update the state of the task. 
  """

  update_params = {
      'ghop_task_key': entity.key().name(),
      }
  update_url = '/tasks/ghop/task/update'

  new_task = taskqueue.Task(eta=entity.deadline, 
                            params=update_params,
                            url=update_url)
  new_task.add('ghop-update')


def updateGHOPTask(request, *args, **kwargs):
  """Method executed by Task Queue API to update a GHOP Task to
  relevant state.

  Expects the ghop_task_key entry to be present in the POST dict.

  Args:
    request: the standard Django HTTP request object 
  """

  post_dict = request.POST

  key_name = post_dict.get('ghop_task_key')

  if not key_name:
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid updateGHOPTask data: %s' % post_dict)

  entity = ghop_task_logic.logic.getFromKeyNameOr404(key_name)

  entity, comment_entity, ws_entity = ghop_task_logic.logic.updateTaskStatus(
      entity)

  if entity:
    # TODO(madhusudan): does this really mean an unsuccessful update?
    # return OK
    return http.HttpResponse()


def updateTasksPostStudentSignUp(request, *args, **kwargs):
  """Appengine task that updates the GHOP Tasks after the student signs up.

  Expects the following to be present in the POST dict:
    student_key: Specifies the student key name who registered

  Args:
    request: Django Request object
  """
  from soc.modules.ghop.logic.models import student as ghop_student_logic

  post_dict = request.POST

  student_key = post_dict.get('student_key')

  if not student_key:
    # invalid student data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid Student data: %s' % post_dict)

  student_entity = ghop_student_logic.logic.getFromKeyNameOr404(student_key)

  # retrieve all tasks currently assigned to the user
  task_fields = {
      'user': student_entity.user,
      }
  task_entities = ghop_task_logic.logic.getForFields(task_fields)

  # TODO(madhusudan) move this to the Task Logic
  # Make sure the tasks store references to the student as well as
  # closing all tasks that are AwaitingRegistration.
  for task_entity in task_entities:
    task_entity.student = student_entity
    if task_entity.status == 'AwaitingRegistration':
      task_entities.remove(task_entity)

      properties = {'status': 'Closed'}
      changes = [ugettext('User-MelangeAutomatic'),
                 ugettext('Action-Student registered'),
                 ugettext('Status-%s' % (properties['status']))]

      comment_properties = {
          'parent': task_entity,
          'scope_path': task_entity.key().name(),
          'created_by': None,
          'changes': changes,
          'content': ugettext(
              '(The Melange Automated System has detected that the student '
              'has signed up for the program and hence has closed this task.'),
          }

      ghop_task_logic.logic.updateEntityPropertiesWithCWS(
          task_entity, properties, comment_properties)

  db.put(task_entities)

  # return OK
  return http.HttpResponse()
