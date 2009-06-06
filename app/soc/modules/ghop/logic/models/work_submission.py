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

"""GHOPWorkSubmission (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]

from soc.logic.models import linkable

import soc.models.linkable

from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.models import work_submission as \
    ghop_work_submission_model


class Logic(linkable.Logic):
  """Logic methods for the GHOPWorkSubmission model.
  """

  def __init__(self, model=ghop_work_submission_model.GHOPWorkSubmission,
               base_model=soc.models.linkable.Linkable, 
               scope_logic=ghop_org_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)


logic = Logic()
