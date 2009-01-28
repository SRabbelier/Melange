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

"""Module contains sidebar memcaching functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache
from google.appengine.api import users

import soc.cache.base


def key(id):
  """Returns the memcache key for the user's sidebar
  """

  return 'sidebar_for_%s' % repr(id)


def get(id, user):
  """Retrieves the sidebar for the specified user from the memcache
  """

  memcache_key = key(id)
  return memcache.get(memcache_key)


def put(sidebar, id, user):
  """Sets the sidebar for the specified user in the memcache

  Args:
    sidebar: the sidebar to be cached
  """

  # Store sidebar for ten minutes since new programs might get added
  retention = 3*60

  memcache_key = key(id)
  memcache.add(memcache_key, sidebar, retention)


def flush(user=None):
  """Removes the sidebar for the current user from the memcache

  Args:
    user: defaults to the current user if not set
  """

  if not user:
    user = users.get_current_user()

  memcache_key = key(user)
  memcache.delete(memcache_key)


# define the cache function
cache = soc.cache.base.getCacher(get, put)
