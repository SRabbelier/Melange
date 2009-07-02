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

"""This module contains the ProjectSurvey model.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from soc.models.survey import Survey


class ProjectSurvey(Survey):
  """Survey for Students that have a StudentProject.
  """

  def __init__(self, *args, **kwargs):
    super(ProjectSurvey, self).__init__(*args, **kwargs)
    self.prefix = 'program'
    self.taking_access = 'student'
