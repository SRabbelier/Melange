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

"""Converts the DB from an old scheme to a new one.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import http

from soc.models import user as user_model
from soc.logic import accounts
from soc.logic.models.user import logic as user_logic


def convert_user_accounts(*args, **kwargs):
  """Converts all current user accounts to normalized form.
  """

  data = user_logic.getAll(user_model.User.all())

  for user in data:
    normalized = accounts.normalizeAccount(user.account)
    if user.account != normalized:
      user.account = normalized
      user.put()

  return http.HttpResponse('Done')
