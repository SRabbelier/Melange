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

"""Appengine Tasks related to GHOPTask.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


from django.utils.encoding import force_unicode

from soc.logic import accounts
from soc.logic import dicts
from soc.logic import mail_dispatcher


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

  template = 'modules/ghop/task/update_notification'

  # send out the message using the default new notification template
  mail_dispatcher.sendMailFromTemplate(template, messageProperties)
