#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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


from google.appengine.ext import db

from django import forms

from gsoc.models import timeline
from soc.logic import dicts
from soc.logic.models import program as program_logic
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

    new_params = {}
    new_params['logic'] = soc.logic.models.timeline.logic
    new_params['edit_template'] = 'soc/timeline/edit.html'
    new_params['name'] = "Timeline"

    patterns = [(r'^%(url_name)s/(?P<access_type>edit)/%(key_fields)s$',
                  'soc.views.models.%(module_name)s.edit', 
                  "Edit %(name_short)s")]

    new_params['django_patterns_defaults'] = patterns

    new_params['edit_dynafields'] = []

    timeline_properties = timeline.Timeline.properties()
    form_fields = {}
    
    # add class 'datetime-pick' for each DateTimeField
    # this is used with datetimepicker js widget
    for key, value in timeline_properties.iteritems():
      if isinstance(value, db.DateTimeProperty):
        form_fields[key] = forms.DateTimeField(required=False,
          widget=forms.TextInput(attrs={'class':'datetime-pick'}))
    
    new_params['create_extra_dynafields'] = form_fields

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    for name, value in program_logic.logic.TIMELINE_LOGIC.iteritems():
      create_form = params_helper.getCreateForm(self._params, value.getModel())
      edit_form = params_helper.getEditForm(self._params, create_form)
      self._params['edit_form_%s' % name] = edit_form

  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """See base.View.edit.
    """

    params = dicts.merge(params, self._params)

    program = program_logic.logic.getFromKeyName(kwargs['scope_path'])
    params['edit_form'] = params["edit_form_%s" % program.workflow]

    return super(View, self).edit(request, access_type, page_name=page_name,
                                  params=params, seed=seed, **kwargs)
  
  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """
    
    # a timeline can only be edited, so set the scope path using entity
    fields['scope_path'] = entity.scope_path


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
