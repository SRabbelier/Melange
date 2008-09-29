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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]

from google.appengine.ext import db

from soc.logic import key_name

import soc.models.site_settings
import soc.logic.model


def getSiteSettings(path):
  """Returns SiteSettings entity for a given path, or None if not found.  
    
  Args:
    path: a request path of the SiteSettings that uniquely identifies it
  """
  # lookup by Settings:path key name
  name = key_name.nameSiteSettings(path)
  
  if name:
    site_settings = soc.models.site_settings.SiteSettings.get_by_key_name(name)
  else:
    site_settings = None
  
  return site_settings


def updateOrCreateSiteSettings(path, **site_settings_properties):
  """Update existing SiteSettings entity, or create new one with supplied properties.

  Args:
    path: a request path of the SiteSettings that uniquely identifies it
    **site_settings_properties: keyword arguments that correspond to Document entity
      properties and their values

  Returns:
    the SiteSettings entity corresponding to the path, with any supplied
    properties changed, or a new SiteSettings entity now associated with the 
    supplied path and properties.
  """
  # attempt to retrieve the existing Site Settings
  site_settings = getSiteSettings(path)

  if not site_settings:
    # site settings did not exist, so create one in a transaction
    name = key_name.nameSiteSettings(path)
    site_settings = soc.models.site_settings.SiteSettings.get_or_insert(
      name, **site_settings_properties)

  # there is no way to be sure if get_or_insert() returned a new SiteSettings or
  # got an existing one due to a race, so update with site_settings_properties anyway,
  # in a transaction
  return soc.logic.model.updateModelProperties(site_settings, **site_settings_properties)
