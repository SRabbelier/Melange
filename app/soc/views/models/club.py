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

"""Views for Clubs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from google.appengine.api import users

from django import forms

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.logic.models import group_app as group_app_logic
from soc.logic.models import club as club_logic
from soc.views.helper import access
from soc.views.helper import widgets
from soc.views.models import base

import soc.logic.models.club


class View(base.View):
  """View methods for the Club model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['create'] = [access.checkIsApplied]

    new_params = {}
    new_params['logic'] = soc.logic.models.club.logic
    new_params['rights'] = rights

    new_params['name'] = "Club"

    new_params['extra_dynaexclude'] = ['founder', 'home', 'member_template']
    new_params['edit_extra_dynafields'] = {
        'founded_by': forms.CharField(widget=widgets.ReadOnlyInput(),
                                   required=False),
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """See base.View.create()
    """

    if 'link_id' not in kwargs:
      return super(View, self).create(request, access_type, page_name,
                                      params=params, **kwargs)

    # Find their application
    key_fields = group_app_logic.logic.getKeyFieldsFromDict(kwargs)
    application = group_app_logic.logic.getFromFields(**key_fields)

    # Extract the application fields
    field_names = application.properties().keys()
    fields = dict( [(i, getattr(application, i)) for i in field_names] )

    empty = dict( [(i, None) for i in self._logic.getKeyFieldNames()] )

    return super(View, self).edit(request, access_type, page_name,
                                  params=params, seed=fields, **empty)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the founded_by with data from the entity
    form.fields['founded_by'].initial = entity.founder.name
    super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      # only if we are creating a new entity we should fill in founder
      account = users.get_current_user()
      user = user_logic.logic.getForFields({'account': account}, unique=True)
      fields['founder'] = user

    super(View, self)._editPost(request, entity, fields)

view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public