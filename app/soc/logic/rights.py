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

"""Module with rights related methods.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import dicts


class Checker(object):
  """Checker class that maps from prefix and status to membership.
  """

  def __init__(self, rights, prefix):
    """Constructs a Checker for the specified prefix.
    """

    self.rights = rights[prefix]
    self.prefix = prefix

  def getMembership(self, status):
    """Retrieves the membership list for the specified status.
    """

    if status == 'user':
      return ['user']

    if status == 'public':
      return ['anyone']

    return self.rights[status]

  def getMemberships(self):
    """Returns all memberships for the configured prefix.
    """

    extra_rights = {
        'user': ['user'],
        'public': ['anyone'],
        'list': [],
        }

    return dicts.merge(extra_rights, self.rights)
