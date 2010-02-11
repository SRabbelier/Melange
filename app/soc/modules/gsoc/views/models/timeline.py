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

"""Views for GSoCTimeline.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]

from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import timeline

from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.timeline import logic as timeline_logic
from soc.modules.gsoc.views.helper import access

import soc.modules.ghop.logic.models.timeline


class View(timeline.View):
  """View methods for the Timeline model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['edit'] = [('checkCanEditTimeline', [program_logic])]

    new_params = {}
    new_params['logic'] = timeline_logic
    new_params['rights'] = rights

    new_params['name'] = "GSoC Timeline"
    new_params['module_name'] = "timeline"

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/timeline'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)


view = View()

edit = decorators.view(view.edit)
public = decorators.view(view.public)
