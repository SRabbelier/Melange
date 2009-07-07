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

"""GradingSurveyGroup has the ability to link a GradingProjectSurvey to a
ProjectSurvey for evaluation purposes.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import linkable
from soc.models.grading_project_survey import GradingProjectSurvey
from soc.models.project_survey import ProjectSurvey


class GradingSurveyGroup(linkable.Linkable):
  """The GradingSurveyGroups links a ProjectSurvey with a GradingProjectSurvey.

  The purpose of this model is to be able to link two different types of
  Surveys together so that a decision can be made about whether or not a
  Student has passed the evaluation. This model will link the Surveys together
  a GradingRecord will link the SurveyRecords.

  Since this model is only used in GSoC style programs the scope will be set to
  a Program entity. The link_id can be auto-generated.

  A GradingSurvey group can also work with only a GradingProjectSurvey defined.

  The GradingSurveyGroup can have several GradingRecords attached to it. These
  will contain matching SurveyRecords for the surveys set in this group, of
  course only if they are filled in.
  """

  #: GradingProjectSurvey which belongs to this group.
  grading_survey = db.ReferenceProperty(
      GradingProjectSurvey, required=True,
      collection_name='grading_survey_groups')

  #: non-required ProjectSurvey that belongs to this group.
  student_survey = db.ReferenceProperty(
      ProjectSurvey, required=False,
      collection_name='project_survey_groups')

  #: DateTime when the last GradingRecord update was started for this group.
  last_update_started = db.DateTimeProperty(
      verbose_name=ugettext('Last Record update started'))

  #: DateTime when the last GradingRecord update was completed for this group.
  last_update_complete = db.DateTimeProperty(
      verbose_name=ugettext('Last Record update completed'))
