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

"""Tasks related to Surveys.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging
import os

from google.appengine.api.labs import taskqueue

from django import http

from soc.tasks.helper import error_handler


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [(r'tasks/surveys/projects/send_reminder/spawn$',
               'soc.tasks.surveys.spawnRemindersForProjectSurvey'),
              (r'tasks/surveys/projects/send_reminder/send$',
               'soc.tasks.surveys.sendSurveyReminderForProject')]

  return patterns


def spawnRemindersForProjectSurvey(request, *args, **kwargs):
  """Spawns tasks for each StudentProject in the given Program.

  Expects the following to be present in the POST dict:
    program_key: Specifies the program key name for which to loop over all the
                 StudentProjects for
    survey_key: specifies the key name for the ProjectSurvey to send reminders
                for
    survey_type: either project or grading depending on the type of Survey
    project_key: optional to specify which project was the last for which a
                 task was spawn

  Args:
    request: Django Request object
  """
  
  from google.appengine.ext import db

  from soc.logic.models.program import logic as program_logic
  from soc.logic.models.student_project import logic as student_project_logic

  # set default batch size
  batch_size = 10

  post_dict = request.POST

  # retrieve the program_key and survey_key from POST data
  program_key = post_dict.get('program_key')
  survey_key = post_dict.get('survey_key')
  survey_type = post_dict.get('survey_type')

  if not (program_key and survey_key and survey_type):
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid sendRemindersForProjectSurvey data: %s' % post_dict)

  # get the program for the given keyname
  program_entity = program_logic.getFromKeyName(program_key)

  if not program_entity:
    # invalid program specified, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid program specified: %s' % program_key)

  # check and retrieve the project_key that has been done last
  if 'project_key' in post_dict:
    project_start_key = post_dict['project_key']
  else:
    project_start_key = None

  # get all valid StudentProjects from starting key
  fields = {'program': program_entity,
            'status': 'accepted'}

  if project_start_key:
    # retrieve the last project that was done
    project_start = student_project_logic.getFromKeyName(project_start_key)

    if not project_start:
      # invalid starting project key specified, log and return OK
      return error_handler.logErrorAndReturnOK(
          'Invalid Student Project Key specified: %s' %(project_start_key))

    fields['__key__ >'] = project_start.key()

  project_entities = student_project_logic.getForFields(fields,
                                                        limit=batch_size)

  for project_entity in project_entities:
    # pass along these params as POST to the new task
    task_params = {'survey_key': survey_key,
                   'survey_type': survey_type,
                   'project_key': project_entity.key().id_or_name()}
    task_url = '/tasks/surveys/projects/send_reminder/send'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add('mail')

  if len(project_entities) == batch_size:
    # spawn new task starting from the last
    new_project_start = project_entities[batch_size-1].key().id_or_name()

    # pass along these params as POST to the new task
    task_params = {'program_key': program_key,
                   'survey_key': survey_key,
                   'survey_type': survey_type,
                   'project_key': new_project_start}
    task_url = '/tasks/surveys/projects/send_reminder/spawn'

    new_task = taskqueue.Task(params=task_params, url=task_url)
    new_task.add()

  # return OK
  return http.HttpResponse()


def sendSurveyReminderForProject(request, *args, **kwargs):
  """Sends a reminder mail for a given StudentProject and Survey.

  A reminder is only send if no record is on file for the given Survey and 
  StudentProject.

  Expects the following to be present in the POST dict:
    survey_key: specifies the key name for the ProjectSurvey to send reminders
                for
    survey_type: either project or grading depending on the type of Survey
    project_key: key which specifies the project to send a reminder for

  Args:
    request: Django Request object
  """

  from soc.logic import mail_dispatcher
  from soc.logic.models.org_admin import logic as org_admin_logic
  from soc.logic.models.site import logic as site_logic
  from soc.logic.models.student_project import logic as student_project_logic
  from soc.logic.models.survey import grading_logic
  from soc.logic.models.survey import project_logic
  from soc.views.helper import redirects

  post_dict = request.POST

  project_key = post_dict.get('project_key')
  survey_key = post_dict.get('survey_key')
  survey_type = post_dict.get('survey_type')

  if not (project_key and survey_key and survey_type):
    # invalid task data, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid sendSurveyReminderForProject data: %s' % post_dict)

  # set logic depending on survey type specified in POST
  if survey_type == 'project':
    survey_logic = project_logic
  elif survey_type == 'grading':
    survey_logic = grading_logic

  # retrieve the project and survey
  student_project = student_project_logic.getFromKeyName(project_key)

  if not student_project:
    # no existing project found, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid project specified %s:' % project_key)

  survey = survey_logic.getFromKeyName(survey_key)

  if not survey:
    # no existing survey found, log and return OK
    return error_handler.logErrorAndReturnOK(
        'Invalid survey specified %s:' % survey_key)

  # try to retrieve an existing record
  record_logic = survey_logic.getRecordLogic()

  fields = {'project': student_project,
            'survey': survey}
  record_entity = record_logic.getForFields(fields, unique=True)

  if not record_entity:
    # send reminder email because we found no record

    student_entity = student_project.student
    site_entity = site_logic.getSingleton()

    if survey_type == 'project':
      survey_redirect = redirects.getTakeSurveyRedirect(
          survey,{'url_name': 'project_survey'})
      to_role = student_entity
      mail_template = 'soc/project_survey/mail/reminder_gsoc.html'
    elif survey_type == 'grading':
      survey_redirect = redirects.getTakeSurveyRedirect(
          survey,{'url_name': 'grading_project_survey'})
      to_role = student_project.mentor
      mail_template = 'soc/grading_project_survey/mail/reminder_gsoc.html'

    survey_url = "http://%(host)s%(redirect)s" % {
      'redirect': survey_redirect,
      'host': os.environ['HTTP_HOST'],
      }

    # set the context for the mail template
    mail_context = {
        'student_name': student_entity.name(),
        'project_title': student_project.title,
        'survey_url': survey_url,
        'survey_end': survey.survey_end,
        'to_name': to_role.name(),
        'site_name': site_entity.site_name,
    }

    # set the sender
    (sender, sender_address) = mail_dispatcher.getDefaultMailSender()
    mail_context['sender'] = sender_address
    # set the receiver and subject
    mail_context['to'] = to_role.email
    mail_context['subject'] = 'Evaluation Survey "%s" Reminder' %(survey.title)

    # find all org admins for the project's organization
    org_entity = student_project.scope

    fields = {'scope': org_entity,
              'status': 'active'}
    org_admin_entities = org_admin_logic.getForFields(fields)

    # collect email addresses for all found org admins
    org_admin_addresses = []

    for org_admin_entity in org_admin_entities:
      org_admin_addresses.append(org_admin_entity.email)

    if org_admin_addresses:
      mail_context['cc'] = org_admin_addresses

    # send out the email
    mail_dispatcher.sendMailFromTemplate(mail_template, mail_context)

  # return OK
  return http.HttpResponse()
