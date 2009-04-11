#!/usr/bin/python2.5
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
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache
from google.appengine.ext import db

import soc.cache.base


def key(model, filter, order):
  """Returns the memcache key for this query.
  """

  new_filter = {}

  for filter_key, value in filter.iteritems():
    new_value = value.key().id_or_name() if isinstance(value, db.Model) else value
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
  return memcache.get(memcache_key), memcache_key


def put(data, memcache_key, *args, **kwargs):
  """Sets the data for the specified query in the memcache.

  Args:
    data: the data to be cached
  """

  # Store data for fifteen minutes to force a refresh every so often
  retention = 15*60
  memcache.add(memcache_key, data, retention)


def flush(model, filter):
  """Removes the data for the current user from the memcache.
  """

  memcache_key = key(model, filter)
  memcache.delete(memcache_key)


# define the cache function
cache = soc.cache.base.getCacher(get, put)
