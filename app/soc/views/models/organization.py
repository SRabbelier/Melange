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

"""Views for Organizations.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users

from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.views.helper import redirects
from soc.views.models import group
from soc.views.models import program as program_view

import soc.models.organization
import soc.logic.models.organization


class View(group.View):
  """View methods for the Organization model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = soc.logic.models.organization.logic

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Organization"
    new_params['name_short'] = "Organization"
    new_params['name_plural'] = "Organizations"
    new_params['url_name'] = "org"
    new_params['module_name'] = "organization"

    new_params['create_extra_dynafields'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
                                   required=True),
        'clean_link_id': cleaning.clean_link_id,
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
