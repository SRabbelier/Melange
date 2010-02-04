#!/usr/bin/python2.5
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
                          'completed the application process.')


def completeApplication(record_entity, org_entity, role_name):
  """Sends out invites to the main and backup admin specified in the
  OrgAppRecord entity and completes the application

  Args:
    record_entity: OrgAppRecord entity
    org_entity: The newly created Organization
    role_name: internal name for the role requested
  """

  from soc.logic.models.org_app_record import logic as org_app_record_logic
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
  org_app_record_logic.updateEntityProperties(record_entity, fields)
