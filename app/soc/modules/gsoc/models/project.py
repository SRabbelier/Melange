#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""This module contains the GSoCProject Model.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.base
import soc.models.linkable
import soc.models.program
import soc.models.role
import soc.models.organization


class GSoCProject(soc.models.base.ModelWithFieldAttributes):
  """Model for a GSoC project used in the GSoC workflow.
  """

  #: Required field indicating the "title" of the project
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Title'))
  title.help_text = ugettext('Title of the project')

  #: Required, text field describing the project
  abstract = db.TextProperty(required=True)
  abstract.help_text = ugettext(
      'Short abstract, summary, or snippet;'
      ' 500 characters or less, plain text displayed publicly')

  #: Optional, text field containing all kinds of information about this project
  public_info = db.TextProperty(required=False, default ='')
  public_info.help_text = ugettext(
      'Additional information about this project to be shown publicly')

  #: Optional, URL which can give more information about this project
  additional_info = db.URLProperty(required=False)
  additional_info.help_text = ugettext(
      'Link to a resource containing more information about this project.')

  #: Optional field storing a feed URL; displayed publicly
  feed_url = db.LinkProperty(
      verbose_name=ugettext('Project Feed URL'))
  feed_url.help_text = ugettext(
      'The URL should be a valid ATOM or RSS feed. '
      'Feed entries are shown on the public page.')

  #: A property containing which mentor has been assigned to this project.
  #: A project must have a mentor at all times.
  mentor = db.ReferenceProperty(reference_class=soc.models.role.Profile,
                                required=True,
                                collection_name='projects')

  #: A property containing a list of additional Mentors for this project
  additional_mentors = db.ListProperty(item_type=db.Key, default=[])

  #: The status of this project
  #: accepted: This project has been accepted into the program
  #: failed: This project has failed an evaluation.
  #: completed: This project has completed the program successfully. This
  #:            should be set automatically when a program has been deemed
  #:            finished.
  #: withdrawn: This project has been withdrawn from the program by a Program
  #:            Administrator or higher.
  #: invalid: This project has been marked as invalid because it was deleted
  status = db.StringProperty(
      required=True, default='accepted',
      choices=['accepted', 'failed', 'completed', 'withdrawn', 'invalid'])

  #: List of all processed GradingRecords which state a pass for this project.
  #: This property can be used to determine how many evaluations someone has
  #: passed. And is also used to ensure that a GradingRecord has been
  #: processed.
  passed_evaluations = db.ListProperty(item_type=db.Key, default=[])

  #: List of all processed GradingRecords which state a fail for this project.
  #: This is a ListProperty to ensure that the system keeps functioning when
  #: manual changes in GradingRecords occur.
  failed_evaluations = db.ListProperty(item_type=db.Key, default=[])

  #: Student which this project is from
  org = db.ReferenceProperty(
      reference_class=soc.models.organization.Organization,
      required=True, collection_name='student_projects')

  #: Program in which this project has been created
  program = db.ReferenceProperty(reference_class=soc.models.program.Program,
                                 required=True, 
                                 collection_name='projects')
