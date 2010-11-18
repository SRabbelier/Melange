#!/usr/bin/env python2.5
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
  '"Doug Coker" <dcoker@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache

from soc.logic.helper import xsrfutil
from soc.logic.models import presence_with_tos

import soc.models.presence_with_tos
import soc.models.site


class Logic(presence_with_tos.Logic):
  """Logic methods for the Site model.
  """

  DEF_SITE_LINK_ID = 'site'

  def __init__(self, model=soc.models.site.Site,
               base_model=soc.models.presence_with_tos.PresenceWithToS):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model)

  def getKeyValuesFromEntity(self, entity):
    """Returns the key values for the site settings.

    The Site entity is a singleton, so this method returns
    a hard-coded link_id.

    Args:
      entity: unused
    """

    return [self.DEF_SITE_LINK_ID]

  def getKeyValuesFromFields(self, fields):
    """Extracts the key values from a dict and returns them.

    The Site entity is a singleton, so this method returns
    a hard-coded link_id.

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

  def getSingleton(self):
    """Return singleton Site settings entity, since there is always only one.
    """

    fields = {
        'link_id': self.DEF_SITE_LINK_ID,
        }

    key_name = self.getKeyNameFromFields(fields)
    singleton = self.getFromKeyName(key_name)

    # if there is no site singleton yet, create it
    if not singleton:
      singleton = self.updateOrCreateFromKeyName(fields, key_name)

    return singleton

  def getXsrfSecretKey(self, settings):
    """Return the secret key for use by the XSRF middleware.

    If the Site entity does not have a secret key, this method will also create
    one and persist it.

    Args:
      settings: the singleton Site entity

    Returns:
      a secret key.
    """
    if not settings.xsrf_secret_key:
      key = xsrfutil.newXsrfSecretKey()
      if not memcache.add("new_xsrf_secret_key", key):
        key = memcache.get("new_xsrf_secret_key")
      settings.xsrf_secret_key = key
      settings.put()
    return settings.xsrf_secret_key


logic = Logic()
