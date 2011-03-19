#!/usr/bin/env python2.5
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

"""This module contains the view code for Notifications.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


import time

from google.appengine.ext import db

from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models.notification import logic as notification_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.models import notification as notification_model
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import lists as list_helper
from soc.views.helper import redirects
from soc.views.models import base


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
    """Inner Meta class that defines some behavior for the form.
    """
    model = notification_model.Notification
    fields = None

    # exclude the necessary fields from the form
    exclude = ['link_id', 'scope', 'scope_path', 'from_user', 'unread']

  clean_to_user = cleaning.clean_existing_user('to_user')


class View(base.View):
  """View methods for the Notification model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['edit'] = ['deny']
    rights['show'] = [('checkIsMyEntity', [notification_logic, 'scope_path'])]
    rights['delete'] = [('checkIsMyEntity', [notification_logic, 'scope_path'])]
    rights['list'] = ['checkIsUser']
    # create is developer only for the time being to test functionality
    rights['create'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = notification_logic
    new_params['rights'] = rights

    new_params['name'] = "Notification"

    new_params['no_create_with_key_fields'] = True
    new_params['create_form'] = CreateForm

    new_params['edit_redirect'] = '/%(url_name)s/list'

    new_params['public_configuration'] = {"multiselect": True}
    new_params['public_field_prefetch'] = ['from_user']
    new_params['public_field_extra'] = lambda entity: {
        "from": entity.from_user.name if entity.from_user else
            site_logic.getSingleton().site_name,
        "unread": "Not Read" if entity.unread else "Read",
    }
    new_params['public_field_props'] = {
        "unread": {
            "stype": "select",
            "editoptions": {"value": ":All;^Read$:Read;^Not Read$:Not Read"}
        }
    }
    new_params['public_conf_extra'] = {
        "multiselect": True,
    }
    new_params['public_field_keys'] = ["unread", "from", "subject",
                                       "created_on",]
    new_params['public_field_names'] = ["Unread", "From", "Subject",
                                        "Received on"]
    new_params['public_button_global'] = [
        {
          'bounds': [1,'all'],
          'id': 'mark_read',
          'caption': 'Mark as Read',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
        },
        {
          'bounds': [1,'all'],
          'id': 'mark_unread',
          'caption': 'Mark as Unread',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
        },
        {
          'bounds': [1,'all'],
          'id': 'delete',
          'caption': 'Delete Notification',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
        }]

    params = dicts.merge(params, new_params)

    params['public_row_extra'] = lambda entity: {
        "link": redirects.getPublicRedirect(entity, params)
    }

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def list(self, request, access_type, page_name=None, params=None,
           filter=None, order=None, **kwargs):
    """Lists all notifications that the current logged in user has stored.

    for parameters see base.list()
    """

    if request.method == 'POST':
      return self.listPost(request, params, **kwargs)
    else: # request.method == 'GET'
      if not order:
        order = ['-created_on']
      user_entity = user_logic.getCurrentUser()
      filter = {'scope': user_entity}
      return super(View, self).list(request, access_type, page_name=page_name,
                                    params=params, filter=filter, order=order,
                                    **kwargs)

  def listPost(self, request, params, **kwargs):
    """Handles the POST request for the list of notifications.
    """

    import logging

    from django.utils import simplejson

    post_dict = request.POST

    data = simplejson.loads(post_dict.get('data', '[]'))
    button_id = post_dict.get('button_id', '')

    user_entity = user_logic.getCurrentUser()

    notifications = []
    for selection in data:
      notification = notification_logic.getFromKeyName(selection['key'])

      if not notification:
        logging.error('No notification found for %(key)s' %selection)
        continue

      if notification.scope.key() == user_entity.key():
        notifications.append(notification)

    if button_id == 'delete':
      for notification in notifications:
        notification_logic.delete(notification)
    elif button_id == 'mark_read' or button_id == 'mark_unread':
      if button_id == 'mark_read':
        # mark all the Notifications selected as read
        fields = {'unread': False}
      elif button_id == 'mark_unread':
        # mark all the Notifications selected as unread
        fields = {'unread': True}

      for notification in notifications:
        notification_logic.updateEntityProperties(notification, fields,
                                                  store=False)
      db.put(notifications)

    # return a 200 response to signal that all is okay
    return http.HttpResponseRedirect('')

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # get the current user
    current_user = user_logic.getCurrentUser()

    fields['link_id'] = 't%i' % (int(time.time()*100))
    fields['scope'] = fields['to_user']
    fields['from_user'] = current_user
    fields['scope_path'] = fields['to_user'].link_id

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
      user = user_logic.getCurrentUser()

      # if the message is meant for the user that is reading it
      # pylint: disable=E1103
      if entity.scope.key() == user.key():
        # mark the entity as read
        self._logic.updateEntityProperties(entity, {'unread' : False} )

    context['entity_type_url'] = self._params['url_name']
    context['entity_suffix'] = entity.key().id_or_name() if entity else None
    context['page_name'] = 'Notification - %s' % (entity.subject)

    return True


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
