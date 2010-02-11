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

"""Views for Timeline.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import forms

from soc.logic import dicts
from soc.logic.models import program as program_logic
from soc.views.helper import access
from soc.views.helper import responses
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
    rights['edit'] = [('checkCanEditTimeline', [program_logic.logic])]

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = soc.logic.models.timeline.logic
    new_params['edit_template'] = 'soc/timeline/edit.html'
    new_params['name'] = "Timeline"

    patterns = [(r'^%(url_name)s/(?P<access_type>edit)/%(key_fields)s$',
                  '%(module_package)s.%(module_name)s.edit',
                  "Edit %(name_short)s")]

    new_params['create_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput)
        }
    new_params['django_patterns_defaults'] = patterns

    new_params['edit_dynaproperties'] = []

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # a timeline can only be edited, so set the scope path using entity
    fields['scope_path'] = entity.scope_path


view = View()

edit = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
