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

"""Views for Club Admins.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.views.helper import redirects
from soc.views.models import base
from soc.views.models import club as club_view

import soc.logic.models.club_admin


class View(base.View):
  """View methods for the Program model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = soc.logic.models.club_admin.logic

    new_params['scope_view'] = club_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Club Admin"

    new_params['extra_dynaexclude'] = ['user', 'org']

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)



view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export

