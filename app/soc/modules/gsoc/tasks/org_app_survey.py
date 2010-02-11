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

"""Tasks related to OrgAppSurveys for the GSoC module.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.tasks.org_app_survey import BulkProcessing

from soc.modules.gsoc.logic.models.org_app_survey import logic as org_app_logic 
from soc.modules.gsoc.logic.models.program import logic as program_logic


def getDjangoURLPatterns():
  """Returns the Django URL patterns for the Tasks.
  """

  patterns = [(r'tasks/gsoc/org_app_surveys/bulk_process$',
               'soc.modules.gsoc.tasks.org_app_survey.run_bulk_process')]

  return patterns


bulk_process = BulkProcessing(program_logic, org_app_logic,
                             '/tasks/gsoc/org_app_surveys/bulk_process')
run_bulk_process = bulk_process.run
