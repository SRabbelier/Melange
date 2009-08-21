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

"""GHOP specific views for Timeline.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import params as params_helper
from soc.views.models import timeline 
from soc.views.sitemap import sidebar

import soc.cache.logic

from soc.modules.ghop.logic.models import program as ghop_program_logic

import soc.modules.ghop.logic.models.timeline


class View(timeline.View):
  """View methods for the GHOP Timeline model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.timeline.logic

    new_params['name'] = "GHOP Timeline"
    new_params['module_name'] = "timeline"

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/timeline'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """See base.View.edit.
    """

    params = dicts.merge(params, self._params)

    key_fields = ghop_program_logic.logic.getKeyFieldsFromFields(kwargs)

    program = ghop_program_logic.logic.getFromKeyFields(key_fields)
    if program:
      params['logic'] = ghop_program_logic.logic.timeline_logic

    timeline_model = ghop_program_logic.logic.timeline_logic

    return super(View, self).edit(request, access_type, page_name=page_name,
                                  params=params, seed=seed, **kwargs)


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
