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

"""Helpers used for list info functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.views.helper import redirects


DEF_NO_RECORD_AVAILABLE_MESSAGE = ugettext('No Record Available')


def getStudentProposalInfo(ranking, proposals_keys):
  """Returns a function that returns information about the rank and assignment.

  Args:
    ranking: dict with a mapping from Student Proposal key to rank
    proposals_keys: list of proposal keys assigned a slot
  """

  def wrapper(item, _):
    """Wrapper method.
    """
    info = {'rank': ranking[item.key()]}

    if item.key() in proposals_keys:
      info['item_class'] =  'selected'
    else:
      info['item_class'] =  'normal'

    return info
  return wrapper


def setStudentProjectSurveyInfo(list_content, program_entity):
  """Sets the list info to a method that returns information used in a Student
  Project table to show how many evaluations have been available and how
  many have been taken.

  Args:
    list_content: list content for which to set the info
    program_entity: the Program to check the total amount of
                    (Grading)ProjctSurveys for

  Returns:
    The original list_content with info set
  """

  from soc.logic.models.survey import grading_logic as grading_survey_logic
  from soc.logic.models.survey import project_logic as project_survey_logic
  from soc.logic.models.survey_record import grading_logic
  from soc.logic.models.survey_record import project_logic

  if not list_content:
    # this can happen because of the need_content parameter for getListContent
    return list_content

  fields = {'scope_path': program_entity.key().id_or_name()}

  # count the number of have been active ProjectSurveys
  project_surveys = project_survey_logic.getForFields(fields)
  project_survey_count = len(project_surveys)

  for project_survey in project_surveys:
    if not project_survey_logic.hasRecord(project_survey):
      project_survey_count = project_survey_count - 1

  # count the number of have been active GradingProjectSurveys
  grading_surveys = grading_survey_logic.getForFields(fields)
  grading_survey_count = len(grading_surveys)

  for grading_survey in grading_surveys:
    if not grading_survey_logic.hasRecord(grading_survey):
      grading_survey_count = grading_survey_count - 1

  # Pre-store the needed info since Django calls the wrapper method for every
  # info call.
  info_storage = {}

  for item in list_content['data']:
    fields = {'project': item}

    # count the amount of records we have on store for this project
    project_record_count = project_logic.getQueryForFields(fields).count()
    grading_record_count = grading_logic.getQueryForFields(fields).count()

    info = {'project_surveys_total': project_survey_count,
            'project_surveys_completed': project_record_count,
            'grading_project_surveys_total': grading_survey_count,
            'grading_project_surveys_completed': grading_record_count}

    info_storage[item.key()] = info

  def wrapper(item, _):
    """Wrapper method.
    """
    return info_storage[item.key()]

  list_content['info'] = (wrapper, None)
  return list_content


def getProjectSurveyInfoForProject(project_entity, survey_params):
  """Returns a function that returns info for listing Surveys and if possible
  their accompanying record.

  Args:
    project_entity: a StudentProject entity
    survey_params: params for the view of the type of Survey that is listed
  """

  survey_logic = survey_params['logic']
  record_logic = survey_logic.getRecordLogic()

  def wrapper(survey_entity, _):
    """Wrapper method.

    Args:
      survey_entity: a ProjectSurvey (or subclass) entity
    """

    # try to retrieve the SurveyRecord for the given Survey and Project
    fields = {'survey': survey_entity,
              'project': project_entity}
    record_entity = record_logic.getForFields(fields, unique=True)

    info = {'record': record_entity}

    if record_entity:
      # SurveyRecord has been found store the import data in info
      info['taken_by'] = record_entity.user.name
      info['taken_on'] = record_entity.modified
    else:
      info['taken_by'] = DEF_NO_RECORD_AVAILABLE_MESSAGE
      info['taken_on'] = DEF_NO_RECORD_AVAILABLE_MESSAGE

    take_redirect_info = {'survey': survey_entity,
                          'params': survey_params}
    info['take_url'] = redirects.getTakeProjectSurveyRedirect(
        project_entity, take_redirect_info)

    return info
  return wrapper
