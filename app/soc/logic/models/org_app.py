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

"""Organization Application (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import group_app
from soc.logic.models import program as program_logic

import soc.models.group_app
import soc.models.org_app

class Logic(group_app.Logic):
  """Logic methods for the Organization Application model.
  """

  def __init__(self, model=soc.models.org_app.OrgApplication,
               base_model=soc.models.group_app.GroupApplication,
               scope_logic=program_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
        scope_logic=program_logic)


logic = Logic()
