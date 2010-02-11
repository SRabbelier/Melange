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

"""GHOPWorkSubmission (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]

from soc.logic.models import base

import soc.modules.ghop.models.work_submission


class Logic(base.Logic):
  """Logic methods for the GHOPWorkSubmission model.
  """

  def __init__(
      self,
      model=soc.modules.ghop.models.work_submission.GHOPWorkSubmission,
      id_based=True):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, id_based=id_based)


logic = Logic()
