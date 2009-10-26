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

"""Views for GSoCOrgAdmin.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import mentor

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.views.models import organization as org_view # TODO
from soc.views.helper import access # TODO


class View(mentor.View):
  """View methods for the GSoCMentor model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkIsMyActiveRole', org_admin_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['invite'] = [('checkHasActiveRoleForScope',
                         org_admin_logic)]
    rights['accept_invite'] = ['checkCanCreateFromRequest',
        ('checkIsNotStudentForProgramOfOrgInRequest',
         [org_logic, student_logic])]
    rights['process_request'] = [
        ('checkCanProcessRequest', [[org_admin_logic]])]
    rights['manage'] = [
        ('checkIsAllowedToManageRole', [org_admin_logic, org_admin_logic])]

    new_params = {}
    new_params['logic'] = org_admin_logic
    new_params['group_logic'] = org_logic
    new_params['group_view'] = org_view.view
    new_params['rights'] = rights

    new_params['scope_view'] = org_view

    new_params['name'] = "GSoC Organization Admin"
    new_params['module_name'] = "org_admin"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/org_admin'

    new_params['role'] = 'gsoc/org_admin'

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
public = decorators.view(view.public)
export = decorators.view(view.export)
