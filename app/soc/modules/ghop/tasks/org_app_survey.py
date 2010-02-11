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

"""Tasks related to OrgAppSurveys for the GHOP module.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.tasks import org_app_survey

from soc.modules.ghop.logic.models.program import logic as program_logic
from soc.modules.ghop.logic.models.org_app_survey import logic as org_app_logic


def getDjangoURLPatterns():
  """Returns the URL patterns for the tasks in this module.
  """

  patterns = [(r'tasks/ghop/org_app_surveys/bulk_process$',
               'soc.modules.ghop.tasks.org_app_survey.bulkProcess')]

  return patterns


bulkProcess = org_app_survey.bulkProcess(program_logic, org_app_logic)
