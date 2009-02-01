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

"""Club Application (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import group_app

import soc.models.club_app
import soc.models.group_app


class Logic(group_app.Logic):
  """Logic methods for the Club Application model.
  """

  def __init__(self, model=soc.models.club_app.ClubApplication,
               base_model=soc.models.group_app.GroupApplication,
               scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
        scope_logic=scope_logic)

  def getKeyValuesFromEntity(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['link_id']


logic = Logic()
