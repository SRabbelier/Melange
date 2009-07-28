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


def getStudentProjectSurveyInfo(program_entity):
  """Returns a function that returns information used in a Student Project
  table to show how many evaluations have been available and how
  many have been taken.

  Args:
    program_entity: the program to check the total amount of
                    (Grading)ProjctSurveys for
  """

  from soc.logic.models.survey import grading_logic as grading_survey_logic
  from soc.logic.models.survey import project_logic as project_survey_logic

  fields = {'scope_path': program_entity.key().id_or_name()}

  # count the number of have been active ProjectSurveys
  project_surveys = project_survey_logic.getForFields(fields)
  project_survey_count = len(project_surveys)

  for project_survey in project_surveys:
    if not project_survey_logic.hasAtLeastOneRecord(project_survey):
      project_survey_count = project_survey_count - 1

  # count the number of have been active GradingProjectSurveys
  grading_surveys = grading_survey_logic.getForFields(fields)
  grading_survey_count = len(grading_surveys)

  for grading_survey in grading_surveys:
    if not grading_survey_logic.hasAtLeastOneRecord(grading_survey):
      grading_survey_count = grading_survey_count - 1

  def wrapper(item, _):
    """Wrapper method.
    """

    from soc.logic.models.survey_record import grading_logic
    from soc.logic.models.survey_record import project_logic

    fields = {'project': item}

    # count the amount of records we have on store for this project
    project_record_count = project_logic.getQueryForFields(fields).count()
    grading_record_count = grading_logic.getQueryForFields(fields).count()

    info = {'project_surveys_total': project_survey_count,
            'project_surveys_completed': project_record_count,
            'grading_project_surveys_total': grading_survey_count,
            'grading_project_surveys_completed': grading_record_count}

    return info
  return wrapper
