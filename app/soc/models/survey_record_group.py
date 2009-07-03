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

"""SurveyRecordGroup represents a cluster (mentor/student) of SurveyRecords
for an evaluation period.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
]


from google.appengine.ext import db

from soc.models.grading_project_survey_record import GradingProjectSurveyRecord
from soc.models.project_survey_record import ProjectSurveyRecord
import soc.models.user


class SurveyRecordGroup(db.Expando):
  """Explicitly group SurveyRecords with a common project.

  Because Mentors and Students take different surveys,
  we cannot simply link survey records by a common project and survey.

  Instead, we establish a SurveyRecordGroup.

  A SurveyRecordGroup links a group of survey records with a common
  project, and links back to its records. 

  This entity also includes the current project_status at its creation.
  This property is used as a filter in lookups and acts as a safeguard
  against unpredictable behavior. 
  """

  # TODO Create SurveyGroup model that contains the two Surveys as to make
  # it possible to setup which surveys should be grouped.

  #: Mentor SurveyRecord for this evaluation.
  mentor_record = db.ReferenceProperty(GradingProjectSurveyRecord,
                                       required=False,
                                       collection_name='mentor_record_groups')

  #: Student SurveyRecord for this evaluation.
  student_record = db.ReferenceProperty(
      ProjectSurveyRecord, required=False,
      collection_name='student_record_groups')

  #: Project for this evaluation.
  project = db.ReferenceProperty(soc.models.student_project.StudentProject,
                                collection_name="survey_record_groups",
                                required=True)

  # Status of project at start of evaluation.
  initial_status = db.StringProperty(required=True)

  #: Status of project at end of evaluation.
  final_status = db.StringProperty(required=False)

  #: Property containing the date that this SurveyRecordGroup was created.
  created = db.DateTimeProperty(auto_now_add=True)

  #: Property containing the last date that this SurveyRecordGroup was modified.
  modified = db.DateTimeProperty(auto_now=True)
