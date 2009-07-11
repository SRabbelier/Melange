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
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models.survey import Survey
import soc.models.user


class BaseSurveyRecord(db.Expando):
  """Record produced each time Survey is taken.

  Like SurveyContent, this model includes dynamic properties
  corresponding to the fields of the survey.
  """

  #: The survey for which this entity is a record.
  survey = db.ReferenceProperty(
      reference_class=Survey, collection_name="survey_records")

  #: Date when this record was created.
  created = db.DateTimeProperty(auto_now_add=True)

  #: Date when this record was last modified.
  modified = db.DateTimeProperty(auto_now=True)

  def getValues(self):
    """Method to get dynamic property values for a survey record.

    Right now it gets all dynamic values, but it could also be confined to
    the SurveyContent entity linked to the survey entity.
    """
    survey_order = self.survey.survey_content.getSurveyOrder()
    values = []
    for position, property in survey_order.items():
        values.insert(position, getattr(self, property, None))
    return values


class SurveyRecord(BaseSurveyRecord):
  """Record produced by taking a Survey.
  """

  #: Reference to the User entity which took this survey.
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name="surveys_taken",
                              verbose_name=ugettext('Taken by'))
