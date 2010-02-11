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

"""GradingRecord (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.ext import db

from soc.logic.models import base

from soc.modules.gsoc.logic.models.survey_record import grading_logic
from soc.modules.gsoc.logic.models.survey_record import project_logic

import soc.modules.gsoc.models.grading_record


class Logic(base.Logic):
  """Logic methods for the GradingRecord model.
  """

  def __init__(self,
               model=soc.modules.gsoc.models.grading_record.GradingRecord,
               base_model=None, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic, id_based=True)

  def updateOrCreateRecordsFor(self, survey_group, project_entities):
    """Updates or creates a GradingRecord in a batch.

    Args:
      survey_group: GradingSurveyGroup entity
      project_entities: list of project_entities which to process
    """

    records_to_store = []

    query_fields = {'grading_survey_group': survey_group}

    for project_entity in project_entities:
      # set a new project to query for
      query_fields['project'] = project_entity

      # try to retrieve an existing record
      record_entity = self.getForFields(query_fields, unique=True)

      # retrieve the fields that should be set
      record_fields = self.getFieldsForGradingRecord(project_entity,
                                                     survey_group,
                                                     record_entity)

      if not record_entity and project_entity.status in ['failed', 'invalid'] \
          and not record_fields['mentor_record'] \
          and not record_fields['student_record']:
        # Don't create a new GradingRecord for an already failed project which
        # has no records attached. Because it does not matter.
        continue

      if record_entity:
        # update existing GradingRecord
        for key,value in record_fields.iteritems():
          setattr(record_entity, key, value)
      else:
        # create a new GradingRecord
        record_entity = self.getModel()(**record_fields)

      # prepare the new/updated record for storage
      records_to_store.append(record_entity)

    # batch put and return the entities
    return db.put(records_to_store)

  def getFieldsForGradingRecord(self, project, survey_group,
                                record_entity=None):
    """Returns the fields for a GradingRecord.

    See GradingRecord model for description of the grade_decision value.

    Args:
      project: Project entity
      survey_group: a GradingSurveyGroup entity
      record_entity: an optional GradingRecord entity

    Returns:
      Dict containing the fields that should be set on a GradingRecord for this
      GradingSurveyGroup and StudentProject
    """

    # retrieve the two Surveys, student_survey might be None
    grading_survey = survey_group.grading_survey
    student_survey = survey_group.student_survey

    # retrieve a GradingSurveyRecord
    survey_record_fields = {'project': project,
                            'survey': grading_survey}

    grading_survey_record = grading_logic.getForFields(survey_record_fields,
                                                       unique=True)

    if student_survey:
      # retrieve ProjectSurveyRecord
      survey_record_fields['survey'] = student_survey
      project_survey_record = project_logic.getForFields(survey_record_fields,
                                                         unique=True)
    else:
      project_survey_record = None

    # set the necessary fields
    fields = {'grading_survey_group': survey_group,
              'project': project,
              'mentor_record': grading_survey_record,
              'student_record': project_survey_record}

    if not record_entity or not record_entity.locked:
      # find grading decision for new or unlocked records

      if not grading_survey_record:
        # no record found, return undecided
        grade_decision = 'undecided'
      elif not student_survey or project_survey_record:
        # if the grade is True then pass else fail
        grade_decision = 'pass' if grading_survey_record.grade else 'fail'
      else:
        # no ProjectSurveyRecord on file while there is a survey to be taken
        grade_decision = 'fail'

      fields['grade_decision'] = grade_decision

    # return the fields that should be set for a GradingRecord
    return fields

logic = Logic()
