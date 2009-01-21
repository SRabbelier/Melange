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


from soc.logic import accounts
from soc.logic import dicts
from soc.logic.models import host as host_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views.models import role
from soc.views.models import sponsor as sponsor_view
from soc.views.helper import access

import soc.models.host
import soc.logic.models.host
import soc.views.helper
import soc.views.models.sponsor

# TODO(pawel.solyga): Rename all list methods and functions to something else
# and remove this tolist assignment
tolist = list


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when creating a Host.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """

    #: db.Model subclass for which the form will gather information
    model = soc.models.host.Host

    #: list of model fields which will *not* be gathered by the form
    exclude = ['scope', 'user']

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

class View(role.View):
  """View methods for the Host model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['create'] = [access.checkIsHost]
    rights['edit'] = [access.checkIsHost]
    rights['list'] = [access.checkIsHost]

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = soc.logic.models.host.logic

    new_params['scope_view'] = sponsor_view

    new_params['logic'] = soc.logic.models.host.logic
    new_params['group_view'] = soc.views.models.sponsor.view
    new_params['invite_filter'] = {'group_ln': 'link_id'}

    new_params['name'] = "Program Administrator"
    new_params['module_name'] = "host"

    new_params['edit_form'] = EditForm
    new_params['create_form'] = CreateForm

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def list(self, request, access_type, page_name=None, 
           params=None, filter=None):
    """See base.View.list.

    Passes a filter to base.View.list so that only hosts from a sponsor
    that this user is host for are listed.
    """

    user = user_logic.logic.getForCurrentAccount()

    # Don't bother looking up everything if there's no user
    if user and (not accounts.isDeveloper(user=user)):
      hosts = host_logic.logic.getForFields({'user': user})
      sponsors = tolist((host.scope for host in hosts))

      new_filter = {'scope': sponsors}
      filter = dicts.merge(filter, new_filter)

    return super(View, self).list(request, access_type, page_name=page_name,
                                  params=params, filter=filter)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    user = user_logic.logic.getFromKeyName(fields['link_id'])
    fields['user'] = user

    super(View, self)._editPost(request, entity, fields)

view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export
invite = view.invite

