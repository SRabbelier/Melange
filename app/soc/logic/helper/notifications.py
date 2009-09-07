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


DEF_NEW_NOTIFICATION_MSG = ugettext(
    "You have received a new Notification.")

DEF_INVITATION_MSG_FMT = ugettext(
    "Invitation to become a %(role_verbose)s for %(group)s.")

DEF_NEW_REQUEST_MSG_FMT = ugettext(
    "New Request Received from %(requester)s to become a %(role_verbose)s "
    "for %(group)s")

DEF_NEW_GROUP_MSG_FMT = ugettext(
    "Your %(application_type)s for %(group_name)s has been accepted.")

DEF_NEW_REVIEW_SUBJECT_FMT = ugettext(
    "New %s Review on %s")

DEF_WELCOME_MSG_FMT = ugettext("Welcome to %(site_name)s, %(name)s,")

DEF_GROUP_INVITE_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'invitation.html'

DEF_NEW_REQUEST_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'new_request.html'

DEF_NEW_REVIEW_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'new_review.html'

DEF_NEW_GROUP_TEMPLATE = 'soc/group/messages/accepted.html'


def sendInviteNotification(entity):
  """Sends out an invite notification to the user the request is for.

  Args:
    entity : A request containing the information needed to create the message
  """

  from soc.logic.models.user import logic as user_logic

  # get the user the request is for
  properties = {'link_id': entity.link_id }
  to_user = user_logic.getForFields(properties, unique=True)

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

  from_user = user_logic.getForCurrentAccount()

  sendNotification(to_user, from_user, message_properties, subject, template)


def sendNewRequestNotification(request_entity):
  """Sends out a notification to the persons who can process this Request.

  Args:
    request_entity: an instance of Request model
  """

  from soc.logic.helper import notifications
  from soc.logic.models.role import ROLE_LOGICS
  from soc.logic.models.user import logic as user_logic

  # get the users who should get the notification
  to_users = []

  # retrieve the Role Logics which we should query on
  role_logic = ROLE_LOGICS[request_entity.role]
  role_logics_to_notify = role_logic.getRoleLogicsToNotifyUponNewRequest()

  # the scope of the roles is the same as the scope of the Request entity
  fields = {'scope': request_entity.scope,
            'status': 'active'}

  for role_logic in role_logics_to_notify:
    roles = role_logic.getForFields(fields)

    for role_entity in roles:
      # TODO: this might lead to double notifications
      to_users.append(role_entity.user)

  # get the user the request is from
  properties = {'link_id': request_entity.link_id }
  user_entity = user_logic.getForFields(properties, unique=True)

  message_properties = {
      'requester_name': user_entity.name,
      'entity': request_entity,
      'request_url': redirects.getProcessRequestRedirect(request_entity, None)}

  subject = DEF_NEW_REQUEST_MSG_FMT % {
      'requester': user_entity.name,
      'role_verbose' : request_entity.role_verbose,
      'group' : request_entity.scope.name
      }

  template = DEF_NEW_REQUEST_NOTIFICATION_TEMPLATE

  for to_user in to_users:
    notifications.sendNotification(to_user, None, message_properties,
                                   subject, template)


def sendNewGroupNotification(entity, params):
  """Sends out an invite notification to the applicant of the group.

  Args:
    entity : An accepted group application
  """

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

  for to in [entity.applicant, entity.backup_admin]:
    if not to:
      continue

    sendNotification(to, None, message_properties, subject, template)


def sendNewReviewNotification(to_user, review, reviewed_name, redirect_url):
  """Sends out a notification to alert the user of a new Review.

  Args:
    to_user: The user who should receive a notification
    review: The review which triggers this notification
    reviewed_name: Name of the entity reviewed
    redirect_url: URL to which the follower should be sent for more information
  """

  message_properties = {'redirect_url': redirect_url,
      'reviewer_name': review.author_name(),
      'reviewed_name': reviewed_name,
      }

  # determine the subject
  review_type = 'public' if review.is_public else 'private'
  subject =  DEF_NEW_REVIEW_SUBJECT_FMT % (review_type, reviewed_name)

  template = DEF_NEW_REVIEW_NOTIFICATION_TEMPLATE

  # send the notification from the system
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

  from soc.logic.models.notification import logic as notification_logic
  from soc.logic.models.site import logic as site_logic

  if from_user:
    sender_name = from_user.name
  else:
    site_entity = site_logic.getSingleton()
    sender_name = 'The %s Team' % (site_entity.site_name)

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
      'link_id': 't%i' % (int(time.time()*100)),
      'scope_path': to_user.link_id
  }

  key_name = notification_logic.getKeyNameFromFields(fields)

  # create and put a new notification in the datastore
  notification_logic.updateOrCreateFromKeyName(fields, key_name)


def sendNewNotificationMessage(notification_entity):
  """Sends an email to a user about a new notification.

    Args:
      notification_entity: Notification about which the message should be sent
  """

  from soc.logic.models.site import logic as site_logic
  from soc.views.models.notification import view as notification_view

  # create the url to show this notification
  notification_url = "http://%(host)s%(index)s" % {
      'host' : os.environ['HTTP_HOST'],
      'index': redirects.getPublicRedirect(notification_entity,
          notification_view.getParams())}

  sender = mail_dispatcher.getDefaultMailSender()
  site_entity = site_logic.getSingleton()
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

  from soc.logic.models.site import logic as site_logic

  # get site name
  site_entity = site_logic.getSingleton()
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
      'to': to,
      'sender': sender,
      'subject': DEF_WELCOME_MSG_FMT % {
          'site_name': site_name,
          'name': user_entity.name
          },
      'site_name': site_name,
      'site_location': 'http://%s' % os.environ['HTTP_HOST'],
      }

  # send out the message using the default welcome template
  mail_dispatcher.sendMailFromTemplate('soc/mail/welcome.html',
                                       messageProperties)
