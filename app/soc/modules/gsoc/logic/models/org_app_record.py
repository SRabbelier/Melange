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

"""OrgAppRecord (Model) query functions for the GSoC module.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.models import org_app_record
from soc.models.org_app_record import OrgAppRecord as \
    org_app_model
from soc.models.survey_record import SurveyRecord


DEF_ACCEPTED_TEMPLATE = \
    'modules/gsoc/org_app_survey/mail/accepted_gsoc2010.html'
DEF_REJECTED_TEMPLATE = 'soc/org_app_survey/mail/rejected.html'


class Logic(org_app_record.Logic):
  """Logic class for OrgAppRecord.
  """

  def __init__(self, model=org_app_model,
               base_model=SurveyRecord, scope_logic=None, module_name='gsoc',
               mail_templates={'accepted': DEF_ACCEPTED_TEMPLATE,
                               'rejected': DEF_REJECTED_TEMPLATE}):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(
        model=model, base_model=base_model, scope_logic=scope_logic,
        module_name=module_name, mail_templates=mail_templates)


logic = Logic()
