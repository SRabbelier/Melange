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

"""GSoCTimeline (Model) query functions.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from soc.logic.models import timeline
from soc.logic.helper import timeline as timeline_helper

import soc.models.timeline

import soc.modules.gsoc.models.timeline


class Logic(timeline.Logic):
  """Logic methods for the GSoCTimeline model.
  """

  def __init__(self, model=soc.modules.gsoc.models.timeline.GSoCTimeline,
               base_model=soc.models.timeline.Timeline):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model)

  def getCurrentTimeline(self, program_entity):
    """Return where we are currently on the timeline.
    """
    from soc.modules.gsoc.logic.models.org_app_survey import logic as oas_logic

    oas_entity = oas_logic.getForFields({'scope': program_entity},
                                        unique=True)
    timeline_entity = program_entity.timeline

    if timeline_helper.isActivePeriod(oas_entity, 'survey'):
      return 'org_signup_period'
    elif timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
      return 'student_signup_period'
    elif timeline_helper.isActivePeriod(timeline_entity, 'program'):
      return 'program_period'

    return ''

logic = Logic()
