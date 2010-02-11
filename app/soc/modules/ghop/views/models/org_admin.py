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

"""GHOP specific views for Org Admins.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import org_admin

from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import student as ghop_student_logic
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.models import organization as ghop_org_view

import soc.modules.ghop.logic.models.org_admin


class View(org_admin.View):
  """View methods for the GHOP OrgAdmin model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the org_admin View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = ghop_access.GHOPChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [
        ('checkIsMyActiveRole', ghop_org_admin_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope',
                         ghop_org_admin_logic.logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']]),
        ('checkIsNotStudentForProgramOfOrgInRequest', 
         [ghop_org_logic.logic, ghop_student_logic.logic])]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[ghop_org_admin_logic.logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [ghop_org_admin_logic.logic,
             ghop_org_admin_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.org_admin.logic
    new_params['group_logic'] = ghop_org_logic.logic
    new_params['group_view'] = ghop_org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = ghop_org_view

    new_params['name'] = "GHOP Organization Admin"
    new_params['module_name'] = "org_admin"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/org_admin'

    new_params['role'] = 'ghop/org_admin'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)


view = View()

accept_invite = decorators.view(view.acceptInvite)
admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
invite = decorators.view(view.invite)
list = decorators.view(view.list)
manage = decorators.view(view.manage)
process_request = decorators.view(view.processRequest)
public = decorators.view(view.public)
export = decorators.view(view.export)
