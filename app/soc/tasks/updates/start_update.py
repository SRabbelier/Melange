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

"""Version update Tasks runner.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import http
from django.template import loader
from django.utils.translation import ugettext

from soc.tasks.helper import error_handler
from soc.tasks.updates import module_conversion
from soc.tasks.updates import student_school_type
from soc.views.helper import responses


def getDjangoURLPatterns():
  """Returns the URL patterns for the views in this module.
  """

  patterns = [
      (r'tasks/update/start$', 'soc.tasks.updates.start_update.startTasks'),
      (r'tasks/update/start/([0-9_a-z]+)$',
       'soc.tasks.updates.start_update.start_task'),
      (r'tasks/update/run/([0-9_a-z]+)$',
       'soc.tasks.updates.start_update.run_task')]

  return patterns


def startTasks(request):
  """Presents a view that allows the user to start update tasks.
  """

  template = 'soc/tasks/start_update.html'

  context = responses.getUniversalContext(request)

  options = task_runner.getOptions()

  sorted_keys = []
  for key, option in options.iteritems():
    option['name'] = key
    sorted_keys.append(
        (option['from_version'], option['in_version_order'], key))

  # sort the keys
  sorted_keys.sort()

  # store only the true option
  sorted_options = []

  for key_tuple in sorted_keys:
    option_key = key_tuple[2]
    sorted_options.append(options[option_key])

  context.update(
      page_name='Update Tasks starter',
      options=sorted_options,
      )

  content = loader.render_to_string(template, dictionary=context)
  return http.HttpResponse(content)


class TaskRunner(object):
  """Runs one of the supported tasks.
  """

  STUDENT_SCHOOL_TYPE = {
      'from_version': '0-5-20090914',
      'in_version_order': 1,
      'description': ugettext(
          'Updates due to changes in the Student model. Sets all school_type '
          'entries to University since that was the first type of Student that '
          'was supported.'),
      'starter': student_school_type.startSchoolTypeUpdate,
      'runner': student_school_type.runSchoolTypeUpdate,
      }

  PROGRAM_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 1,
      'description': ugettext(
          'Update that converts Program->GSoCProgram entities for use in the '
          'new Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runProgramConversionUpdate,
      }

  ORG_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 2,
      'description': ugettext(
          'Update that converts Organization->GSoCOrganization entities for '
          'use in the new Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runOrgConversionUpdate,
      }

  ORG_ADMIN_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 3,
      'description': ugettext(
          'Update that converts OrgAdmin->GSoCOrgAdmin entities for '
          'use in the new Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runOrgAdminConversionUpdate,
      }

  MENTOR_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 4,
      'description': ugettext(
          'Update that converts Mentor->GSoCMentor entities for '
          'use in the new Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runMentorConversionUpdate,
      }

  STUDENT_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 5,
      'description': ugettext(
          'Update that converts Student->GSoCStudent entities for '
          'use in the new Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runStudentConversionUpdate,
      }

  STUDENT_PROPOSAL_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 6,
      'description': ugettext(
          'Update that sets the properties in the StudentProposal to match '
          'the new entities in the Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runStudentProposalUpdate,
      }

  REVIEW_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 7,
      'description': ugettext(
          'Update that removes the reviewer property from the Review entity.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runReviewUpdate,
      }

  STUDENT_PROJECT_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 8,
      'description': ugettext(
          'Update that sets the properties in the StudentProject to match '
          'the new entities in the Module system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runStudentProjectUpdate,
      }

  SURVEY_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 9,
      'description': ugettext(
          'Update that changes prefix from Program to GSoCProgram and updates '
          'the necessary references for Surveys.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runSurveyUpdate,
      }

  PROJECT_SURVEY_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 10,
      'description': ugettext(
          'Update that changes prefix from Program to GSoCProgram and updates '
          'the necessary references for ProjectSurveys.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runProjectSurveyUpdate,
      }

  GRADING_PROJECT_SURVEY_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 11,
      'description': ugettext(
          'Update that changes prefix from Program to GSoCProgram and updates '
          'the necessary references for GradingProjectSurveys.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runGradingProjectSurveyUpdate,
      }

  SURVEY_RECORD_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 12,
      'description': ugettext(
          'Update for SurveyRecords to point to the new Surveys'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runSurveyRecordUpdate,
      }

  PROJECT_SURVEY_RECORD_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 13,
      'description': ugettext(
          'Update for ProjectSurveyRecords to point to the new Surveys and '
          'update the Organization reference.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runProjectSurveyRecordUpdate,
      }

  GRADING_PROJECT_SURVEY_RECORD_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 14,
      'description': ugettext(
          'Update for GradingProjectSurveyRecords to point to the new Surveys '
          'and update the Organization reference.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runGradingProjectSurveyRecordUpdate,
      }

  GRADING_SURVEY_GROUP_MODULE = {
      'from_version': '0-5-20091121',
      'in_version_order': 15,
      'description': ugettext(
          'Update for GradingSurveyGroups to point to the new Surveys.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runGradingSurveyGroupUpdate,
      }

  DOCUMENT_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 16,
      'description': ugettext(
          'Update to change the prefixes of Documents to the new Module '
          'system.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runDocumentUpdate,
      }

  TIMELINE_MODULE_CONVERSION = {
      'from_version': '0-5-20091121',
      'in_version_order': 17,
      'description': ugettext(
          'Update to convert Timeline->GSoCTimeline and also update the '
          'Program reference to point to the new GSoCProgram.'),
      'starter': module_conversion.startUpdateWithUrl,
      'runner': module_conversion.runTimelineConversionUpdate,
      }


  def __init__(self):
    """Initializes the TaskRunner.
    """

    self.options = {
        'student_school_type': self.STUDENT_SCHOOL_TYPE,
        'program_module_conversion': self.PROGRAM_MODULE_CONVERSION,
        'org_module_conversion': self.ORG_MODULE_CONVERSION,
        'org_admin_module_conversion': self.ORG_ADMIN_MODULE_CONVERSION,
        'mentor_module_conversion': self.MENTOR_MODULE_CONVERSION,
        'student_module_conversion': self.STUDENT_MODULE_CONVERSION,
        'student_proposal_module': self.STUDENT_PROPOSAL_MODULE,
        'review_module': self.REVIEW_MODULE,
        'student_project_module': self.STUDENT_PROJECT_MODULE,
        'survey_module_conversion': self.SURVEY_MODULE_CONVERSION,
        'project_survey_module_conversion': 
            self.PROJECT_SURVEY_MODULE_CONVERSION,
        'grading_project_survey_module_conversion': 
            self.GRADING_PROJECT_SURVEY_MODULE_CONVERSION,
        'survey_record_module': self.SURVEY_RECORD_MODULE,
        'project_survey_record_module': self.PROJECT_SURVEY_RECORD_MODULE,
        'grading_project_survey_record_module':
            self.GRADING_PROJECT_SURVEY_RECORD_MODULE,
        'grading_survey_group_module': self.GRADING_SURVEY_GROUP_MODULE,
        'document_module_conversion': self.DOCUMENT_MODULE_CONVERSION,
        'timeline_module_conversion': self.TIMELINE_MODULE_CONVERSION,
    }

  def getOptions(self):
    """Returns the supported options.
    """

    return self.options

  def startTask(self, request, option_name):
    """Starts the specified Task for the given option.
    """

    context = responses.getUniversalContext(request)
    context['page_name'] = 'Start Update Task'

    option = self.options.get(option_name)
    if not option:
      template = 'soc/error.html'
      context['message'] = 'Uknown option "%s".' % option_name
    else:
      template = 'soc/tasks/run_update.html'
      context['option'] = option
      context['success'] = option['starter'](request,
                                             self._getRunUpdateURL(option_name))

    content = loader.render_to_string(template, dictionary=context)
    return http.HttpResponse(content)

  def _getRunUpdateURL(self, option):
    """Returns the URL to run a specific update.

    Args:
      option: the update option for which the URL should returned
    """
    return '/tasks/update/run/%s' % option

  def runTask(self, request, option_name, *args, **kwargs):
    """Runs the specified Task for the given option.
    """

    option = self.options.get(option_name)

    if not option:
      error_handler('Uknown Updater option "%s".' % option_name)
    else:
      return option['runner'](request, *args, **kwargs)


task_runner = TaskRunner()
start_task = task_runner.startTask
run_task = task_runner.runTask
