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

"""Views for Requests.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.logic.models import sponsor as sponsor_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models import role as role_view

import soc.models.request
import soc.logic.models.request
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when Developer creates a Request.
  """

  class Meta:
    model = soc.models.request.Request

    #: list of model fields which will *not* be gathered by the form 
    exclude = ['inheritance_line', 'requester', 'to', 'role', 'declined']

  role = forms.CharField(widget=helper.widgets.ReadOnlyInput())

  user = forms.CharField(
      label=soc.models.request.Request.requester.verbose_name,
      help_text=soc.models.request.Request.requester.help_text,
      widget=helper.widgets.ReadOnlyInput())  

  group = forms.CharField(
      label=soc.models.request.Request.to.verbose_name,
      help_text=soc.models.request.Request.to.help_text,
      widget=helper.widgets.ReadOnlyInput())

  def clean_user(self):
    self.cleaned_data['requester'] =  user_logic.logic.getForFields(
        {'link_id': self.cleaned_data['user']}, unique=True)
    return self.cleaned_data['user']

  def clean_group(self):
    self.cleaned_data['to'] = sponsor_logic.logic.getFromFields(
        link_id=self.cleaned_data['group'])
    return self.cleaned_data['group']


class EditForm(CreateForm):
  """Django form displayed when Developer edits a Request.
  """

  pass


class View(base.View):
  """View methods for the Docs model.
  """

  def __init__(self, original_params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
    """

    self._logic = soc.logic.models.request.logic

    params = {}

    params['name'] = "Request"
    params['name_short'] = "Request"
    params['name_plural'] = "Requests"
    params['url_name'] = "request"
    params['module_name'] = "request"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    params['sidebar_defaults'] = [('/%s/list', 'List %(name_plural)s')]

    params['delete_redirect'] = '/' + params['url_name'] + '/list'
    params['create_redirect'] = '/' + params['url_name']

    params['save_message'] = [ugettext_lazy('Request saved.')]

    params = dicts.merge(original_params, params)

    base.View.__init__(self, params=params)
    
    
  def listSelf(self, request, page_name=None, params=None, **kwargs):
    """Displays the unhandled requests for this user.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used
    """

    try:
      self.checkAccess('list', request)
    except out_of_band.Error, error:
      return error.response(request)

    params = dicts.merge(params, self._params)

    # get the current user
    properties = {'account': users.get_current_user()}
    user_entity = user_logic.logic.getForFields(properties, unique=True)

    # TODO(ljvderijk): Construct the Unhandled Request list

    # only select the requests for this user that haven't been handled yet
    filter = {'requester': user_entity,
              'accepted' : True,
              'declined' : False}

    params['list_action'] = (self.inviteAcceptedRedirect, None)
    params['list_description'] = "An overview of your unhandled requests"

    uh = helper.lists.getListContent(request, params, self._logic, filter)

    # TODO(ljvderijk): Construct the other Request lists here

    contents = [uh]
    return self._list(request, params, contents, page_name)

  def inviteAcceptedRedirect(self, entity, _):
    """Returns the redirect for accepting a request
    """

    return '/%s/create/%s/%s' % (
        entity.role, entity.to.link_id, entity.requester.link_id)

  def _editSeed(self, request, seed):
    """See base.View._editGet().
    """

    # fill in the email field with the data from the entity
    seed['user'] = seed['user_ln']
    seed['group'] = seed['group_ln']

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the email field with the data from the entity
    form.fields['user'].initial = entity.requester.link_id
    form.fields['group'].initial = entity.to.link_id 

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # fill in the account field with the user created from email
    fields['user_ln'] = fields['requester'].link_id
    fields['group_ln'] = fields['to'].link_id
    
    # make declined explicitly false when not specified
    if 'declined' not in fields:
      fields['declined'] = False


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
list_self = view.listSelf
public = view.public
