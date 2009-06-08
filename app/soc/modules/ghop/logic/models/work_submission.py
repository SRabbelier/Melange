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

import soc.modules.ghop.logic.models.organization
import soc.modules.ghop.models.work_submission


class Logic(linkable.Logic):
  """Logic methods for the GHOPWorkSubmission model.
  """

  def __init__(
      self,
      model=soc.modules.ghop.models.work_submission.GHOPWorkSubmission,
      base_model=soc.models.linkable.Linkable, 
      scope_logic=soc.modules.ghop.logic.models.organization):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)


logic = Logic()
