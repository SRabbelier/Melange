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

"""Survey (Model) query functions.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.ext import db

from soc.logic.models import linkable as linkable_logic
from soc.logic.models import survey_record as survey_record_logic
from soc.logic.models import work
from soc.models.survey import Survey
from soc.models.survey import SurveyContent
from soc.models.work import Work


class Logic(work.Logic):
  """Logic methods for the Survey model.
  """

  def __init__(self, model=Survey, base_model=Work,
               scope_logic=linkable_logic,
               record_logic=survey_record_logic.logic):
    """Defines the name, key_name and model for this entity.

    params:
      record_logic: SurveyRecordLogic (or subclass) instance for this Survey
    """

    self.record_logic = record_logic

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def createSurvey(self, survey_fields, schema, survey_content=False):
    """Create a new survey from prototype.

    params:
      survey_fields = dict of survey field items (see SurveyContent model)
      schema = metadata about survey fields (SurveyContent.schema)
      survey_content = existing SurveyContent entity
    """

    if not survey_content:
      survey_content = SurveyContent()
    else:
      # wipe clean existing dynamic properties if they exist
      for prop in survey_content.dynamic_properties():
        delattr(survey_content, prop)

    for name, value in survey_fields.items():
      setattr(survey_content, name, value)

    survey_content.schema = str(schema)

    db.put(survey_content)

    return survey_content

  def getSurveyForContent(self, survey_content):
    """Returns the Survey belonging to the given SurveyContent.

    params:
      survey_content: the SurveyContent to retrieve the Survey for.

    returns:
      Survey or subclass if possible else None.
    """

    fields = {'survey_content': survey_content}

    return self.getForFields(fields, unique=True)

  def getRecordLogic(self):
    """Returns SurveyRecordLogic that belongs to this SurveyLogic.
    """

    return self.record_logic

  def getDebugUser(self, survey, this_program):
    """Debugging method impersonates other roles.

    Tests taking survey, saving response, and grading.

    params:
      survey = survey entity
      this_program = program scope of survey
    """

    if 'mentor' in survey.taking_access:
      from soc.models.mentor import Mentor
      role = Mentor.get_by_key_name(
          this_program.key().name() + "/org_1/test")

    if 'student' in survey.taking_access:
      from soc.models.student import Student
      role = Student.get_by_key_name(
          this_program.key().name() + "/test")

    if role: 
      return role.user

  def getKeyValuesFromEntity(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.prefix, entity.scope_path, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['prefix'], fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['prefix', 'scope_path', 'link_id']

  def getScope(self, entity):
    """Gets Scope for entity.

    params:
      entity = Survey entity
    """

    from soc.logic.helper import prefixes

    return prefixes.getOrSetScope(entity)

  def hasRecord(self, survey_entity):
    """Returns True iff the given Survey has at least one SurveyRecord.

    Args:
      survey_entity: a Survey instance
    """

    fields = {'survey': survey_entity}

    record_logic = self.getRecordLogic()
    return record_logic.getQueryForFields(fields).count(1) > 0

  def _onCreate(self, entity):
    """Set the scope of the survey.
    """

    self.getScope(entity)
    super(Logic, self)._onCreate(entity)


logic = Logic()
