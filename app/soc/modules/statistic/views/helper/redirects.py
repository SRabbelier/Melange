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

"""Redirect related methods.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


def getManageRedirect(entity, params):
  """Returns manage_statistics redirect for a particular program.
  """

  return '/%s/statistic/manage_statistics/%s' % (
      params['url_prefix'], entity.key().id_or_name())

def getVisualizeRedirect(entity, params):
  """Returns visualize redirect for particular statistic.
  """

  return '/%s/visualize/%s' % (
      params['url_name'], entity.key().id_or_name())
