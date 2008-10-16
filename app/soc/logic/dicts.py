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
  ]


def mergeDicts(target, updates):
  """Like the builtin 'update' method but does not overwrite existing values

  Args:
    target: The dictionary that is to be updated, may be None
    updates: A dictionary containing new values for the original dict

  Returns: the target dictionary 
  """

  if not target:
    target = {}

  for key, value in updates.iteritems():
    if key not in target:
      target[key] = value

  return target
