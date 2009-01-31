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
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.views.helper import access
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

    # TODO do the proper access checks
    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsDeveloper']
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['list'] = ['checkIsDeveloper']
    rights['list_requests'] = ['checkIsDeveloper']
    rights['list_roles'] = ['checkIsDeveloper']
    # TODO(ljvderijk) implement Org application process
    #rights['applicant'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = soc.logic.models.organization.logic

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Organization"
    new_params['url_name'] = "org"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['public_template'] = 'soc/organization/public.html'
    new_params['list_row'] = 'soc/organization/list/row.html'
    new_params['list_heading'] = 'soc/organization/list/heading.html'

    #TODO(ljvderijk) add cleaning methods to not overwrite existing orgs
    new_params['create_extra_dynafields'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
                                   required=True),
        'clean_link_id': cleaning.clean_link_id('link_id'),
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # TODO(ljvderijk) define several menu items for organizations
    #def _getExtraMenuItems(self, role_description, params=None):


view = View()

create = view.create
delete = view.delete
edit = view.edit
home = view.home
list = view.list
list_requests = view.listRequests
list_roles = view.listRoles
public = view.public
export = view.export
pick = view.pick
