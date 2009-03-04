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

"""Views for Timeline.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import forms

from soc.logic import dicts
from soc.logic.models import program as program_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import params as params_helper
from soc.views.models import base

import soc.logic.models.timeline


class View(base.View):
  """View methods for the Timeline model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['edit'] = ['checkCanEditTimeline']

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = soc.logic.models.timeline.logic
    new_params['edit_template'] = 'soc/timeline/edit.html'
    new_params['name'] = "Timeline"

    patterns = [(r'^%(url_name)s/(?P<access_type>edit)/%(key_fields)s$',
                  'soc.views.models.%(module_name)s.edit', 
                  "Edit %(name_short)s")]

    new_params['create_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput)
        }
    new_params['django_patterns_defaults'] = patterns

    new_params['edit_dynaproperties'] = []

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    for name, logic_value in program_logic.logic.TIMELINE_LOGIC.iteritems():
      create_form = params_helper.getCreateForm(self._params, 
          logic_value.getModel())
      edit_form = dynaform.extendDynaForm(
        dynaform = create_form,
        dynainclude = self._params['edit_dynainclude'],
        dynaexclude = self._params['edit_dynaexclude'],
        )

      self._params['edit_form_%s' % name] = edit_form

  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """See base.View.edit.
    """
    params = dicts.merge(params, self._params)
    
    # TODO(pawel.solyga): If program doesn't exist for timeline display
    # customized error message without pointing to 'Create Timeline'

    key_fields = program_logic.logic.getKeyFieldsFromFields(kwargs)

    program = program_logic.logic.getFromKeyFields(key_fields)
    if program:
      params['edit_form'] = params["edit_form_%s" % program.workflow]

    return super(View, self).edit(request, access_type, page_name=page_name,
                                  params=params, seed=seed, **kwargs)
  
  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    
    # a timeline can only be edited, so set the scope path using entity
    fields['scope_path'] = entity.scope_path


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)

