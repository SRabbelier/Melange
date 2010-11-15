#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Module contains singleton memcaching functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache

from soc.modules import callback

import soc.cache.base


def key(logic):
  """Returns the memcache key for the user's sidebar.
  """

  return 'singleton_for_%s' % logic._model.kind()


def get(logic):
  """Retrieves the singleton for the specified entity from the memcache.
  """

  store_key = key(logic)
  core = callback.getCore()

  return core.getRequestValue(store_key), store_key


def add(entity, store_key, logic):
  """Adds the singleton for the specified entity in the memcache.
  """

  core = callback.getCore()

  core.setRequestValue(store_key, entity)


# define the cache function
cache = soc.cache.base.getSoftCacher(get, add)
