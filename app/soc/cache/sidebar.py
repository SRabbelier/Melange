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

"""Module contains sidebar memcaching functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache

import soc.cache.base
import soc.cache.rights
import soc.logic.accounts


def key(id):
  """Returns the memcache key for the user's sidebar.
  """

  return 'sidebar_for_%s' % repr(id)


def get(core, id, *args, **kwargs):
  """Retrieves the sidebar for the specified user from the memcache.
  """

  memcache_key = key(id)
  # pylint: disable=E1101
  return memcache.get(memcache_key), memcache_key


def add(sidebar, memcache_key, core, *args, **kwargs):
  """Adds the sidebar for the specified user in the memcache.

  Args:
    sidebar: the sidebar to be cached
  """

  # Store sidebar for just three minutes to force a refresh every so often
  retention = 3*60
  # pylint: disable=E1101
  memcache.add(memcache_key, sidebar, retention)


def flush(id=None):
  """Removes the sidebar for the current user from the memcache.

  Also calls soc.cache.rights.flush for the specified user.

  Args:
    id: defaults to the current account if not set
  """

  if not id:
    id = soc.logic.accounts.getCurrentAccount()

  memcache_key = key(id)
  # pylint: disable=E1101
  memcache.delete(memcache_key)
  soc.cache.rights.flush(id)


# define the cache function
cache = soc.cache.base.getSoftCacher(get, add)
