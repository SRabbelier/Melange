#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""OrgAppSurvey (Model) query functions for the GHOP module.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import org_app_survey
from soc.models.org_app_survey import OrgAppSurvey

from soc.modules.ghop.logic.models.org_app_record import logic as \
    org_app_record_logic
from soc.modules.ghop.logic.models import program as program_logic


class Logic(org_app_survey.Logic):
  """Logic class for OrgAppSurveys within the GHOP module.
  """

  def __init__(self, model=OrgAppSurvey,
               scope_logic=program_logic, record_logic = org_app_record_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, scope_logic=scope_logic,
                                record_logic=record_logic)


logic = Logic()
