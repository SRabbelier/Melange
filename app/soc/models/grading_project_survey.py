#!/usr/bin/python2.5
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

"""This module contains the GradingProjectSurvey model.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from soc.models.project_survey import ProjectSurvey


class GradingProjectSurvey(ProjectSurvey):
  """Survey for Mentors for each of their StudentProjects.
  """

  def __init__(self, *args, **kwargs):
    super(GradingProjectSurvey, self).__init__(*args, **kwargs)
    self.taking_access = 'mentor'

  def getRecords(self):
    """Returns all GradingProjectSurveyRecords belonging to this survey.
    """
    return self.grading_survey_records
