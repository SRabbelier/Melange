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

"""Helper functions for sending out notifications.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import os

from google.appengine.api import users

from django.utils.translation import ugettext_lazy

import soc.logic.models as model_logic

from soc.logic import mail_dispatcher
from soc.views.helper import redirects


DEF_INVITATION_FMT = ugettext_lazy(
    "Invitation to become a %(role)s for %(group)s")

DEF_WELCOME_FMT = ugettext_lazy("Welcome to Melange %(name)s")

def sendInviteNotification(entity):
  """Sends out an invite notification to the user the request is for.

  Args:
    entity : A request containing the information needed to create the message
  """
  
  # get user logic
  user_logic = model_logic.user

  # get the current user
  properties = {'account': users.get_current_user()}
  current_user_entity = user_logic.logic.getForFields(properties, unique=True)
  
  # get the user the request is for
  properties = {'link_id': entity.link_id }
  request_user_entity = user_logic.logic.getForFields(properties, unique=True)

  # create the invitation_url
  invitation_url = "%(host)s%(index)s" % {
      'host' : os.environ['HTTP_HOST'], 
      'index': redirects.inviteAcceptedRedirect(entity, None)}

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
      'subject': DEF_INVITATION_FMT % {
          'role': entity.role,
          'group': group_entity.name
          },
      }

  # send out the message using the default invitation template    
  mail_dispatcher.sendMailFromTemplate('soc/mail/invitation.html', 
                                       messageProperties)
  
def sendWelcomeMessage(user_entity):
  """Sends out a welcome message to a user.

    Args:
      user_entity: User entity which the message should be send to
  """
  
  # get user logic
  user_logic = model_logic.user  
  
  # get the current user
  properties = {'account': users.get_current_user()}
  current_user_entity = user_logic.logic.getForFields(properties, unique=True)

  # create the message contents
  # TODO(Lennard) change the message sender to some sort of no-reply adress that is
  # probably a setting in sitesettings. (adress must be a developer). This is due
  # to a GAE limitation that allows only devs or the current user to send an email.
  # Currently this results in a user receiving the same email twice.
  messageProperties = {
      'to_name': user_entity.name,
      'sender_name': current_user_entity.name,
      'to': user_entity.account.email(),
      'sender': current_user_entity.account.email(),
      'subject': DEF_WELCOME_FMT % {
          'name': user_entity.name
          }
      } 

  # send out the message using the default welcome template    
  mail_dispatcher.sendMailFromTemplate('soc/mail/welcome.html', 
                                       messageProperties)
