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

"""This module contains the Student Project Model.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.mentor
import soc.models.program
import soc.models.student


class StudentProject(soc.models.linkable.Linkable):
  """Model for a student project used in the GSoC workflow.
  """

  #: Required field indicating the "title" of the project
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Title'))
  title.help_text = ugettext('Title of the project')

  #: required, text field describing the project
  abstract = db.TextProperty(required=True)
  abstract.help_text = ugettext(
      'Short abstract, summary, or snippet;'
      ' 500 characters or less, plain text displayed publicly')

  #: optional, URL which can give more information about this project
  additional_info = db.URLProperty(required=False)
  additional_info.help_text = ugettext(
      'Link to a resource containing more information about this project.')

  #: Optional field storing a feed URL; displayed publicly.
  feed_url = db.LinkProperty(
      verbose_name=ugettext('Project Feed URL'))
  feed_url.help_text = ugettext(
      'The URL should be a valid ATOM or RSS feed. '
      'Feed entries are shown on the home page.')

  #: A property containing which mentor has been assigned to this project.
  #: A project must have a mentor at all times
  mentor = db.ReferenceProperty(reference_class=soc.models.mentor.Mentor,
                                required=True,
                                collection_name='student_projects')

  #: the status of this project
  #: accepted: This project has been accepted into the program
  #: mid_term_passed: This project has passed the midterm evaluation
  #: mid_term_failed: This project has failed the midterm evaluation
  #: final_failed: This project has failed the final evaluation
  #: passed: This project has completed the program successfully
  status = db.StringProperty(required=True, default='accepted',
      choices=['accepted', 'mid_term_passed', 'mid_term_failed', 
              'final_failed', 'passed'])

  #: student which this project is from
  student = db.ReferenceProperty(
      reference_class=soc.models.student.Student,
      required=True, collection_name='student_projects')

  #: program in which this project has been created
  program = db.ReferenceProperty(reference_class=soc.models.program.Program,
                                 required=True, 
                                 collection_name='student_projects')
