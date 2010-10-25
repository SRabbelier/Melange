#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Views for Student Ranking.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


from soc.views.models import base

from soc.logic import dicts

from soc.views.helper import decorators

from soc.modules.gci.views.helper import access as gci_access
from soc.modules.gci.views.models import student as gci_student_view

import soc.modules.gci.logic.models.student_ranking

class View(base.View):
  """View methods for the Tasks.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the task View class
    to provide the user with the necessary views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['any_access'] = ['allow']

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.student_ranking.logic
    new_params['rights'] = rights

    new_params['name'] = "Student Ranking"
    new_params['module_name'] = "student_ranking"
    new_params['sidebar_grouping'] = 'Student Rankings'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/student_ranking'

    new_params['scope_view'] = gci_student_view

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)


view = View()
