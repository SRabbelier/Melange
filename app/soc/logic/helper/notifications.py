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


import time
import os

from google.appengine.api import users

from django.template import loader
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext_lazy

from soc.logic import mail_dispatcher
from soc.views.helper import redirects

import soc.views.models as model_view
import soc.logic.models as model_logic


DEF_NEW_NOTIFICATION_MSG = ugettext_lazy(
  "You have received a new Notification")

DEF_INVITATION_MSG_FMT = ugettext_lazy(
    "Invitation to become a %(role)s for %(group)s")

DEF_WELCOME_MSG_FMT = ugettext_lazy("Welcome to Melange %(name)s")

def sendInviteNotification(entity):
  """Sends out an invite notification to the user the request is for.

  Args:
    entity : A request containing the information needed to create the message
  """
  
  # get user logic
  user_logic = model_logic.user.logic

  # get the current user
  current_user_entity = user_logic.getForCurrentAccount()
  
  # get the user the request is for
  properties = {'link_id': entity.link_id }
  request_user_entity = user_logic.getForFields(properties, unique=True)

  # create the invitation_url
  invitation_url = "http://%(host)s%(index)s" % {
      'host' : os.environ['HTTP_HOST'], 
      'index': redirects.inviteAcceptedRedirect(entity, None)}

  # get the group entity
  group_entity = entity.scope
  
  # create the properties for the message
  messageProperties = {
      'to_name': request_user_entity.name,
      'sender_name': current_user_entity.name,
      'role': entity.role,
      'group': group_entity.name,
      'invitation_url': invitation_url,
      }
  
  # render the message
  message = loader.render_to_string('soc/notification/messages/invitation.html', dictionary=messageProperties)
  
  # create the fields for the notification
  fields = { 
      'from_user' : current_user_entity,
      'subject' : DEF_INVITATION_MSG_FMT % {
          'role' : entity.role,
          'group' : group_entity.name 
          },
      'message' : message,
      'scope' : request_user_entity,
      'link_id' :'%i' % (time.time()),
      'scope_path' : request_user_entity.link_id
  }
  
  # create and put a new notification in the datastore
  notification_logic = model_logic.notification.logic
  notification_logic.updateOrCreateFromFields(fields, 
      notification_logic.getKeyFieldsFromDict(fields))
  
def sendNewNotificationMessage(notification_entity):
  """Sends an email to a user about a new notification
  
    Args:
      notification_entity: Notification about which the message should be sent    
  """

  # get user logic
  user_logic = model_logic.user  
  
  # get the current user
  current_user_entity = user_logic.logic.getForCurrentAccount()

  # create the url to show this notification
  notification_url = "http://%(host)s%(index)s" % {
      'host' : os.environ['HTTP_HOST'], 
      'index': redirects.getPublicRedirect(notification_entity,
          model_view.notification.view.getParams())}


  # TODO(Lennard): Change the sender to the no-reply address

  # create the message contents
  messageProperties = {
      'to_name': notification_entity.scope.name,
      'sender_name': current_user_entity.name,
      'to': notification_entity.scope.account.email(),
      'sender': current_user_entity.account.email(),
      'subject': force_unicode(DEF_NEW_NOTIFICATION_MSG),
      'notification' : notification_entity,
      'notification_url' : notification_url
      }
  
  # send out the message using the default new notification template    
  mail_dispatcher.sendMailFromTemplate('soc/mail/new_notification.html', 
                                       messageProperties)
  
def sendWelcomeMessage(user_entity):
  """Sends out a welcome message to a user.

    Args:
      user_entity: User entity which the message should be send to
  """
  
  # get user logic
  user_logic = model_logic.user  
  
  # get the current user
  current_user_entity = user_logic.logic.getForCurrentAccount()

  # TODO(Lennard): change the message sender to some sort of no-reply adress 
  # that is probably a setting in sitesettings. (adress must be a developer). 
  # This is due to a GAE limitation that allows only devs or the current user 
  # to send an email. Currently this results in a user receiving the same 
  # email twice.
  
  # create the message contents
  messageProperties = {
      'to_name': user_entity.name,
      'sender_name': current_user_entity.name,
      'to': user_entity.account.email(),
      'sender': current_user_entity.account.email(),
      'subject': DEF_WELCOME_MSG_FMT % {
          'name': user_entity.name
          }
      } 

  # send out the message using the default welcome template    
  mail_dispatcher.sendMailFromTemplate('soc/mail/welcome.html', 
                                       messageProperties)
