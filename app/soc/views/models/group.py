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

"""Views for Groups.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users

from django import forms

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views.models import base

import soc.views.helper
import soc.views.helper.widgets


class View(base.View):
  """View methods for the Group model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}

    new_params['extra_dynaexclude'] = ['founder', 'home']
    new_params['edit_extra_dynafields'] = {
        'founded_by': forms.CharField(widget=helper.widgets.ReadOnlyInput(),
                                   required=False),
        }

    # TODO(tlarsen): Add support for Django style template lookup
    new_params['public_template'] = 'soc/group/public.html'

    new_params['list_row'] = 'soc/group/list/row.html'
    new_params['list_heading'] = 'soc/group/list/heading.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the founded_by with data from the entity
    form.fields['founded_by'].initial = entity.founder.name

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      # only if we are creating a new entity we should fill in founder
      account = users.get_current_user()
      user = user_logic.logic.getForFields({'account': account}, unique=True)
      fields['founder'] = user
