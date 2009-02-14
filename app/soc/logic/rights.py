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

"""Module with rights related methods.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import dicts

class Checker(object):
  """Checker class that maps from prefix and status to membership.
  """

  SITE_MEMBERSHIP = {
      'admin': [],
      'restricted': ['host'],
      'member': ['user'],
      }

  CLUB_MEMBERSHIP = {
      'admin': ['host', 'club_admin'],
      'restricted': ['host', 'club_admin'],
      'member': ['host', 'club_admin', 'club_member'],
      }

  SPONSOR_MEMBERSHIP = {
      'admin': ['host'],
      'restricted': ['host'],
      'member': ['host'],
      }

  PROGRAM_MEMBERSHIP = {
      'admin': ['host'],
      'restricted': ['host', 'org_admin'],
      'member': ['host', 'org_admin', 'org_mentor', 'org_student'],
      }

  ORGANIZATION_MEMBERSHIP = {
      'admin': ['host', 'org_admin'],
      'restricted': ['host', 'org_admin', 'org_mentor'],
      'member': ['host', 'org_admin', 'org_mentor', 'org_student'],
      }

  USER_MEMBERSHIP = {
      'admin': ['user_self'],
      'restricted': ['user_self'], # ,'friends'
      'member': ['user'],
      }

  RIGHTS = {
      'site': SITE_MEMBERSHIP,
      'club': CLUB_MEMBERSHIP,
      'sponsor': SPONSOR_MEMBERSHIP,
      'program': PROGRAM_MEMBERSHIP,
      'org': ORGANIZATION_MEMBERSHIP,
      'user': USER_MEMBERSHIP,
      }

  def __init__(self, prefix):
    """Constructs a Checker for the specified prefix.
    """

    self.prefix = prefix
    self.rights = self.RIGHTS[prefix]

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

    return dicts.merge(self.rights, {'user': ['user'], 'public': ['anyone']})
