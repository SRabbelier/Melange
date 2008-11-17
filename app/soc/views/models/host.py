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

"""Views for Host profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.views import helper
from soc.views.models import base
from soc.views.models import role

import soc.models.host
import soc.logic.models.host
import soc.logic.models.sponsor
import soc.views.helper


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when creating a Host.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """

    #: db.Model subclass for which the form will gather information
    model = soc.models.host.Host

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line']

  def clean_empty(self, field):
    data = self.cleaned_data.get(field)
    if not data or data == u'':
      return None

    return data

  def clean_home_page(self):
    return self.clean_empty('home_page')

  def clean_blog(self):
    return self.clean_empty('blog')

  def clean_photo_url(self):
    return self.clean_empty('photo_url')


class EditForm(CreateForm):
  """Django form displayed when editing a Host.
  """

  pass

class View(role.RoleView):
  """View methods for the Host model.
  """

  def __init__(self, original_params=None, original_rights=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
      original_rights: a dict with right definitions for this View
    """

    self._logic = soc.logic.models.host.logic

    params = {}
    rights = {}

    params['logic'] = soc.logic.models.host.logic
    params['group_logic'] = soc.logic.models.sponsor.logic
    params['invite_filter'] = {'group_ln': 'link_name'}

    params['name'] = "Host"
    params['name_short'] = "Host"
    params['name_plural'] = "Hosts"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen) Add support for Django style template lookup
    params['edit_template'] = 'soc/models/edit.html'
    params['public_template'] = 'soc/host/public.html'
    params['list_template'] = 'soc/models/list.html'
    params['invite_template'] = 'soc/models/invite.html'

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/host/list/host_row.html',
      'list_heading': 'soc/host/list/host_heading.html',
    }

    params['delete_redirect'] = '/host/list'
    params['invite_redirect'] = '/request/list'

    params['save_message'] = [ugettext_lazy('Profile saved.')]

    params['edit_params'] = {
        self.DEF_SUBMIT_MSG_PARAM_NAME: self.DEF_SUBMIT_MSG_PROFILE_SAVED,
        }

    rights['list'] = [helper.access.checkIsDeveloper]
    rights['delete'] = [helper.access.checkIsDeveloper]

    params = dicts.merge(original_params, params)
    rights = dicts.merge(original_rights, rights)

    role.RoleView.__init__(self, original_rights=rights, original_params=params)


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
invite = view.invite
