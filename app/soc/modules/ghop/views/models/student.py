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

"""GHOP specific views for Student.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.models import student

from soc.modules.ghop.logic.models import mentor as ghop_mentor_logic
from soc.modules.ghop.logic.models import organization as ghop_org_logic
from soc.modules.ghop.logic.models import org_admin as ghop_org_admin_logic
from soc.modules.ghop.logic.models import program as ghop_program_logic
from soc.modules.ghop.logic.models import student as ghop_student_logic
from soc.modules.ghop.views.helper import access as ghop_access
from soc.modules.ghop.views.models import program as ghop_program_view

import soc.modules.ghop.logic.models.student


class View(student.View):
  """View methods for the GHOP Student model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the student View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = ghop_access.GHOPChecker(params)
    rights['edit'] = [('checkIsMyActiveRole', ghop_student_logic.logic)]
    rights['apply'] = [
        'checkIsUser',
        ('checkIsActivePeriod', 
         ['student_signup', 'scope_path', ghop_program_logic.logic]),
        ('checkIsNotParticipatingInProgramInScope', [ghop_program_logic.logic,
        ghop_student_logic.logic, ghop_org_admin_logic.logic,
        ghop_mentor_logic.logic]),
        'checkCanApply']
    rights['manage'] = [('checkIsMyActiveRole', ghop_student_logic.logic)]

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.student.logic
    new_params['rights'] = rights

    new_params['group_logic'] = ghop_program_logic.logic
    new_params['group_view'] = ghop_program_view.view

    new_params['scope_view'] = ghop_program_view

    new_params['name'] = "GHOP Student"
    new_params['module_name'] = "student"
    new_params['sidebar_grouping'] = 'Students'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/student'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)


view = View()

apply = decorators.view(view.apply)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
manage = decorators.view(view.manage)
public = decorators.view(view.public)
export = decorators.view(view.export)
