#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""Notifications for the GCI module.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.encoding import force_unicode
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import dicts
from soc.logic import mail_dispatcher
from soc.logic.helper import notifications

DEF_BULK_CREATE_COMPLETE_SUBJECT_MSG = ugettext(
    'Bulk creation of tasks completed')

DEF_BULK_CREATE_COMPLETE_TEMPLATE = \
    'modules/gci/notification/messages/bulk_create_complete.html'

DEF_TASK_REQUEST_SUBJECT_MSG = ugettext(
    'A new task has been requested from your organization')

DEF_TASK_REQUEST_TEMPLATE = \
    'modules/gci/notification/messages/task_request.html'

def sendTaskUpdateMail(subscriber, subject, message_properties=None):
  """Sends an email to a user about an update to a Task.

    Args:
      subscriber: The user entity to whom the message must be sent
      subject: Subject of the mail
      message_properties: The mail message properties
      template: Optional django template that is used to build the message body
  """

  from soc.logic.models.site import logic as site_logic

  site_entity = site_logic.getSingleton()
  site_name = site_entity.site_name

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, abort
    return
  else:
    (sender_name, sender) = default_sender

  to = accounts.denormalizeAccount(subscriber.account).email()

  # create the message contents
  new_message_properties = {
      'to_name': subscriber.name,
      'sender_name': sender_name,
      'to': to,
      'sender': sender,
      'site_name': site_name,
      'subject': force_unicode(subject),
      }

  messageProperties = dicts.merge(message_properties, new_message_properties)

  template = 'modules/gci/task/update_notification.html'

  # send out the message using the default new notification template
  mail_dispatcher.sendMailFromTemplate(template, messageProperties)

def sendBulkCreationCompleted(bulk_data):
  """Sends out a notification that the bulk creation of tasks has been
  completed.

  Any error messages that have been generated are also added to the notification.

  Args:
    bulk_data: GCIBulkCreateData entity containing information needed to
               populate the notification.
  """
  message_properties = {
      'bulk_data' : bulk_data
      }

  subject = DEF_BULK_CREATE_COMPLETE_SUBJECT_MSG
  template = DEF_BULK_CREATE_COMPLETE_TEMPLATE

  notifications.sendNotification(
      bulk_data.created_by.user, None, message_properties, subject, template)

def sendRequestTaskNotification(org_admins, message):
  """Sends notifications to org admins that there is a student who requested
  more tasks from them.

  Args:
    org_admins: a list of org admins who the notification should be sent to
    message: a short message that will be included to the notification
  """

  from soc.logic.models.site import logic as site_logic

  # get the default mail sender
  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no valid sender found, abort
    return
  else:
    (sender_name, sender) = default_sender

  # get site name
  site_entity = site_logic.getSingleton()
  site_name = site_entity.site_name
  subject = DEF_TASK_REQUEST_SUBJECT_MSG
  template = DEF_TASK_REQUEST_TEMPLATE

  properties = {
      'message': message,
      'sender': sender,
      'sender_name': sender_name,
      'site_name': site_name,
      'subject': subject,
      }

  for org_admin in org_admins:
    to = org_admin.user
    properties['to'] = to
    properties['to_name'] = to.name

    notifications.sendNotification(to, None, properties, subject, template)
