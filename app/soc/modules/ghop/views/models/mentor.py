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

"""GHOP specific views for Organization Mentors.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import mentor

import soc.cache.logic

from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import student as ghop_student_logic
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.models import organization as ghop_org_view

import soc.modules.ghop.logic.models.mentor


class View(mentor.View):
  """View methods for the GHOP Mentor model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the mentor View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = ghop_access.GHOPChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', ghop_mentor_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope',
                         ghop_org_admin_logic.logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']]),
        ('checkIsNotStudentForProgramOfOrgInRequest',
         [ghop_org_logic.logic, ghop_student_logic.logic])]
    rights['request'] = [
        ('checkIsNotStudentForProgramOfOrg',
         [ghop_org_logic.logic, ghop_student_logic.logic]),
        ('checkCanMakeRequestToGroup', ghop_org_logic.logic)]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[ghop_org_admin_logic.logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [ghop_mentor_logic.logic,
                                        ghop_org_admin_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.mentor.logic
    new_params['group_logic'] = ghop_org_logic.logic
    new_params['group_view'] = ghop_org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = ghop_org_view

    new_params['name'] = "GHOP Mentor"
    new_params['module_name'] = "mentor"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/mentor'

    new_params['role'] = 'ghop/mentor'

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
role_request = decorators.view(view.request)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)

