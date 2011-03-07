#!/usr/bin/env python2.5
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
  '"Daniel Hans <daniel.m.hans@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.organization
import soc.models.program
import soc.models.role


# define the [min_score, max_score] and the name for the RankList
DEF_SCORE = [-1000, 1000]
DEF_RANKER_NAME = 'student_app_ranker'


class StudentProposal(soc.models.linkable.Linkable):
  """Model for a student proposal used in the GSoC workflow.
  """

  #: Required field indicating the "title" of the proposal
  title = db.StringProperty(required=True,
      verbose_name=ugettext('Project Title'))
  title.help_text = ugettext('Title of the proposal')

  #: required, text field used for different purposes,
  #: depending on the specific type of the proposal
  abstract = db.TextProperty(required=True,
      verbose_name=ugettext('Short Description'))
  abstract.help_text = ugettext(
      'Short abstract, summary, or snippet;'
      ' 500 characters or less, plain text displayed publicly')

  #: Required field containing the content of the proposal.
  content = db.TextProperty(required=True,
      verbose_name=ugettext('Content'))
  content.help_text = ugettext('This contains your actual proposal')

  #: an URL linking to more information about this students proposal
  additional_info = db.URLProperty(required=False)
  additional_info.help_text = ugettext(
      'Link to a resource containing more information about your proposal')

  #: indicates whether the proposal's content may be publicly seen or not
  is_publicly_visible = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('Make public'))
  is_publicly_visible.help_text = ugettext(
      'If you check here, the content of your proposal will be visible '
      'for others. Please note that they still will not be able to see '
      'any public comments and reviews of the proposal.')

  #: A property containing which mentor has assigned himself to this proposal.
  #: Only a proposal with an assigned mentor can be turned into
  #: a accepted proposal. A proposal can only have one mentor.
  mentor = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                required=False,
                                collection_name='student_proposals')

  #: A property containing a list of possible Mentors for this proposal
  possible_mentors = db.ListProperty(item_type=db.Key, default=[])

  #: the current score of this proposal, used to determine which proposals
  #: should be assigned a project slot.
  score = db.IntegerProperty(required=True, default=0)

  #: the status of this proposal
  #: new : the proposal has not been ranked/scored yet
  #: pending: the proposal is in the process of being ranked/scored
  #: accepted: the proposal has been assigned a project slot
  #: rejected: the proposal has not been assigned a slot
  #: invalid: the student or org admin marked this as an invalid proposal.
  status = db.StringProperty(required=True, default='new',
      choices=['new', 'pending', 'accepted', 'rejected', 'invalid'])

  #: organization to which this proposal is directed
  org = db.ReferenceProperty(
      reference_class=soc.models.organization.Organization,
      required=True, collection_name='student_proposals')

  #: program in which this proposal has been created
  program = db.ReferenceProperty(reference_class=soc.models.program.Program,
                                 required=True,
                                 collection_name='student_proposals')

  #: date when the proposal was created
  created_on = db.DateTimeProperty(required=True, auto_now_add=True)

  #: date when the proposal was last modified, should be set manually on edit
  last_modified_on = db.DateTimeProperty(required=True, auto_now_add=True)
