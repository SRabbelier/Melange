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

"""GHOP specific views for Programs.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


import datetime

from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import program 
from soc.views.sitemap import sidebar

import soc.cache.logic

from soc.modules.ghop.logic.models import program as ghop_program_logic
import soc.modules.ghop.logic.models.program


class View(program.View):
  """View methods for the GHOP Program model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the program View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = soc.modules.ghop.logic.models.program.logic

    new_params['name'] = "GHOP Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'

    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['url_name'] = 'ghop/program'

    new_params['extra_dynaexclude'] = ['apps_tasks_limit',
                                       'min_slots', 'max_slots',
                                       'slots', 'slot_allocation',
                                       'allocations_visible',
                                       'task_difficulties', 'task_types',
                                       ]

    new_params['create_dynafields'] = [
        {'name': 'task_difficulties_str',
         'base': forms.fields.CharField,
         'label': 'Task Difficulty levels',
         },
        {'name': 'task_types_str',
         'base': forms.fields.CharField,
         'label': 'Task Types',
         },
        ]

    new_params['create_extra_dynaproperties'] = {
        'clean_task_difficulties_str': cleaning.str2set(
            'task_difficulties_str'),
        'clean_task_types_str': cleaning.str2set(
            'task_types_str'),
        }

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    if entity.task_difficulties:
      form.fields['task_difficulties_str'].initial = ', '.join(
          entity.task_difficulties)

    if entity.task_types:
      form.fields['task_types_str'].initial = ', '.join(entity.task_types)

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    fields['task_difficulties'] = fields['task_difficulties_str']
    fields['task_types'] = fields['task_types_str']

    return super(View, self)._editPost(request, entity, fields)


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
home = decorators.view(view.home)
