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

  DEF_SITE_SCOPE_PATH = 'site'
  DEF_SITE_LINK_ID = 'home'
  DEF_SITE_HOME_DOC_LINK_ID = 'home'

  def __init__(self, model=soc.models.site.Site,
               base_model=soc.models.presence.Presence):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model)

  def getKeyValues(self, unused_entity):
    """Returns the default key values for the site settings.

    The Site entity is always expected to be a singleton, so this method
    returns the hard-coded scope and link_id.
    """

    return [self.DEF_SITE_SCOPE_PATH, 
            self.DEF_SITE_LINK_ID]


logic = Logic()
