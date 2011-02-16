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

"""Appengine Tasks related to sending emails regarding
parental consent forms.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from google.appengine.ext import db
from google.appengine.api import taskqueue

from django.http import HttpResponse

from soc.tasks.helper import error_handler

from soc.modules.gci.logic.helper import notifications as gci_notifications
from soc.modules.gci.logic.models.program import logic as gci_program_logic
from soc.modules.gci.logic.models.student import logic as gci_student_logic


# batch size to use when going through Student entities.
DEF_BATCH_SIZE = 25

DEF_SPAWN_TASK_URL = '/tasks/gci/parental_consent_form/reminder/mail'

def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  from soc.modules.gci.views.models.program import view as gci_program_view

  program_params = gci_program_view.getParams().copy()

  patterns = [
      (r'^tasks/gci/parental_consent_form/reminder/spawn/%(key_fields_pattern)s$'
          % program_params,
       'soc.modules.gci.tasks.parental_forms.spawnParentalFormMailTask'),
      (r'^tasks/gci/parental_consent_form/reminder/mail$',
       'soc.modules.gci.tasks.parental_forms.sendParentalFormMail')]

  return patterns


def spawnParentalFormMailTask(request, *args, **kwargs):
  """Spawns a task to send remainder email to existing students for sending
  parental consent forms.
  """

  program = gci_program_logic.getFromKeyFields(kwargs)

  if not program:
    return error_handler.logErrorAndReturnOK(
        'Invalid program key name: %(scope)s/%(link_id)s' % kwargs)

  task_params = {
      'program_key': program.key().id_or_name()
      }

  new_task = taskqueue.Task(params=task_params, url=DEF_SPAWN_TASK_URL)
  new_task.add('mail')

  # just to make sure task was spawned
  return HttpResponse('OK')


def sendParentalFormMail(request, *args, **kwargs):
  """Method executed by Task Queue API to send remainder email to
  existing students for sending parental consent forms.

  Optionally accepts the start_key entry to be present in the
  POST dict.

  Args:
    request: the standard Django HTTP request object
  """

  post_dict = request.POST

  program_key = post_dict.get('program_key')
  if not program_key:
    return error_handler.logErrorAndReturnOK(
        'The program key is not specified: %s' % post_dict)

  program = gci_program_logic.getFromKeyName(program_key)
  if not program:
    return error_handler.logErrorAndReturnOK(
        'Invalid program key specified: %s' % program_key)

  fields = {
      'scope': program,
      'parental_form_mail': False,
      }

  start_key = post_dict.get('start_key', None)

  if start_key:
    # retrieve the last student entity that was converted
    start = gci_student_logic.getFromKeyName(start_key)

    if not start:
      # invalid starting student key specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid Student Key specified: %s' %(start_key))

    fields['__key__ >'] = start.key()

  # get the first batch_size number of StudentProjects
  entities = gci_student_logic.getForFields(fields, limit=DEF_BATCH_SIZE)

  for entity in entities:
    gci_notifications.sendParentalConsentFormRequired(
        entity.user, entity.scope)
    gci_student_logic.updateEntityProperties(
        entity, {'parental_form_mail': True})

  if len(entities) == DEF_BATCH_SIZE:
    # spawn new task starting from the last
    new_start = entities[DEF_BATCH_SIZE-1].key().id_or_name()

    # pass along these params as POST to the new task
    task_params = {
        'start_key': new_start,
        'program_key': program_key,
        }

    new_task = taskqueue.Task(params=task_params,
                              url=DEF_SPAWN_TASK_URL)
    new_task.add('mail')

  # return OK
  return HttpResponse('OK')
