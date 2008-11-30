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

"""Helper functions for sending out notifications
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]

from google.appengine.api import users

from django.utils.translation import ugettext_lazy

from soc.logic import mail_dispatcher
from soc.logic.models import user as user_logic

from soc.views.helper import redirects

import os


DEF_INVITATION_FMT = ugettext_lazy(
    "Invitation to become a %(role)s for %(group)s")


def sendInviteNotification(entity):
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
