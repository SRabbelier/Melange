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

"""GHOPMentor (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic.models import mentor

import soc.models.mentor

import soc.modules.ghop.logic.models.organization
import soc.modules.ghop.models.mentor


class Logic(mentor.Logic):
  """Logic methods for the GHOPMentor model.
  """

  def __init__(self, model=soc.modules.ghop.models.mentor.GHOPMentor,
               base_model=soc.models.mentor.Mentor,
               scope_logic=soc.modules.ghop.logic.models.organization,
               role_name='ghop_mentor', disallow_last_resign=False):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic, role_name=role_name,
                                disallow_last_resign=disallow_last_resign)

  def getRoleLogicsToNotifyUponNewRequest(self):
    """Returns a list with OrgAdmin logic which can be used to notify all
    appropriate Organization Admins.
    """

    from soc.modules.ghop.logic.models.org_admin import logic as \
        org_admin_logic

    return [org_admin_logic]


logic = Logic()
