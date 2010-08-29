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

"""GCI specific views for Timeline.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import timeline

from soc.modules.gci.logic.models import program as gci_program_logic
from soc.modules.gci.views.helper import access as gci_access

import soc.modules.gci.logic.models.timeline


class View(timeline.View):
  """View methods for the GCI Timeline model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['edit'] = [('checkCanEditTimeline', [gci_program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.timeline.logic
    new_params['rights'] = rights

    new_params['name'] = "GCI Timeline"
    new_params['module_name'] = "timeline"

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/timeline'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)


view = View()

edit = decorators.view(view.edit)
public = decorators.view(view.public)
