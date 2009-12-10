#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""GradingSurveyGroup (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import base
from soc.logic.models import program as program_logic

from soc.modules.gsoc.logic.models.grading_record import logic as record_logic

import soc.modules.gsoc.models.grading_survey_group


class Logic(base.Logic):
  """Logic methods for the GradingSurveyGroup model.
  """

  def __init__(self,
      model=soc.modules.gsoc.models.grading_survey_group.GradingSurveyGroup,
      base_model=None, scope_logic=program_logic,
      record_logic=record_logic):
    """Defines the name, key_name and model for this entity.
    """

    self.record_logic = record_logic

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def getRecordLogic(self):
    """Returns Record logic belonging to the GradingSurveyGroup
    """
    return self.record_logic


logic = Logic()
