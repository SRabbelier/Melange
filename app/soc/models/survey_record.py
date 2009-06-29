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

"""SurveyRecord represents a single Survey result.

ProjectSurveyRecord allows linking two result sets by StudentProject.

GradingProjectSurveyRecord stores the grade in an evaluation survey.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models.survey import Survey
from soc.models.grading_project_survey import GradingProjectSurvey
from soc.models.project_survey import ProjectSurvey
import soc.models.student_project
import soc.models.user


class BaseSurveyRecord(db.Expando):
  """Record produced each time Survey is taken.

  Like SurveyContent, this model includes dynamic properties
  corresponding to the fields of the survey.
  """

  #: Reference to the User entity which took this survey.
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name="surveys_taken",
                              verbose_name=ugettext('Created by'))

  #: Date when this record was created.
  created = db.DateTimeProperty(auto_now_add=True)

  #: Date when this record was last modified.
  modified = db.DateTimeProperty(auto_now=True)

  def getValues(self):
    """Method to get dynamic property values for a survey record.

    Right now it gets all dynamic values, but it could also be confined to
    the SurveyContent entity linked to the survey entity.
    """
    survey_order = self.getSurvey().survey_content.getSurveyOrder()
    values = []
    for position, property in survey_order.items():
        values.insert(position, getattr(self, property, None))
    return values


# TODO(ajaksu) think of a better way to handle the survey reference
class SurveyRecord(BaseSurveyRecord):

  #: The survey for which this entity is a record.
  survey = db.ReferenceProperty(Survey, collection_name="survey_records")

  def getSurvey(self):
    """Returns the Survey belonging to this record.
    """
    return self.survey

class ProjectSurveyRecord(SurveyRecord):
  """Record linked to a Project, enabling to store which Projects had their
  Survey done.
  """

  #: The survey for which this entity is a record.
  project_survey = db.ReferenceProperty(ProjectSurvey,
                                collection_name="project_survey_records")

  #: Reference to the Project that this record belongs to.
  project = db.ReferenceProperty(soc.models.student_project.StudentProject,
                                 collection_name="survey_records")

  def getSurvey(self):
    """Returns the ProjectSurvey that belongs to this record.
    """
    return self.project_survey


class GradingProjectSurveyRecord(ProjectSurveyRecord):
  """Grading record for evaluation surveys.

  Represents the grading part of a evaluation survey group (usually a pair)
  where the grading (e.g. Mentor's) survey is linked to a non-grading (e.g
  Student's) one by a project.
  """

  #: The survey for which this entity is a record.
  grading_survey = db.ReferenceProperty(GradingProjectSurvey,
                                collection_name="grading_survey_records")

  #: Required grade given to the project that this survey is about.
  grade = db.BooleanProperty(required=True)

  def getSurvey(self):
    """Returns the GradingProjectSurvey that belongs to this record.
    """
    return self.grading_survey
