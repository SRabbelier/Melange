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

"""Module contains rights memcache functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import memcache


RIGHTS = [
    'checkCanEditTimeline',
    'checkCanMakeRequestToGroup',
    'checkCanProcessRequest',
    'checkHasPickGetArgs',
    'checkHasRoleForScope',
    'checkHasUserEntity',
    'checkIsActive',
    'checkIsAllowedToManageRole',
    'checkIsDeveloper',
    'checkIsDocumentReadable',
    'checkIsDocumentCreatable',
    'checkIsDocumentWritable',
    'checkIsHostForProgram',
    'checkIsLoggedIn',
    'checkIsMyEntity',
    'checkIsMyRequestWithStatus',
    'checkIsUnusedAccount',
    'checkIsUser',
    'checkIsUserSelf',
    'checkNotLoggedIn',
    ]


def flush(id):
  """Flushes all ACL's for the specified account.
  """

  key_prefix = '%s.' % id
  # pylint: disable=E1101
  memcache.delete_multi(RIGHTS, key_prefix=key_prefix)
