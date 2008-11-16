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

"""Logic related to handling dictionaries
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


def filter(target, keys):
  """Filters a dictonary to only allow items with the given keys.
  
  Args:
    target: The dictionary that is to be filtered
    keys: The list with keys to filter the dictionary on
  
  Returns:
    A dictionary that only contains the (key,value) from target that have their key in keys
  """
  result = {}
  
  for key, value in target.iteritems():
    if key in keys:
      result[key] = value
  
  return result


def merge(target, updates):
  """Like the builtin 'update' method but does not overwrite existing values.

  Args:
    target: The dictionary that is to be updated, may be None
    updates: A dictionary containing new values for the original dict

  Returns:
    the target dict, with any missing values from updates merged in, in-place 
  """

  if not target:
    target = {}

  for key, value in updates.iteritems():
    if key not in target:
      target[key] = value

  return target


def zip(keys, values):
  """Returns a dict containing keys with values.

  If there are more items in keys than in values, None will be used.
  If there are more items in values than in keys, they will be ignored.

  Args:
    keys: the keys for the dictionary
    values: the values for the dictionary
  """

  result = {}

  size = len(keys)

  for i in range(size):
    if i < len(values):
      value = values[i]
    else:
      value = None
    key = keys[i]
    result[key] = value

  return result

def rename(target, keys):
  """Returns a dict containing only the key/value pairs from keys

  The keys from target will be looked up in keys, and the corresponding
  value from keys will be used instead. If a key is not found, it is skipped.

  Args:
    target: the dictionary to filter
    keys: the fields to filter
  """

  result = {}

  for key, value in target.iteritems():
    if key in keys:
      new_key = keys[key]
      result[new_key] = value

  return result
