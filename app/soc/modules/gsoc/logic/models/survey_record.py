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

"""SurveyRecord (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import survey_record as survey_record_logic
from soc.models.survey_record import SurveyRecord

from soc.modules.gsoc.models.grading_project_survey_record \
    import GradingProjectSurveyRecord
from soc.modules.gsoc.models.project_survey_record import ProjectSurveyRecord



class ProjectLogic(survey_record_logic.Logic):
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


project_logic = ProjectLogic()
grading_logic = GradingProjectLogic()
