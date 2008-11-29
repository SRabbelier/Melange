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

"""Redirect related methods
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


def getCreateRequestRedirect(entity, params):
  """Returns the create request redirect for the specified entity.
  """

  result ='/request/create/%s/%s/%s' % (
     params['url_name'], params['group_scope'], entity.link_id)
  
  return result


def getEditRedirect(entity, params):
  """Returns the edit redirect for the specified entity.
  """

  suffix = params['logic'].getKeySuffix(entity)
  url_name = params['url_name']
  return '/%s/edit/%s' % (url_name, suffix)


def inviteAcceptedRedirect(entity, _):
  """Returns the redirect for accepting an invite.
  """

  return '/%s/create/%s/%s' % (
      entity.role, entity.scope_path, entity.link_id)
