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

"""Module contains homepage memcaching functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import logging

from google.appengine.api import memcache

from soc.logic import accounts
from soc.logic import system

import soc.cache.base


def key(entity):
  """Returns the memcache key for an entities homepage.
  """

  host = system.getRawHostname()
  version = system.getAppVersion()
  kind = entity.kind()
  key = entity.key().id_or_name()

  return 'homepage_for_%s_%s_%s_%s' % (host, version, kind, key)


def get(self, *args, **kwargs):
  """Retrieves the homepage for the specified entity from the memcache.
  """

  # only cache the page for non-logged-in users
  # TODO: figure out how to cache everything but the sidebar
  # also, no need to normalize as we don't use it anyway
  if accounts.getCurrentAccount(normalize=False):
    return (None, None)

  entity = self._logic.getFromKeyFields(kwargs)

  # if we can't retrieve the entity, leave it to the actual method
  if not entity:
    return (None, None)

  memcache_key = key(entity)
  logging.info("Retrieving %s" % memcache_key)
  # pylint: disable-msg=E1101
  return memcache.get(memcache_key), memcache_key

def put(result, memcache_key, *args, **kwargs):
  """Sets the homepage for the specified entity in the memcache.

  Args:
    result: the homepage to be cached
  """

  # no sense in storing anything if we won't query it later on
  # also, no need to normalize as we don't use it anyway
  if accounts.getCurrentAccount(normalize=False):
    return

  # Store homepage for just ten minutes to force a refresh every so often
  retention = 10*60

  logging.info("Setting %s" % memcache_key)
  # pylint: disable-msg=E1101
  memcache.add(memcache_key, result, retention)


def flush(entity):
  """Removes the homepage for the current entity from the memcache.

  Also calls soc.cache.rights.flush for the specified user.

  Args:
    id: defaults to the current account if not set
  """

  memcache_key = key(entity)
  logging.info("Flushing %s" % memcache_key)
  # pylint: disable-msg=E1101
  memcache.delete(memcache_key)


# define the cache function
cache = soc.cache.base.getSoftCacher(get, put)
