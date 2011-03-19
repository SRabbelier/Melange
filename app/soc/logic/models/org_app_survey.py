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

"""OrgAppSurvey (Model) query functions.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django.utils.translation import ugettext

from soc.logic.models import program as program_logic
from soc.logic.models import survey
from soc.logic.models.org_app_record import logic as \
    org_app_record_logic
from soc.models.org_app_survey import OrgAppSurvey
from soc.models.survey import Survey
from soc.logic.exceptions import NotFound


class Logic(survey.Logic):
  """Logic class for OrgAppSurvey.
  """

  def __init__(self, model=OrgAppSurvey,
               base_model=Survey, scope_logic=program_logic,
               record_logic=org_app_record_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                       scope_logic=scope_logic,
                                       record_logic=record_logic)

  def getForProgram(self, program):
    """Returns the OrgAppSurvey belonging to the given program.

    Args:
      program: Program entity to get the OrgAppSurvey for

    Returns:
      OrgAppSurvey belonging to the given Program, None if not exists.
    """
    fields = {'scope': program}

    return self.getForFields(fields, unique=True)

  def getForProgramOr404(self, program):
    """Returns the OrgAppSurvery belonging to the given program.

    Raises:
      NotFound if no entity is found
    """

    entity = self.getForProgram(program)

    if entity:
      return entity

    msg = ugettext(
        'There is no "%(name)s" for the program %(program_name)s.') % {
        'name': self._name, 'program_name': program.name}

    raise NotFound(msg)


logic = Logic()
