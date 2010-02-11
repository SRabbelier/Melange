#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Helper functions for the OrgAppSurveys.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.translation import ugettext


DEF_INVITE_MSG = ugettext('This invite was automatically generated because you'
                          ' completed the application process.')


def sentApplicationProcessedNotification(entity, status, module_name,
                                         mail_templates):
  """Sends out email about the processed Organization Application. If the 
  application is accepted a Notification is also generated.

  Args:
    entity: OrgAppRecord entity
    status: the new status of the OrgAppRecord entity
    module_name: The name of the module the Organization entity is in
    mail_templates: dictionary containing accepted and rejected keys mapping
        to the location of the mail template to be used iff status is equal to
        that key
  """

  from soc.logic import accounts
  from soc.logic import mail_dispatcher
  from soc.logic.helper import notifications

  default_sender = mail_dispatcher.getDefaultMailSender()

  if not default_sender:
    # no default sender abort
    return
  else:
    (sender_name, sender) = default_sender

  # construct the contents of the email
  admin_entity = entity.main_admin
  backup_entity = entity.backup_admin

  context = {
      'sender': sender,
      'sender_name': sender_name,
      'program_name': entity.survey.scope.name,
      'org_app_name': entity.name
      }

  if status == 'accepted':
    # use the accepted template and subject
    template = mail_templates['accepted']
    context['subject'] = 'Congratulations!'
  elif status == 'rejected':
    # use the rejected template and subject
    template = mail_templates['rejected']
    context['subject'] = 'Thank you for your application'

  for to in [admin_entity, backup_entity]:
    if not to:
      continue

    email = accounts.denormalizeAccount(to.account).email()
    context['to'] = email
    context['to_name'] = to.name

    # send out the constructed email
    mail_dispatcher.sendMailFromTemplate(template, context)

  # send out the notifications about what to do next to the accepted ones
  if status == 'accepted':
    notifications.sendNewOrganizationNotification(entity, module_name)

def completeApplication(record_entity, record_logic, org_entity, role_name):
  """Sends out invites to the main and backup admin specified in the
  OrgAppRecord entity and completes the application.

  Args:
    record_entity: OrgAppRecord entity
    record_logic: OrgAppRecord Logic instance
    org_entity: The newly created Organization
    role_name: internal name for the role requested
  """

  from soc.logic.models.request import logic as request_logic

  properties = {
      'role': role_name,
      'group': org_entity,
      'message': DEF_INVITE_MSG,
      'status': 'group_accepted',
      }

  for admin in [record_entity.main_admin, record_entity.backup_admin]:
    if not admin:
      continue

    properties['user'] = admin
    request_logic.updateOrCreateFromFields(properties)

  fields = {'status': 'completed'}
  record_logic.updateEntityProperties(record_entity, fields)
