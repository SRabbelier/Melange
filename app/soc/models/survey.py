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

"""This module contains the Survey models.

Survey describes meta-information and permissions.
SurveyContent contains the fields (questions) and their metadata.
"""

__authors__ = [
  '"Daniel Diniz" <ajaksu@gmail.com>',
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.work


COMMENT_PREFIX = 'comment_for_'


class SurveyContent(db.Expando):
  """Fields (questions) and schema representation of a Survey.

  Each survey content entity consists of properties where names and default
  values are set by the survey creator as survey fields.

    schema: A dictionary (as text) storing, for each field:
      - type
      - index
      - order (for choice questions)
      - render (for choice questions)
      - question (free form text question, used as label)
  """

  #:Field storing the content of the survey in the form of a dictionary.
  schema = db.TextProperty()

  #: Fields storing the created on and last modified on dates.
  created = db.DateTimeProperty(auto_now_add=True)
  modified = db.DateTimeProperty(auto_now=True)

  def getSurveyOrder(self):
    """Make survey questions always appear in the same (creation) order.
    """
    survey_order = {}
    schema = eval(self.schema)
    for property in self.dynamic_properties():
      # map out the order of the survey fields
      index = schema[property]["index"]
      if index not in survey_order:
        survey_order[index] = property
      else:
        # Handle duplicated indexes
        survey_order[max(survey_order) + 1] = property
    return survey_order

  def orderedProperties(self):
    """Helper for View.get_fields(), keep field order.
    """
    properties = []
    survey_order = self.getSurveyOrder().items()
    for position,key in survey_order:
      properties.insert(position, key)
    return properties


class Survey(soc.models.work.Work):
  """Model of a Survey.

  This model describes meta-information and permissions.
  The actual questions of the survey are contained
  in the SurveyContent entity.
  """

  URL_NAME = 'survey'
  # euphemisms like "student" and "mentor" should be used if possible
  SURVEY_ACCESS = ['admin', 'restricted', 'member', 'user']

  # these are GSoC specific, so eventually we can subclass this
  SURVEY_TAKING_ACCESS = ['student',
                          'mentor',
                          'org_admin',
                          'user']
  
  GRADE_OPTIONS = {'midterm':['mid_term_passed', 'mid_term_failed'],
                   'final':['final_passed', 'final_failed'],
                   'N/A':[] }

  prefix = db.StringProperty(default='program', required=True,
      choices=['site', 'club', 'sponsor', 'program', 'org', 'user'],
      verbose_name=ugettext('Prefix'))
  prefix.help_text = ugettext(
      'Indicates the prefix of the survey,'
      ' determines which access scheme is used.')

  #: Field storing the required access to read this survey.
  read_access = db.StringProperty(default='restricted', required=True,
      choices=SURVEY_ACCESS,
      verbose_name=ugettext('Survey Read Access'))
  read_access.help_text = ugettext(
      'Indicates who can read the results of this survey.')

  #: Field storing the required access to write to this survey.
  write_access = db.StringProperty(default='admin', required=True,
      choices=SURVEY_ACCESS,
      verbose_name=ugettext('Survey Write Access'))
  write_access.help_text = ugettext(
      'Indicates who can edit this survey.')

  #: Field storing the required access to write to this survey.
  taking_access = db.StringProperty(default='student', required=True,
      choices=SURVEY_TAKING_ACCESS,
      verbose_name=ugettext('Survey Taking Access'))
  taking_access.help_text = ugettext(
      'Indicates who can take this survey. '
      'Student/Mentor options are for Midterms and Finals.')

  #: Field storing whether a link to the survey should be featured in
  #: the sidebar menu (and possibly elsewhere); FAQs, Terms of Service,
  #: and the like are examples of "featured" survey.
  is_featured = db.BooleanProperty(
      verbose_name=ugettext('Is Featured'))
  is_featured.help_text = ugettext(
      'Field used to indicate if a Survey should be featured, for example,'
      ' in the sidebar menu.')

  #: Date at which the survey becomes available for taking.
  survey_start = db.DateTimeProperty(required=False)
  survey_start.help_text = ugettext(
      'Indicates a date before which this survey'
      ' cannot be taken or displayed.')

  #: Deadline for taking survey.
  survey_end = db.DateTimeProperty(required=False)
  survey_end.help_text = ugettext(
      'Indicates a date after which this survey'
      ' cannot be taken.')

  #: Referenceproperty that specifies the content of this survey.
  survey_content = db.ReferenceProperty(SurveyContent,
                                     collection_name="survey_parent")
