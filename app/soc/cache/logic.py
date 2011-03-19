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

"""Module contains logic memcaching functions.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache
from google.appengine.ext import db

import soc.cache.base


def key(model, filter, order, *args, **kwargs):
  """Returns the memcache key for this query.
  """

  new_filter = {}

  for filter_key, value in filter.iteritems():
    if isinstance(value, db.Model):
      new_value = value.key().id_or_name()
    else:
      new_value = value
    new_filter[filter_key] = new_value

  return 'query_for_%(kind)s_%(filter)s_%(order)s' % {
      'kind': repr(model.kind()),
      'filter': repr(new_filter),
      'order': repr(order),
      }


def get(model, filter, order, *args, **kwargs):
  """Retrieves the data for the specified query from the memcache.
  """

  memcache_key = key(model, filter, order)
  # pylint: disable=E1101
  return memcache.get(memcache_key), memcache_key


def add(data, memcache_key, *args, **kwargs):
  """Adds the data for the specified query in the memcache.

  The data is added if and only if it is not already stored.

  Args:
    data: the data to be cached
  """

  # Store data for fifteen minutes to force a refresh every so often
  retention = 15*60
  # pylint: disable=E1101
  memcache.add(memcache_key, data, retention)


def set(data, memcache_key):
  """Sets the data for the specified query in the memcache.

  The data is always added to memcache.

  Args:
    data: the data to be cached
  """

  # Store data for fifteen minutes to force a refresh every so often
  retention = 15*60
  # pylint: disable=E1101
  memcache.set(memcache_key, data, retention)


def flush(model, filter):
  """Removes the data for the current user from the memcache.
  """

  memcache_key = key(model, filter)
  # pylint: disable=E1101
  memcache.delete(memcache_key)


# define the cache functions
cache = soc.cache.base.getSoftCacher(get, add)
force_cache = soc.cache.base.getHardCacher(key, set)
