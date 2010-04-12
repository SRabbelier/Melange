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

"""Module containing some basic caching functions.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from functools import wraps


def getSoftCacher(get, add):
  """Returns a caching decorator that uses get and add.

  Its main attitude is that the desired key is looked up in the current cache
  memory and if it is found, the associated value is returned. Otherwise,
  the data store is queried.
  """

  # TODO(SRabbelier) possibly accept 'key' instead, and define
  # get and put in terms of key, depends on further usage

  def cache(func):
    """Decorator that caches the result from func.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
      """Decorator wrapper method.
      """
      result, key = get(*args, **kwargs)
      if result:
        return result

      result = func(*args, **kwargs)

      if key:
        add(result, key, *args, **kwargs)

      return result

    return wrapper

  return cache


def getHardCacher(key, set):
  """ Returns a caching function that puts data in cache.

  It is a hard cacher as it always writes new data into the cache memory and
  possibly overrides the existing one. 
  """

  def cache(*args, **kwargs):
    """ Sets data in cache.
    """

    memcache_key = key(*args, **kwargs)
    data = kwargs.get('data')
    if memcache_key and data:
      set(data, memcache_key)

  return cache
