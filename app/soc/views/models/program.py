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

"""Views for Programs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms

from soc.logic import dicts
from soc.logic.models import program as program_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import presence
from soc.views.models import document as document_view
from soc.views.models import sponsor as sponsor_view
from soc.views.sitemap import sidebar

import soc.logic.models.program


class View(presence.View):
  """View methods for the Program model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['any_access'] = [access.allow]
    rights['show'] = [access.allow]

    new_params = {}
    new_params['logic'] = soc.logic.models.program.logic
    new_params['rights'] = rights

    new_params['scope_view'] = sponsor_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Program"

    new_params['edit_template'] = 'soc/program/edit.html'

    new_params['extra_dynaexclude'] = ['timeline']

    new_params['create_extra_dynafields'] = {
        'description': forms.fields.CharField(widget=helper.widgets.TinyMCE(
            attrs={'rows':10, 'cols':40})),

        'scope_path': forms.CharField(widget=forms.HiddenInput, required=True),

        'workflow' : forms.ChoiceField(choices=[('gsoc','Project-based'),
            ('ghop','Task-based')], required=True),
        }

    new_params['edit_extra_dynafields'] = {
        'workflow': forms.CharField(widget=widgets.ReadOnlyInput(),
                                   required=True),
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    if not entity:
      # there is no existing entity so create a new timeline
      fields['timeline'] = self._createTimelineForType(fields)
    else:
      # use the timeline from the entity
      fields['timeline'] = entity.timeline

    super(View, self)._editPost(request, entity, fields)

  def _createTimelineForType(self, fields):
    """Creates and stores a timeline model for the given type of program.
    """

    workflow = fields['workflow']

    timeline_logic = program_logic.logic.TIMELINE_LOGIC[workflow]

    key_fields = self._logic.getKeyFieldsFromDict(fields)
    key_name = self._logic.getKeyNameForFields(key_fields)

    properties = {'scope_path': key_name}

    timeline = timeline_logic.updateOrCreateFromFields(properties, properties)
    return timeline

  def getExtraMenus(self, request, params=None):
    """Returns the extra menu's for this view.

    A menu item is generated for each program that is currently
    running. The public page for each program is added as menu item,
    as well as all public documents for that program.

    Args:
      request: unused
      params: a dict with params for this View.
    """

    params = dicts.merge(params, self._params)
    logic = params['logic']

    entities = logic.getForLimitAndOffset(1000)

    doc_params = document_view.view.getParams()
    menus = []

    for entity in entities:
      menu = {}
      menu['heading'] = entity.short_name
      items = document_view.view.getMenusForScope(entity, params)
      menu['items'] = sidebar.getSidebarMenu(request, items, params=doc_params)
      menus.append(menu)

    return menus

view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export
home = view.home
pick = view.pick
