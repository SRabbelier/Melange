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

"""Views for GSoCMentor.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import mentor

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.views.helper import access
from soc.modules.gsoc.views.models import organization as org_view


class View(mentor.View):
  """View methods for the GSoCMentor model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', mentor_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasRoleForScope', org_admin_logic)]
    rights['accept_invite'] = [
        ('checkIsMyRequestWithStatus', [['group_accepted']]),
        ('checkIsNotStudentForProgramOfOrgInRequest', [org_logic,
                                              student_logic])]
    rights['request'] = [
        ('checkIsNotStudentForProgramOfOrg',
            [org_logic, student_logic]),
        ('checkCanMakeRequestToGroup', org_logic)]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[org_admin_logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [mentor_logic, org_admin_logic])]

    new_params = {}
    new_params['logic'] = mentor_logic
    new_params['group_logic'] = org_logic
    new_params['group_view'] = org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = org_view

    new_params['name'] = "GSoC Mentor"
    new_params['module_name'] = "mentor"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/mentor'

    new_params['role'] = 'gsoc/mentor'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)


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
