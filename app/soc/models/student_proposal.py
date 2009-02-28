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

"""This module contains the Student Proposal Model.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.mentor
import soc.models.organization
import soc.models.program


class StudentProposal(soc.models.linkable.Linkable):
  """Model for a student proposal used in the GSoC workflow.
  """

  #: Required field indicating the "title" of the proposal
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Title'))
  title.help_text = ugettext(
      'title of the proposal')

  #: required, text field used for different purposes,
  #: depending on the specific type of the proposal
  abstract = db.StringProperty(required=True, multiline=True)
  abstract.help_text = ugettext(
      'short abstract, summary, or snippet;'
      ' 500 characters or less, plain text displayed publicly')

  #: Required field containing the content of the proposal.
  content = db.TextProperty(required=True)
  content.help_text = ugettext(
      'This contains your actual proposal')

  #: an URL linking to more information about this students proposal
  additional_info = db.URLProperty(required=False)
  additional_info.help_text = ugettext(
      'Link to a resource containing more information about your proposal')

  #: A property containing which mentor has assigned himself to this proposal
  #: Only a proposal with an assigned mentor can be turned into a accepted proposal
  #: A proposal can only have one mentor
  mentor = db.ReferenceProperty(reference_class=soc.models.mentor.Mentor,
                              required=False, collection_name='student_proposals')

  #: the current score of this proposal, used to determine which proposals
  #: should be assigned a project slot.
  score = db.IntegerProperty(required=True, default=0)

  #: the status of this proposal
  #: new : the proposal has not been ranked/scored yet
  #: pending: the proposal is in the process of being ranked/scored
  #: accepted: the proposal has been assigned a project slot
  #: rejected: the proposal has not been assigned a slot or the organization
  #: does not want this proposal.
  #: invalid: the student or developer marked this as an invalid proposal.
  status = db.StringProperty(required=True, default='new',
      choices=['new', 'pending', 'accepted', 'rejected', 'invalid'])

  #: organization to which this proposal is directed
  org = db.ReferenceProperty(reference_class=soc.models.organization.Organization,
                              required=True, collection_name='student_proposals')

  #: program in which this proposal has been created
  program = db.ReferenceProperty(reference_class=soc.models.program.Program,
                              required=True, collection_name='student_proposals')

  #: date when the proposal was created
  created_on = db.DateTimeProperty(required=True, auto_now_add=True)

  #: date when the proposal was last modified, should be set manually on edit
  last_modified_on = db.DateTimeProperty(required=True, auto_now_add=True)
