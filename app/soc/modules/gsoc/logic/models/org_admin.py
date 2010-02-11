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

"""GSoCOrgAdmin (Model) query functions.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import org_admin

import soc.models.org_admin

import soc.modules.gsoc.logic.models.organization
import soc.modules.gsoc.models.org_admin


class Logic(org_admin.Logic):
  """Logic methods for the GSoCOrgAdmin model.
  """

  def __init__(self, model=soc.modules.gsoc.models.org_admin.GSoCOrgAdmin,
               base_model=soc.models.org_admin.OrgAdmin,
               scope_logic=soc.modules.gsoc.logic.models.organization,
               role_name='gsoc_org_admin'):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic, role_name=role_name)


logic = Logic()
