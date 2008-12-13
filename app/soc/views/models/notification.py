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

"""This module contains the view code for Notifications
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


import time

from google.appengine.api import users

from django import forms
from django import http
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.models import notification as notification_model
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.models import base
from soc.logic.models import notification as notification_logic
from soc.logic.models import user as user_logic


class CreateForm(helper.forms.BaseForm):
  """Form for creating a Notification.
  """

  # to user field
  to_user = forms.fields.CharField(label='To User')

  def __init__(self, *args, **kwargs):
    """ Calls super and then redefines the order in which the fields appear.

    for parameters see BaseForm.__init__()
    """
    super(CreateForm, self).__init__(*args, **kwargs)

    # set form fields order
    self.fields.keyOrder = ['to_user', 'subject', 'message']

  class Meta:
    model = notification_model.Notification

    # exclude the necessary fields from the form
    exclude = ['link_id', 'scope', 'scope_path', 'from_user', 'unread']

  def clean_to_user(self):
    """Check if the to_user field has been filled in correctly.
    """
    link_id = self.cleaned_data.get('to_user').lower()

    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")

    to_user = user_logic.logic.getForFields({'link_id' : link_id}, unique=True)

    if not to_user:
      # user does not exist
      raise forms.ValidationError("This user does not exist")

    return link_id


class View(base.View):
  """View methods for the Notification model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['unspecified'] = [access.deny]
    rights['edit'] = [access.deny]
    rights['show'] = [access.checkIsMyNotification]
    rights['delete'] = [access.checkIsDeveloper]
    rights['list'] = [access.checkIsUser]
    # create is developer only for the time being to test functionality
    rights['create'] = [access.checkIsDeveloper]

    new_params = {}
    new_params['logic'] = notification_logic.logic
    new_params['rights'] = rights

    new_params['name'] = "Notification"
    new_params['name_short'] = "Notification"
    new_params['name_plural'] = "Notifications"
    new_params['url_name'] = "notification"
    new_params['module_name'] = "notification"

    new_params['create_form'] = CreateForm

    new_params['edit_redirect'] = '/%(url_name)s/list'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def list(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """Lists all notifications that the current logged in user has stored.

    for parameters see base.list()
    """

    params = dicts.merge(params, self._params)

    # get the current user
    user_entity = user_logic.logic.getForCurrentAccount()

    # only select the notifications for this user so construct a filter
    filter = {'scope': user_entity}

    # create the list parameters
    list_params = params.copy()

    # define the list redirect action to show the notification
    list_params['list_action'] = (redirects.getPublicRedirect, params)
    list_params['list_description'] = ugettext_lazy(
        "An overview of your received Notifications.")

    # TODO(Lennard) when list sorting is implemented sort on descending date

    # use the generic list method with the filter. The access check in this
    # method will trigger an errorResponse when user_entity is None
    return super(View, self).list(request, access_type,
        page_name, list_params, filter)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # get the current user
    current_user = user_logic.logic.getForCurrentAccount()

    to_user = user_logic.logic.getForFields(
        {'link_id' : fields['to_user']}, unique=True)

    fields['link_id'] = '%i' %(time.time())
    fields['scope'] = to_user
    fields['from_user'] = current_user
    fields['scope_path'] = fields['to_user']

  def _editSeed(self, request, seed):
    """Checks if scope_path is seeded and puts it into to_user.

    for parameters see base._editSeed()
    """

    # if scope_path is present
    if 'scope_path' in seed.keys():
      # fill the to_user field with the scope path
      seed['to_user'] = seed['scope_path']

  def _public(self, request, entity, context):
    """Marks the Notification as read if that hasn't happened yet.

    for parameters see base._public()
    """

    # if the user viewing is the user for which this notification is meant
    # and the notification has not been read yet
    if entity.unread:
      # get the current user
      user = user_logic.logic.getForCurrentAccount()
      
      # if the message is meant for the user that is reading it
      if entity.scope.key() == user.key():
        # mark the entity as read
        self._logic.updateModelProperties(entity, {'unread' : False} )

    context['entity_type_url'] = self._params['url_name']
    context['entity_suffix'] = self._logic.getKeySuffix(entity)


view = View()
create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
