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

"""SurveyRecord (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import expando_base
from soc.models.survey_record import SurveyRecord
from soc.models.grading_project_survey_record import GradingProjectSurveyRecord
from soc.models.project_survey_record import ProjectSurveyRecord


class Logic(expando_base.Logic):
  """Logic methods for listing results for Surveys.
  """

  def __init__(self, model=SurveyRecord,
               base_model=None, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic, id_based=True)

  def updateOrCreateFromFields(self, entity, properties, clear_dynamic=False):
    """Create a new SurveyRecord, or update an existing one.

    params:
      entity: existing SurveyRecord, if one exists
      properties: the properties to be set
      clear_dynamic: iff True removes all dynamic properties before updating
    """

    if entity:
      if clear_dynamic:
        # remove all dynamic properties before we update
        for prop in entity.dynamic_properties():
          delattr(entity, prop)
      self.updateEntityProperties(entity, properties)
    else:
      entity = super(Logic, self).updateOrCreateFromFields(properties)

    return entity


class ProjectLogic(Logic):
  """Logic class for ProjectSurveyRecord.
  """

  def __init__(self, model=ProjectSurveyRecord,
               base_model=SurveyRecord, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(ProjectLogic, self).__init__(model=model, base_model=base_model,
                                       scope_logic=scope_logic)


class GradingProjectLogic(ProjectLogic):
  """Logic class for GradingProjectSurveyRecord.
  """

  def __init__(self, model=GradingProjectSurveyRecord,
               base_model=ProjectSurveyRecord, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(GradingProjectLogic, self).__init__(model=model,
                                              base_model=base_model,
                                              scope_logic=scope_logic)


logic = Logic()
project_logic = ProjectLogic()
grading_logic = GradingProjectLogic()
