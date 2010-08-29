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

"""GCI specific views for Org Admins.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import org_admin

from soc.modules.gci.logic.models import organization as gci_org_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import student as gci_student_logic
from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import organization as gci_org_view

import soc.modules.gci.logic.models.org_admin


class View(org_admin.View):
  """View methods for the GCI OrgAdmin model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the org_admin View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [
        ('checkIsMyActiveRole', gci_org_admin_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope',
                         gci_org_admin_logic.logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']]),
        ('checkIsNotStudentForProgramOfOrgInRequest', 
         [gci_org_logic.logic, gci_student_logic.logic])]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[gci_org_admin_logic.logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [gci_org_admin_logic.logic,
             gci_org_admin_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.org_admin.logic
    new_params['group_logic'] = gci_org_logic.logic
    new_params['group_view'] = gci_org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = gci_org_view

    new_params['name'] = "GCI Organization Admin"
    new_params['module_name'] = "org_admin"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/org_admin'

    new_params['role'] = 'gci/org_admin'

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
