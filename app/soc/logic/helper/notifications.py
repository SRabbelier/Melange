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

"""Helper functions for sending out notifications.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import logging
import time

from django.template import loader
from django.utils.encoding import force_unicode
from django.utils.translation import ugettext

# We cannot import soc.logic.models notification nor user here
# due to cyclic imports
from soc.logic import accounts
from soc.logic import dicts
from soc.logic import mail_dispatcher
from soc.logic import system
from soc.views.helper import redirects


DEF_NEW_NOTIFICATION_MSG_SUBJECT_FMT = ugettext(
    'New Notification: %s')

DEF_INVITATION_MSG_FMT = ugettext(
    'Invitation to become a %(role_verbose)s for %(group)s.')

DEF_NEW_REQUEST_MSG_FMT = ugettext(
    'New Request Received from %(requester)s to become a %(role_verbose)s '
    'for %(group)s')

DEF_NEW_ORG_MSG_FMT = ugettext(
    'Your Organization Application for %(group_name)s has been accepted.')

DEF_NEW_REVIEW_SUBJECT_FMT = ugettext(
    'New %s Review on %s')

DEF_REJECTED_REQUEST_SUBJECT_FMT = ugettext(
    'Request to become a %(role_verbose)s for %(group)s has been rejected')

DEF_WITHDRAWN_INVITE_SUBJECT_FMT = ugettext(
    'Invite to become a %(role_verbose)s for %(group)s has been withdrawn')

DEF_WELCOME_MSG_FMT = ugettext('Welcome to %(site_name)s, %(name)s,')

DEF_GROUP_INVITE_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'invitation.html'

DEF_NEW_REQUEST_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'new_request.html'

DEF_NEW_REVIEW_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'new_review.html'

DEF_NEW_ORG_TEMPLATE = 'soc/organization/messages/accepted.html'

DEF_REJECTED_REQUEST_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'rejected_request.html'

DEF_WITHDRAWN_INVITE_NOTIFICATION_TEMPLATE = 'soc/notification/messages/' \
    'withdrawn_invite.html'


def sendInviteNotification(entity):
  """Sends out an invite notification to the user the request is for.

  Args:
    entity : A request containing the information needed to create the message
  """

  from soc.logic.models.user import logic as user_logic
  from soc.views.models.role import ROLE_VIEWS

  invitation_url = 'http://%(host)s%(index)s' % {
      'host' : system.getHostname(),
      'index': redirects.getInviteProcessRedirect(entity, None),
      }

  role_params = ROLE_VIEWS[entity.role].getParams()

  message_properties = {
      'role_verbose' : role_params['name'],
      'group': entity.group.name,
      'invitation_url': invitation_url,
      }

  subject = DEF_INVITATION_MSG_FMT % {
      'role_verbose' : role_params['name'],
      'group' : entity.group.name
      }

  template = DEF_GROUP_INVITE_NOTIFICATION_TEMPLATE

  from_user = user_logic.getForCurrentAccount()

  sendNotification(entity.user, from_user, message_properties, subject, template)


def sendNewRequestNotification(request_entity):
  """Sends out a notification to the persons who can process this Request.

  Args:
    request_entity: an instance of Request model
  """

  from soc.logic.helper import notifications
  from soc.logic.models.role import ROLE_LOGICS
  from soc.views.models.role import ROLE_VIEWS

  # get the users who should get the notification
  to_users = []

  # retrieve the Role Logics which we should query on
  role_logic = ROLE_LOGICS[request_entity.role]
  role_logics_to_notify = role_logic.getRoleLogicsToNotifyUponNewRequest()

  # the scope of the roles is the same as the scope of the Request entity
  fields = {'scope': request_entity.group,
            'status': 'active'}

  for role_logic in role_logics_to_notify:
    roles = role_logic.getForFields(fields)

    for role_entity in roles:
      # TODO: this might lead to double notifications
      to_users.append(role_entity.user)

  # get the user the request is from
  user_entity = request_entity.user

  role_params = ROLE_VIEWS[request_entity.role].getParams()

  request_url = 'http://%(host)s%(redirect)s' % {
      'host': system.getHostname(),
      'redirect': redirects.getProcessRequestRedirect(request_entity, None),
      }

  message_properties = {
      'requester': user_entity.name,
      'role_verbose': role_params['name'],
      'group': request_entity.group.name,
      'request_url': request_url
      }

  subject = DEF_NEW_REQUEST_MSG_FMT % {
      'requester': user_entity.name,
      'role_verbose' : role_params['name'],
      'group' : request_entity.group.name
      }

  template = DEF_NEW_REQUEST_NOTIFICATION_TEMPLATE

  for to_user in to_users:
    notifications.sendNotification(to_user, None, message_properties,
                                   subject, template)


def sendRejectedRequestNotification(entity):
  """Sends a message that the request to get a role has been rejected.

  Args:
    entity : A request containing the information needed to create the message
  """
  from soc.views.models.role import ROLE_VIEWS

  role_params = ROLE_VIEWS[entity.role].getParams()

  message_properties = {
      'role_verbose' : role_params['name'],
      'group': entity.group.name,
      }

  subject = DEF_REJECTED_REQUEST_SUBJECT_FMT % {
      'role_verbose' : role_params['name'],
      'group' : entity.group.name
      }

  template = DEF_REJECTED_REQUEST_NOTIFICATION_TEMPLATE

  # from user set to None to not leak who rejected it.
  sendNotification(entity.user, None, message_properties, subject, template)


def sendWithdrawnInviteNotification(entity):
  """Sends a message that the invite to obtain a role has been withdrawn.

  Args:
    entity : A request containing the information needed to create the message
  """
  from soc.views.models.role import ROLE_VIEWS

  role_params = ROLE_VIEWS[entity.role].getParams()

  message_properties = {
      'role_verbose' : role_params['name'],
      'group': entity.group.name,
      }

  subject = DEF_WITHDRAWN_INVITE_SUBJECT_FMT % {
      'role_verbose' : role_params['name'],
      'group' : entity.group.name
      }

  template = DEF_WITHDRAWN_INVITE_NOTIFICATION_TEMPLATE

  # from user set to None to not leak who rejected it.
  sendNotification(entity.user, None, message_properties, subject, template)

def sendNewOrganizationNotification(entity, module_name):
  """Sends out an invite notification to the applicant of the Organization.

  Args:
    entity : An accepted OrgAppRecord
  """

  program_entity = entity.survey.scope

  url = 'http://%(host)s%(redirect)s' % {
      'redirect': redirects.getApplicantRedirect(entity,
      {'url_name': '%s/org' % module_name,
       'program': program_entity}),
      'host': system.getHostname(),
      }

  message_properties = {
      'org_name': entity.name,
      'program_name': program_entity.name,
      'url': url
      }

  subject = DEF_NEW_ORG_MSG_FMT % {
      'group_name': entity.name,
      }

  template = DEF_NEW_ORG_TEMPLATE

  for to in [entity.main_admin, entity.backup_admin]:
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
  review_notification_url = 'http://%(host)s%(redirect_url)s' % {
      'host' : system.getHostname(),
      'redirect_url': redirect_url}
  
  message_properties = {'review_notification_url': review_notification_url,
      'reviewer_name': review.author_name(),
      'reviewed_name': reviewed_name,
      'review_content': review.content,
      'review_visibility': 'public' if review.is_public else 'private',
      }

  # determine the subject
  review_type = 'public' if review.is_public else 'private'
  subject = DEF_NEW_REVIEW_SUBJECT_FMT % (review_type, reviewed_name)

  template = DEF_NEW_REVIEW_NOTIFICATION_TEMPLATE

  # send the notification from the system
  # TODO(srabbelier): do this in a task instead
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
  notification_url = 'http://%(host)s%(index)s' % {
      'host' : system.getHostname(),
      'index': redirects.getPublicRedirect(notification_entity,
          notification_view.getParams())}

  sender = mail_dispatcher.getDefaultMailSender()
  site_entity = site_logic.getSingleton()
  site_name = site_entity.site_name

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, abort
    logging.error('No default sender')
    return
  else:
    (sender_name, sender) = default_sender

  to = accounts.denormalizeAccount(notification_entity.scope.account).email()
  subject = DEF_NEW_NOTIFICATION_MSG_SUBJECT_FMT % notification_entity.subject

  # create the message contents
  messageProperties = {
      'to_name': notification_entity.scope.name,
      'sender_name': sender_name,
      'to': to,
      'sender': sender,
      'site_name': site_name,
      'subject': force_unicode(subject),
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
    logging.error('No default sender')
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
      'site_location': 'http://%s' % system.getHostname(),
      }

  # send out the message using the default welcome template
  mail_dispatcher.sendMailFromTemplate('soc/mail/welcome.html',
                                       messageProperties)
