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

"""Organization (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import base
from soc.logic.models import group
from soc.logic.models import org_app as org_app_logic
from soc.logic.models import program as program_logic
from soc.logic.models import request as request_logic

import soc.models.group
import soc.models.organization


class Logic(group.Logic):
  """Logic methods for the Organization model.
  """

  def __init__(self, model=soc.models.organization.Organization,
               base_model=soc.models.group.Group, scope_logic=program_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  # Restore base.Logic key field related methods
  getKeyValuesFromEntity = base.Logic.getKeyValuesFromEntity
  getKeyValuesFromFields = base.Logic.getKeyValuesFromFields
  getKeyFieldNames = base.Logic.getKeyFieldNames


  def _onCreate(self, entity):
    """Invites the group admin and backup admin.
    """

    fields = {
        'link_id': entity.link_id,
        'scope_path': entity.scope_path
        }

    # Find their application
    application = org_app_logic.logic.getFromKeyFields(fields)

    if application:
      # only if there is an application send out the invites
      properties = {
          'scope': entity,
          'scope_path': entity.key().name(),
          'role': 'org_admin',
          'role_verbose': 'Organization Admin',
          'status': 'group_accepted',
          }

      for admin in [application.applicant, application.backup_admin]:
        if not admin:
          continue

        properties['link_id'] = admin.link_id
        key_fields = request_logic.logic.getKeyFieldsFromFields(properties)
        request_logic.logic.updateOrCreateFromFields(properties, key_fields)

      # set the application to completed
      fields = {'status': 'completed'}
      org_app_logic.logic.updateEntityProperties(application, fields)

    super(Logic, self)._onCreate(entity)

logic = Logic()
