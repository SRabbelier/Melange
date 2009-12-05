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

"""Views for GSoCOrganization.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import dicts
from soc.logic.models.org_app import logic as org_app_logic
from soc.views.helper import decorators
from soc.views.models import organization
from soc.views.models import group

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.views.models import program as program_view
from soc.modules.gsoc.views.helper import access


class View(organization.View):
  """View methods for the Organization model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasActiveRoleForKeyFieldsAsScope',
                           org_admin_logic),
                      ('checkGroupIsActiveForLinkId', org_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['public_list'] = ['allow']
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasActiveRoleForKeyFieldsAsScope',
                                org_admin_logic)]
    rights['list_roles'] = [('checkHasActiveRoleForKeyFieldsAsScope',
                             org_admin_logic)]
    rights['applicant'] = [('checkIsApplicationAccepted',
                            org_app_logic)]
    rights['list_proposals'] = [('checkHasAny', [
        [('checkHasActiveRoleForKeyFieldsAsScope', [org_admin_logic]),
         ('checkHasActiveRoleForKeyFieldsAsScope', [mentor_logic])]
        ])]

    new_params = {}
    new_params['logic'] = org_logic
    new_params['rights'] = rights

    new_params['scope_view'] = program_view

    new_params['name'] = "GSoC Organization"
    new_params['module_name'] = "organization"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/org'
    new_params['document_prefix'] = 'gsoc_org'

    new_params['mentor_role_name'] = 'gsoc_mentor'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)


view = View()

admin = decorators.view(view.admin)
#applicant = decorators.view(view.applicant) # TODO
apply_mentor = decorators.view(view.applyMentor)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
home = decorators.view(view.home)
list = decorators.view(view.list)
list_proposals = decorators.view(view.listProposals)
list_public = decorators.view(view.listPublic)
list_requests = decorators.view(view.listRequests)
list_roles = decorators.view(view.listRoles)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
