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

"""Functions used to send email messages.

The following are the possible fields of an email message:

  sender: The email address of the sender, the From address. This must be the
    email address of a registered administrator for the application, or the
    address of the current signed-in user. Administrators can be added to
    an application using the Administration Console. The current user's email
    address can be determined with the Users API.
  to: A recipient's email address (a string) or a list of email addresses to
    appear on the To: line in the message header.
  cc: A recipient's email address (a string) or a list of email addresses to
    appear on the Cc: line in the message header.
  bcc: A recipient's email address (a string) or a list of email addresses to
    receive the message, but not appear in the message header ("blind carbon
    copy").
  reply_to: An email address to which a recipient should reply instead of the
    sender address, the Reply-To: field.
  subject: The subject of the message, the Subject: line.
  body: The plaintext body content of the message.
  html: An HTML version of the body content, for recipients that
    prefer HTML email.
  attachments: The file attachments for the message, as a list of two-value
    tuples, one tuple for each attachment. Each tuple contains a filename as
    the first element, and the file contents as the second element.
    An attachment file must be one of the allowed file types, and the
    filename must end with an extension that corresponds with the type.
    For a list of allowed types and filename extensions, see Allowed
    Attachment Types.

Usage:

  context = { 'sender': 'melange-noreply@example.com',
              'to': 'test@example.com',
              'subject': 'You have been invited to become a Host',
              'sender_name': 'Alice',
              'to_name': 'Melange Team',
              'role': 'Host',
              'group': 'Google Summer of Code 2009',
              'invitation_url': 'http://invitation-url'}

  sendMailFromTemplate('soc/mail/invitation.html', context)
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com',
  ]


import logging

from django.template import loader

from google.appengine.api import mail

from soc.logic import dicts
from soc.logic import system
from soc.tasks import mailer


def sendMailFromTemplate(template, context):
  """Sends out an email using a Django template.

  If 'html' is present in context dictionary it is overwritten with
  template HTML output.

  Args:
    template: the template (or search list of templates) to use
    context: The context supplied to the template and email (dictionary)

  Raises:
    Error that corresponds with the first problem it finds iff the message
    is not properly initialized.

    List of all possible errors:
      http://code.google.com/appengine/docs/mail/exceptions.html
  """

  # render the template and put in context with 'html' as key
  context['html'] = loader.render_to_string(template, dictionary=context)

  # filter out the unneeded values in context to keep sendMail happy
  sendMail(dicts.filter(context, mail.EmailMessage.PROPERTIES))


def sendMail(context):
  """Sends out an email using context to supply the needed information.

  Args:
    context : The context supplied to the email message (dictionary)

  Raises:
    Error that corresponds with the first problem it finds iff the message
    is not properly initialized.

    List of all possible errors:
      http://code.google.com/appengine/docs/mail/exceptions.html
  """
  # construct the EmailMessage from the given context
  message = mail.EmailMessage(**context)
  message.check_initialized()

  # don't send out emails in non-local debug mode
  if not system.isLocal() and system.isDebug():
    return

  mailer.spawnMailTask(context)

def getDefaultMailSender():
  """Returns the sender that currently can be used to send emails.

  Returns:
    - A tuple containing (sender_name, sender_address)
    Consisting of:
    - If available the site name and noreply address from the site singleton
    - Or the (public) name and email address of the current logged in User
    - None if there is no address to return
  """
  from soc.logic import accounts
  from soc.logic.models import user as user_logic
  from soc.logic.models import site as site_logic

  # check if there is a noreply email address set
  site_entity = site_logic.logic.getSingleton()

  if site_entity.noreply_email:
    return (site_entity.site_name, site_entity.noreply_email)

  # use the email address of the current logged in user
  account = accounts.getCurrentAccount(normalize=False)

  if not account:
    logging.warning('Non-Authenticated user triggered getDefaultMailSender '
                    'please set a no-reply address in Site settings')
    return None

  # we need to retrieve account separately, as user_logic normalizes it
  # and the GAE admin API is case sensitive
  user_entity = user_logic.logic.getForAccount(account)

  # pylint: disable=E1103
  name = user_entity.name if user_entity else account.nickname()

  return (name, account.email())
