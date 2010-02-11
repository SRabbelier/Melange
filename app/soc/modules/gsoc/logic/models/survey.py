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


import logging

from google.appengine.ext import db

from soc.logic.models import linkable as linkable_logic
from soc.logic.models import survey as survey_logic

from soc.models.survey import Survey

from soc.modules.gsoc.logic.models.survey_record import grading_logic as \
    grading_record_logic
from soc.modules.gsoc.logic.models.survey_record import project_logic as \
    project_record_logic

from soc.modules.gsoc.models.grading_project_survey import GradingProjectSurvey
from soc.modules.gsoc.models.grading_record import GradingRecord
from soc.modules.gsoc.models.project_survey import ProjectSurvey


class ProjectLogic(survey_logic.Logic):
  """Logic class for ProjectSurvey.
  """

  def __init__(self, model=ProjectSurvey,
               base_model=Survey, scope_logic=linkable_logic,
               record_logic=project_record_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(ProjectLogic, self).__init__(model=model, base_model=base_model,
                                       scope_logic=scope_logic,
                                       record_logic=record_logic)


class GradingProjectLogic(ProjectLogic):
  """Logic class for GradingProjectSurvey.
  """

  def __init__(self, model=GradingProjectSurvey,
               base_model=ProjectSurvey, scope_logic=linkable_logic,
               record_logic=grading_record_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(GradingProjectLogic, self).__init__(model=model,
                                              base_model=base_model,
                                              scope_logic=scope_logic,
                                              record_logic=record_logic)


project_logic = ProjectLogic()
grading_logic = GradingProjectLogic()
