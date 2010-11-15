#!/usr/bin/python2.5
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

"""Statistic (Model) query functions.
"""

__authors__ = [
    '"Daniel Hans" <Daniel.M.Hans@gmail.com>',
  ]


from soc.logic import dicts

from soc.views.helper import decorators as view_decorators

from soc.modules.gsoc.logic.models.program import logic as gsoc_program_logic
from soc.modules.statistic.views.models import statistic


class View(statistic.View):
  """View methods for the GSoC Statistics.
  """

  def __init__(self, params={}):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Args:
      params: a dict with params for this View

    """

    new_params = {}

    new_params['url_name'] = 'gsoc/statistic'
    new_params['module_name'] = 'gsoc_statistic'
    new_params['program_logic'] = gsoc_program_logic

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

manage_statistics = view_decorators.view(view.manageStatistics)
