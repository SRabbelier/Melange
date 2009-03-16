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
import time

from django.template import loader
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext

# We cannot import soc.logic.models notification nor user here
# due to cyclic imports
from soc.logic import accounts
from soc.logic import dicts
from soc.logic import mail_dispatcher
from soc.views.helper import redirects

import soc.views.models as model_view
import soc.logic.models as model_logic


DEF_NEW_NOTIFICATION_MSG = ugettext(
  "You have received a new Notification.")

DEF_INVITATION_MSG_FMT = ugettext(
    "Invitation to become a %(role_verbose)s for %(group)s.")

DEF_NEW_GROUP_MSG_FMT = ugettext(
    "Your %(application_type)s for %(group_name)s has been accepted.")

DEF_WELCOME_MSG_FMT = ugettext("Welcome to %(site_name)s, %(name)s,")

DEF_GROUP_INVITE_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'invitation.html'

DEF_NEW_GROUP_TEMPLATE = 'soc/group/messages/accepted.html'


def sendInviteNotification(entity):
  """Sends out an invite notification to the user the request is for.

  Args:
    entity : A request containing the information needed to create the message
  """

  # get the user the request is for
  properties = {'link_id': entity.link_id }
  to_user = model_logic.user.logic.getForFields(properties, unique=True)

  invitation_url = "http://%(host)s%(index)s" % {
      'host' : os.environ['HTTP_HOST'],
      'index': redirects.getInviteProcessRedirect(entity, None),
      }

  message_properties = {
      'role_verbose' : entity.role_verbose,
      'group': entity.scope.name,
      'invitation_url': invitation_url,
      }

  subject = DEF_INVITATION_MSG_FMT % {
      'role_verbose' : entity.role_verbose,
      'group' : entity.scope.name
      }

  template = DEF_GROUP_INVITE_NOTIFICATION_TEMPLATE

  from_user = model_logic.user.logic.getForCurrentAccount()

  sendNotification(to_user, from_user, message_properties, subject, template)


def sendNewGroupNotification(entity, params):
  """Sends out an invite notification to the applicant of the group.

  Args:
    entity : An accepted group application
  """

  to_user = entity.applicant

  url = "http://%(host)s%(redirect)s" % {
      'redirect': redirects.getApplicantRedirect(entity,
      {'url_name': params['group_url_name']}),
      'host': os.environ['HTTP_HOST'],
      }

  message_properties = {
      'application_type': params['name'],
      'group_type': params['group_name'],
      'group_name': entity.name,
      'url': url,
      }

  subject = DEF_NEW_GROUP_MSG_FMT % {
      'application_type': params['name'],
      'group_name': entity.name,
      }

  template = DEF_NEW_GROUP_TEMPLATE

  sendNotification(to_user, None, message_properties, subject, template)


def sendNotification(to_user, from_user, message_properties, subject, template):
  """Sends out a notification to the specified user.

  Args:
    to_user : user to which the notification will be send
    from_user: user from who sends the notifications (None iff sent by site)
    message_properties : message properties
    subject : subject of notification email
    template : template used for generating notification
  """

  if from_user:
    sender_name = from_user.name
  else:
    site_entity = model_logic.site.logic.getSingleton()
    sender_name = 'The %s Team' %(site_entity.site_name)

  new_message_properties = {
      'sender_name': sender_name,
      'to_name': to_user.name,
      }

  message_properties = dicts.merge(message_properties, new_message_properties)

  message = loader.render_to_string(template, dictionary=message_properties)

  fields = {
      'from_user': from_user,
      'subject': subject,
      'message': message,
      'scope': to_user,
      'link_id': 't%i' %(int(time.time()*100)),
      'scope_path': to_user.link_id
  }

  key_name = model_logic.notification.logic.getKeyNameFromFields(fields)

  # create and put a new notification in the datastore
  model_logic.notification.logic.updateOrCreateFromKeyName(fields, key_name)


def sendNewNotificationMessage(notification_entity):
  """Sends an email to a user about a new notification.

    Args:
      notification_entity: Notification about which the message should be sent
  """

  # create the url to show this notification
  notification_url = "http://%(host)s%(index)s" % {
      'host' : os.environ['HTTP_HOST'],
      'index': redirects.getPublicRedirect(notification_entity,
          model_view.notification.view.getParams())}

  sender = mail_dispatcher.getDefaultMailSender()
  site_entity = model_logic.site.logic.getSingleton()
  site_name = site_entity.site_name

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, abort
    return
  else:
    (sender_name, sender) = default_sender

  to = accounts.denormalizeAccount(notification_entity.scope.account).email()

  # create the message contents
  messageProperties = {
      'to_name': notification_entity.scope.name,
      'sender_name': sender_name,
      'to': to,
      'sender': sender,
      'site_name': site_name,
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

  # get site name
  site_entity = model_logic.site.logic.getSingleton()
  site_name = site_entity.site_name

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, should not happen but abort anyway
    return
  else:
    sender_name, sender = default_sender

  to = accounts.denormalizeAccount(user_entity.account).email()

  # create the message contents
  messageProperties = {
      'to_name': user_entity.name,
      'sender_name': sender_name,
      'site_name': site_name,
      'to': to,
      'sender': sender,
      'subject': DEF_WELCOME_MSG_FMT % {
          'site_name': site_name,
          'name': user_entity.name
          }
      }

  # send out the message using the default welcome template
  mail_dispatcher.sendMailFromTemplate('soc/mail/welcome.html',
                                       messageProperties)
