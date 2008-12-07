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

"""Site (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic.models import base
from soc.logic.models import presence

import soc.models.presence
import soc.models.site


class Logic(presence.Logic):
  """Logic methods for the Site model.
  """

  DEF_SITE_LINK_ID = 'site'

  def __init__(self, model=soc.models.site.Site,
               base_model=soc.models.presence.Presence):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model)

  def getKeyValues(self, entity):
    """Returns the key values for the site settings.

    The Site entity is a singleton, so this method returns a
    hard-coded link_id.

    Args:
      entity: unused
    """

    return [self.DEF_SITE_LINK_ID]

  def getKeyValuesFromFields(self, fields):
    """Extracts the key values from a dict and returns them.

    The Site entity is a singleton, so this method returns a
    hard-coded link_id.

    Args:
      fields: unused
    """

    return [self.DEF_SITE_LINK_ID]

  def getKeyFieldNames(self):
    """Returns an array with the names of the Key Fields.

    The Site entity is an unscoped singleton, it's key fields consist
    of just the link_id.
    """

    return ['link_id']


logic = Logic()
