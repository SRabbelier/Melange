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

"""Host (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverer@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]

from google.appengine.api import users

from django.utils.translation import ugettext_lazy

from soc.logic import mail_dispatcher
from soc.logic.models import base
from soc.logic.models import user as user_logic

import os

import soc.models.request


class Logic(base.Logic):
  """Logic methods for the Request model.
  """

  DEF_INVITATION_FMT = ugettext_lazy(
      "Invitation to become a %(role)s for %(group)s")

  def __init__(self, model=soc.models.request.Request,
               base_model=None):
    """Defines the name, key_name and model for this entity.
    """

    base.Logic.__init__(self, model, base_model=base_model)

  def getKeyValues(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.role, entity.scope.link_id, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['role'], fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['role', 'scope_path', 'link_id']
  
  def _onCreate(self, entity):
    """Sends out a message notifying users about the new invite/request.
    """
    
    if entity.group_accepted:  
      # this is an invite
      self.sendInviteMessage(entity)
    elif entity.user_accepted:
      # this is a request
      # TODO(Lennard) Create a new request message
      pass

    
  def sendInviteMessage(self, entity):
    """Sends out an invite notification to the user the request is for.

    Args:
      entity : A request containing the information needed to create the message
    """

    # get the current user
    properties = {'account': users.get_current_user()}
    current_user_entity = user_logic.logic.getForFields(properties, unique=True)

    # get the user the request is for
    properties = {'link_id': entity.link_id }
    request_user_entity = user_logic.logic.getForFields(properties, unique=True)

    # create the invitation_url
    invitation_url = "%(host)s%(index)s" % {
                          'host' : os.environ['HTTP_HOST'], 
                          'index': self.inviteAcceptedRedirect(entity, None)
                          }

    # get the group entity
    group_entity = entity.scope

    messageProperties = {
        'to_name': request_user_entity.name,
        'sender_name': current_user_entity.name,
        'role': entity.role,
        'group': group_entity.name,
        'invitation_url': invitation_url,
        'to': request_user_entity.account.email(),
        'sender': current_user_entity.account.email(),
        'subject': self.DEF_INVITATION_FMT % {
            'role': entity.role,
            'group': group_entity.name
            },
        }

    # send out the message using the default invitation template    
    mail_dispatcher.sendMailFromTemplate('soc/mail/invitation.html', 
                                         messageProperties)

  def inviteAcceptedRedirect(self, entity, _):
    """Returns the redirect for accepting an invite
    """

    return '/%s/create/%s/%s' % (
        entity.role, entity.scope_path, entity.link_id)

logic = Logic()
