#!/usr/bin/env python2.5
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

"""Appengine Tasks related to GCI Task handling.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <dhans@google.com>',
  ]


import datetime

from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from django import http
from django.utils.translation import ugettext

from soc.logic import system
from soc.tasks.helper import error_handler
from soc.views.helper import redirects

from soc.modules.gci.logic.models import student_ranking \
    as gci_student_ranking_logic
from soc.modules.gci.logic.models import task as gci_task_logic


DEF_TASK_UPDATE_SUBJECT_FMT = ugettext('[GCI Task Update] %(title)s')


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [
      (r'^tasks/gci/task/update$',
       'soc.modules.gci.tasks.task_update.updateGCITask'),
      (r'^tasks/gci/task/mail/create$',
       'soc.modules.gci.tasks.task_update.createNotificationMail'),
      (r'^tasks/gci/task/update/student_status$',
       'soc.modules.gci.tasks.task_update.updateTasksPostStudentSignUp')]

  return patterns


def spawnUpdateTask(entity):
  """Spawns a task to update the state of the task. 
  """

  update_params = {
      'gci_task_key': entity.key().name(),
      }
  update_url = '/tasks/gci/task/update'

  new_task = taskqueue.Task(eta=entity.deadline,
                            params=update_params,
                            url=update_url)
  new_task.add('gci-update')


def updateGCITask(request, *args, **kwargs):
  """Method executed by Task Queue API to update a GCI Task to
  relevant state.

  Expects the gci_task_key entry to be present in the POST dict.

  Args:
    request: the standard Django HTTP request object 
  """

  post_dict = request.POST

  key_name = post_dict.get('gci_task_key')

  if not key_name:
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid updateGCITask data: %s' % post_dict)

  entity = gci_task_logic.logic.getFromKeyNameOr404(key_name)

  entity, comment_entity = gci_task_logic.logic.updateTaskStatus(entity)

  if entity:
    # TODO(madhusudan): does this really mean an unsuccessful update?
    # return OK
    return http.HttpResponse()


def spawnCreateNotificationMail(entity):
  """Spawns a task to send mail to the user who has subscribed to the specific
  task.

  Args:
    entity: The Comment entity for which mails must be sent
  """

  task_params = {
      'comment_key': entity.key().id_or_name(),
      'task_key': entity.parent_key().id_or_name(),
      }
  task_url = '/tasks/gci/task/mail/create'

  new_task = taskqueue.Task(params=task_params, url=task_url)
  new_task.add('mail')


def createNotificationMail(request, *args, **kwargs):
  """Appengine task that sends mail to the subscribed users.

  Expects the following to be present in the POST dict:
    comment_key: Specifies the comment id for which to send the notifications
    task_key: Specifies the task key name for which the comment belongs to

  Args:
    request: Django Request object
  """

  from soc.modules.gci.logic.helper import notifications as gci_notifications

  from soc.modules.gci.logic.models import comment as gci_comment_logic
  from soc.modules.gci.logic.models import task_subscription as \
      gci_task_subscription_logic

  # set default batch size
  batch_size = 10

  post_dict = request.POST

  comment_key = post_dict.get('comment_key')
  task_key = post_dict.get('task_key')

  if not (comment_key and task_key):
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid createNotificationMail data: %s' % post_dict)

  comment_key = long(comment_key)

  # get the task entity under which the specified comment was made
  task_entity = gci_task_logic.logic.getFromKeyName(task_key)

  # get the comment for the given id
  comment_entity = gci_comment_logic.logic.getFromID(
      comment_key, task_entity)

  if not comment_entity:
    # invalid comment specified, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid comment specified: %s/%s' % (comment_key, task_key))

  # check and retrieve the subscriber_start_key that has been done last
  if 'subscriber_start_index' in post_dict:
    subscriber_start_index = post_dict['subscriber_start_index']
  else:
    subscriber_start_index = 0

  # get all subscribers to GCI task
  fields = {
      'task': task_entity,
      }

  ts_entity = gci_task_subscription_logic.logic.getForFields(
      fields, unique=True)

  subscribers = db.get(ts_entity.subscribers[
      subscriber_start_index:subscriber_start_index+batch_size])

  task_url = "http://%(host)s%(task)s" % {
                 'host': system.getHostname(),
                 'task': redirects.getPublicRedirect(
                     task_entity, {'url_name': 'gci/task'}),
                 }

  # create the data for the mail to be sent
  message_properties = {
      'task_url': task_url,
      'redirect_url': "%(task_url)s#c%(cid)d" % {
          'task_url': task_url,
          'cid': comment_entity.key().id_or_name()
          },
      'comment_entity': comment_entity,
      'task_entity': task_entity,
  }

  subject = DEF_TASK_UPDATE_SUBJECT_FMT % {
      'title': task_entity.title, 
      }

  for subscriber in subscribers:
    gci_notifications.sendTaskUpdateMail(subscriber, subject,
                                          message_properties)

  if len(subscribers) == batch_size:
    # spawn task for sending out notifications to next set of subscribers
    next_start = subscriber_start_index + batch_size

    task_params = {
        'comment_key': comment_key,
        'task_key': task_key,
        'subscriber_start_index': next_start
        }
    task_url = '/tasks/gci/task/mail/create'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add('mail')

  # return OK
  return http.HttpResponse()


def updateTasksPostStudentSignUp(request, *args, **kwargs):
  """Appengine task that updates the GCI Tasks after the student signs up.

  Expects the following to be present in the POST dict:
    student_key: Specifies the student key name who registered

  Args:
    request: Django Request object
  """
  from soc.modules.gci.logic.models import student as gci_student_logic

  post_dict = request.POST

  student_key = post_dict.get('student_key')

  if not student_key:
    # invalid student data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid Student data: %s' % post_dict)

  student_entity = gci_student_logic.logic.getFromKeyNameOr404(student_key)

  # retrieve all tasks currently assigned to the user
  task_fields = {
      'user': student_entity.user,
      }
  task_entities = gci_task_logic.logic.getForFields(task_fields)

  # TODO(madhusudan) move this to the Task Logic
  # Make sure the tasks store references to the student as well as
  # closing all tasks that are AwaitingRegistration.
  for task_entity in task_entities:
    task_entity.student = student_entity
    if task_entity.status == 'AwaitingRegistration':
      task_entities.remove(task_entity)

      properties = {
          'status': 'Closed',
          'closed_on': datetime.datetime.utcnow()
          }
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

      gci_student_ranking_logic.logic.updateRanking(task_entity)

      gci_task_logic.logic.updateEntityPropertiesWithCWS(
          task_entity, properties, comment_properties)

  db.put(task_entities)

  # return OK
  return http.HttpResponse()
