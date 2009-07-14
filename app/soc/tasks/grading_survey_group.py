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

"""Tasks related to Grading Survey Groups.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime
import logging

from google.appengine.api.labs import taskqueue

from django import http

from soc.tasks.helper import error_handler


# batch size to use when going through StudentProjects
DEF_BATCH_SIZE = 10


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [(
      r'tasks/grading_survey_group/update_records$',
      'soc.tasks.grading_survey_group.updateOrCreateRecordsForSurveyGroup'),
              (
      r'tasks/grading_survey_group/update_projects$',
      'soc.tasks.grading_survey_group.updateProjectsForSurveyGroup'),
              (
      r'tasks/grading_survey_group/mail_result$',
      'soc.tasks.grading_survey_group.sendMailAboutGradingRecordResult')]

  return patterns


def updateOrCreateRecordsForSurveyGroup(request, *args, **kwargs):
  """Updates or creates GradingRecords for the given GradingSurveyGroup.

  Expects the following to be present in the POST dict:
    group_key: Specifies the GradingSurveyGroup key name.
    project_key: optional to specify which project was the last for which this
                 task was run
  Args:
    request: Django Request object
  """

  from soc.logic.models.grading_record import logic as grading_record_logic
  from soc.logic.models.grading_survey_group import logic as survey_group_logic
  from soc.logic.models.student_project import logic as student_project_logic

  post_dict = request.POST

  group_key = post_dict.get('group_key')

  if not group_key:
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid updateRecordForSurveyGroup data: %s' % post_dict)

  # get the GradingSurveyGroup for the given keyname
  survey_group_entity = survey_group_logic.getFromKeyName(group_key)

  if not survey_group_entity:
    # invalid GradingSurveyGroup specified, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid GradingSurveyGroup specified: %s' % group_key)

  # check and retrieve the project_key that has been done last
  if 'project_key' in post_dict:
    project_start_key = post_dict['project_key']
  else:
    project_start_key = None

  # get all valid StudentProjects from starting key
  fields = {'program': survey_group_entity.scope,
            'status': ['accepted', 'failed', 'completed']}

  if project_start_key:
    # retrieve the last project that was done
    project_start = student_project_logic.getFromKeyName(project_start_key)

    if not project_start:
      # invalid starting project key specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid Student Project Key specified: %s' %(project_start_key))

    fields['__key__ >'] = project_start.key()

  # get the first batch_size number of StudentProjects
  project_entities = student_project_logic.getForFields(fields,
                                                        limit=DEF_BATCH_SIZE)

  # update/create and batch put the new GradingRecords
  grading_record_logic.updateOrCreateRecordsFor(survey_group_entity,
                                                project_entities)

  if len(project_entities) == DEF_BATCH_SIZE:
    # spawn new task starting from the last
    new_project_start = project_entities[DEF_BATCH_SIZE-1].key().id_or_name()

    # pass along these params as POST to the new task
    task_params = {'group_key': group_key,
                   'project_key': new_project_start}
    task_url = '/tasks/grading_survey_group/update_records'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()
  else:
    # task completed, update timestamp for last update complete
    fields = {'last_update_complete': datetime.datetime.now()}
    survey_group_logic.updateEntityProperties(survey_group_entity, fields)

  # task completed, return OK
  return http.HttpResponse('OK')


def updateProjectsForSurveyGroup(request, *args, **kwargs):
  """Updates each StudentProject for which a GradingRecord is found.

  Expects the following to be present in the POST dict:
    group_key: Specifies the GradingSurveyGroup key name.
    record_key: Optional, specifies the key of the last processed
                GradingRecord.
    send_mail: Optional, if this string evaluates to True mail will be send
               for each GradingRecord that's processed.

  Args:
    request: Django Request object
  """

  from soc.logic.models.grading_record import logic as grading_record_logic
  from soc.logic.models.grading_survey_group import logic as survey_group_logic
  from soc.logic.models.student_project import logic as student_project_logic

  post_dict = request.POST

  group_key = post_dict.get('group_key')

  if not group_key:
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid updateRecordForSurveyGroup data: %s' % post_dict)

  # get the GradingSurveyGroup for the given keyname
  survey_group_entity = survey_group_logic.getFromKeyName(group_key)

  if not survey_group_entity:
    # invalid GradingSurveyGroup specified, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid GradingSurveyGroup specified: %s' % group_key)

  # check and retrieve the record_key that has been done last
  if 'record_key' in post_dict and post_dict['record_key'].isdigit():
    record_start_key = int(post_dict['record_key'])
  else:
    record_start_key = None

  # get all valid StudentProjects from starting key
  fields = {'grading_survey_group': survey_group_entity}

  if record_start_key:
    # retrieve the last record that was done
    record_start = grading_record_logic.getFromID(record_start_key)

    if not record_start:
      # invalid starting record key specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid GradingRecord Key specified: %s' %(record_start_key))

    fields['__key__ >'] = record_start.key()

  # get the first batch_size number of GradingRecords
  record_entities = grading_record_logic.getForFields(fields,
                                                      limit=DEF_BATCH_SIZE)

  student_project_logic.updateProjectsForGradingRecords(record_entities)

  # check if we need to send an email for each GradingRecord
  send_mail = post_dict.get('send_mail', '')

  if send_mail:
    # enqueue a task to send mail for each GradingRecord
    for record_entity in record_entities:
      # pass along these params as POST to the new task
      task_params = {'record_key': record_entity.key().id_or_name()}
      task_url = '/tasks/grading_survey_group/mail_result'

      mail_task = taskqueue.Task(params=task_params, url=task_url)
      mail_task.add('mail')

  if len(record_entities) == DEF_BATCH_SIZE:
    # spawn new task starting from the last
    new_record_start = record_entities[DEF_BATCH_SIZE-1].key().id_or_name()

    # pass along these params as POST to the new task
    task_params = {'group_key': group_key,
                   'record_key': new_record_start,
                   'send_mail': send_mail}
    task_url = '/tasks/grading_survey_group/update_projects'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()

  # task completed, return OK
  return http.HttpResponse('OK')


def sendMailAboutGradingRecordResult(request, *args, **kwargs):
  """Sends out a mail about the result of one GradingRecord.

  Expects the following to be present in the POST dict:
    record_key: Specifies the key for the record to process.

  Args:
    request: Django Request object
  """

  from soc.logic import mail_dispatcher
  from soc.logic.models.grading_record import logic as grading_record_logic
  from soc.logic.models.org_admin import logic as org_admin_logic
  from soc.logic.models.site import logic as site_logic

  post_dict = request.POST

  # check and retrieve the record_key that has been done last
  if 'record_key' in post_dict and post_dict['record_key'].isdigit():
    record_key = int(post_dict['record_key'])
  else:
    record_key = None

  if not record_key:
    # no GradingRecord key specified, log and return OK
    error_handler.logErrorAndReturnOK(
        'No valid record_key specified in POST data: %s' % request.POST)

  record_entity = grading_record_logic.getFromID(record_key)

  if not record_entity:
    # no valid GradingRecord key specified, log and return OK
    error_handler.logErrorAndReturnOK(
        'No valid GradingRecord key specified: %s' % record_key)

  survey_group_entity = record_entity.grading_survey_group
  project_entity = record_entity.project
  student_entity = project_entity.student
  mentor_entity = project_entity.mentor
  org_entity = project_entity.scope
  site_entity = site_logic.getSingleton()

  mail_context = {
    'survey_group': survey_group_entity,
    'grading_record': record_entity,
    'project': project_entity,
    'organization': org_entity,
    'site_name': site_entity.site_name,
    'to_name': student_entity.name()
  }

  # set the sender
  (sender, sender_address) = mail_dispatcher.getDefaultMailSender()
  mail_context['sender'] = sender_address

  # set the receiver and subject
  mail_context['to'] = student_entity.email
  mail_context['cc'] = [mentor_entity.email]
  mail_context['subject'] = '%s results processed for %s' %(
      survey_group_entity.name, project_entity.title)

  # find all org admins for the project's organization
  fields = {'scope': org_entity,
            'status': 'active'}
  org_admin_entities = org_admin_logic.getForFields(fields)

  # collect email addresses for all found org admins
  org_admin_addresses = []

  for org_admin_entity in org_admin_entities:
    org_admin_addresses.append(org_admin_entity.email)

  if org_admin_addresses:
    mail_context['cc'].extend(org_admin_addresses)

  # send out the email using a template
  mail_template = 'soc/grading_record/mail/result.html'
  mail_dispatcher.sendMailFromTemplate(mail_template, mail_context)

  # return OK
  return http.HttpResponse()
