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

"""Views for GradingSurveyGroup.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import access
from soc.views.models import base

import soc.logic.models.grading_survey_group


class View(base.View):
  """View methods for the GradingSurveyGroup model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsDeveloper']
    rights['delete'] = ['checkIsDeveloper']
    rights['show'] = ['checkIsDeveloper']
    rights['list'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = soc.logic.models.grading_survey_group.logic
    new_params['rights'] = rights
    new_params['name'] = "Grading Survey Group"

    new_params['no_admin'] = True
    new_params['no_create_raw'] = True
    new_params['no_create_with_key_fields'] = True

    patterns = []

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
