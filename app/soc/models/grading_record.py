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

"""GradingRecord represents a cluster (mentor/student) of SurveyRecords
for an evaluation period.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import base
from soc.models.grading_project_survey_record import GradingProjectSurveyRecord
from soc.models.grading_survey_group import GradingSurveyGroup
from soc.models.project_survey_record import ProjectSurveyRecord
from soc.models.student_project import StudentProject


class GradingRecord(base.ModelWithFieldAttributes):
  """Explicitly group SurveyRecords with a common project.

  Because Mentors and Students take different surveys,
  we cannot simply link survey records by a common project and survey.

  Instead, we establish a GradingRecord.

  A GradingRecord links a group of survey records with a common
  project, and links back to its records.

  This entity can be edited by Program Administrators to edit the outcome
  of a the Grading surveys without touching the real survey's answers.

  Also if a ProjectSurvey has been coupled to the GradingSurveyGroup this must
  be on record as well for the GradingRecord to state a pass, even if the
  Mentor has filled in a passing grade.
  """

  #: The GradingSurveyGroup to which this record belongs
  grading_survey_group = db.ReferenceProperty(
      GradingSurveyGroup, required=True, collection_name='grading_records')

  #: Mentor's GradingProjectSurveyRecord for this evaluation. Iff exists.
  mentor_record = db.ReferenceProperty(
      GradingProjectSurveyRecord, required=False,
      collection_name='mentor_grading_records')

  #: Student's ProjectSurveyRecord for this evaluation. Iff exists.
  student_record = db.ReferenceProperty(
      ProjectSurveyRecord, required=False,
      collection_name='student_grading_records')

  #: Project for this evaluation.
  project = db.ReferenceProperty(StudentProject,
                                collection_name='grading_records',
                                required=True)

  #: Grade decision set for this grading record.
  #: pass: Iff the mentor_record states that the student has passed. 
  #:       And if a ProjectSurvey has been set in the GradingSurveyGroup
  #:       then the student_record must be set as well.
  #: fail: If the mentor_record states that the student has failed. The
  #:       student_record does not matter in this case. However if the mentor
  #:       states that the student has passed, a ProjectSurvey has been
  #:       set in the GradingSurveyGroup and the student_record property is not
  #:       set the decision will be fail.
  #: undecided: If no mentor_record has been set.
  grade_decision = db.StringProperty(required=True, default='undecided',
      choices=['pass', 'fail', 'undecided'])

  #: Boolean that states if the grade_decision property has been locked
  #: This is to prevent an automatic update from a GradingSurveyGroup to
  #: overwrite the decision made by for example a Program Administrator.
  locked = db.BooleanProperty(required=True, default=False,
                              verbose_name=ugettext('Grade Decision locked'))

  #: Property containing the date that this GradingRecord was created.
  created = db.DateTimeProperty(auto_now_add=True)

  #: Property containing the last date that this GradingRecord was modified.
  modified = db.DateTimeProperty(auto_now=True)
