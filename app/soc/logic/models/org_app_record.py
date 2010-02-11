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

"""OrgAppRecord (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import survey_record
from soc.models.org_app_record import OrgAppRecord as \
    org_app_model
from soc.models.survey_record import SurveyRecord


class Logic(survey_record.Logic):
  """Logic class for OrgAppRecord.
  """

  def __init__(self, model=org_app_model,
               base_model=SurveyRecord, scope_logic=None,
               module_name=None, mail_templates=None):
    """Defines the name, key_name and model for this entity.
    """
    self.module_name = module_name
    self.mail_templates = mail_templates

    super(Logic, self).__init__(
        model=model, base_model=base_model, scope_logic=scope_logic)

  def processRecord(self, record):
    """Processes an OrgAppRecord that is in the pre-accepted/pre-rejected
    state.

    The status of such an OrgAppRecord is updated to either accepted or
    rejected based on the current status.

    Args:
      record: OrgAppRecord entity
    """

    current_status = record.status

    if current_status == 'pre-accepted':
      new_status = 'accepted'
    elif current_status == 'pre-rejected':
      new_status = 'rejected'
    else:
      # no work to be done
      return record

    fields = {'status': new_status}
    return self.updateEntityProperties(record, fields)

  def _updateField(self, entity, entity_properties, name):
    """Hook for when a field in the OrgAppRecord is updated.

    Responds to change in the status field to accepted/rejected by sending out
    a notification and an email to the users set in the record.
    """

    from soc.logic.helper import org_app_survey as org_app_helper

    value = entity_properties[name]

    if name == 'status' and value in ['accepted', 'rejected'] and \
        entity.status != value:
      # Sent email and notification that this application has been 
      # accepted/rejected.
      org_app_helper.sentApplicationProcessedNotification(
          entity, value, self.module_name, self.mail_templates)

    return super(Logic, self)._updateField(entity, entity_properties, name)

logic = Logic()
