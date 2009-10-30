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

"""Views for GSoCProgram.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.helper import access # TODO
from soc.views.models import program

from soc.logic.models.host import logic as host_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic


class View(program.View):
  """View methods for the Program model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasActiveRoleForScope',
        host_logic])]
    rights['edit'] = [('checkIsHostForProgram', [program_logic.logic])]
    rights['delete'] = ['checkIsDeveloper']
    rights['assign_slots'] = [('checkIsHostForProgram', [program_logic.logic])]
    rights['slots'] = [('checkIsHostForProgram', [program_logic.logic])]
    rights['show_duplicates'] = [('checkIsHostForProgram',
        [program_logic.logic])]
    rights['assigned_proposals'] = [('checkIsHostForProgram',
        [program_logic.logic])]
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['accepted_organization_announced_deadline',
         '__all__', program_logic])]
    rights['list_projects'] = [('checkIsAfterEvent',
        ['accepted_students_announced_deadline',
         '__all__', program_logic])]

    new_params = {}
    new_params['logic'] = program_logic
    new_params['rights'] = rights

    new_params['name'] = "GSoC Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/program'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)


view = View()

accepted_orgs = decorators.view(view.acceptedOrgs)
list_projects = decorators.view(view.acceptedProjects)
admin = decorators.view(view.admin)
assign_slots = decorators.view(view.assignSlots)
assigned_proposals = decorators.view(view.assignedProposals)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
show_duplicates = decorators.view(view.showDuplicates)
slots = decorators.view(view.slots)
home = decorators.view(view.home)
pick = decorators.view(view.pick)
