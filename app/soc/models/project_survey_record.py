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

"""ProjectSurveyRecord allows linking two result sets by StudentProject.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from soc.models.survey_record import SurveyRecord
from soc.models.project_survey import ProjectSurvey
import soc.models.student_project


#TODO decide if this should inherit from BaseSurveyRecord
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
