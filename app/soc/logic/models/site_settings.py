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

"""SiteSettings (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import key_name
from soc.logic.models import base
from soc.logic.models import home_settings

import soc.models.home_settings
import soc.models.site_settings


class Logic(home_settings.Logic):
  """Logic methods for the SiteSettings model.
  """

  DEF_SITE_SETTINGS_PARTIAL_PATH = 'site'
  DEF_SITE_SETTINGS_LINK_NAME = 'home'
  DEF_SITE_HOME_DOC_LINK_NAME = 'home'

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """
    base.Logic.__init__(self, soc.models.site_settings.SiteSettings,
                        base_model=soc.models.home_settings.HomeSettings)

  def getMainKeyValues(self):
    """Returns the default key values for the site settings.
    """

    return [self.DEF_SITE_SETTINGS_PARTIAL_PATH, 
            self.DEF_SITE_SETTINGS_LINK_NAME]


logic = Logic()
