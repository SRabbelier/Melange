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

"""GradingProjectSurveyRecord extends ProjectSurveyRecord to store the grade.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models.project_survey_record import ProjectSurveyRecord
from soc.models.grading_project_survey import GradingProjectSurvey


class GradingProjectSurveyRecord(ProjectSurveyRecord):
  """Grading record for evaluation surveys.

  Represents the grading part of a evaluation survey group (usually a pair)
  where the grading (e.g. Mentor's) survey is linked to a non-grading (e.g
  Student's) one by a project.
  """

  #: Required grade given to the project that this survey is about.
  #: Symbolizes pass(=True) or fail(=False)
  grade = db.BooleanProperty(required=True)
