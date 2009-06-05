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

"""This module contains the GHOP Task Model.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable
import soc.models.role
import soc.models.student
import soc.models.user

from soc.modules.ghop.models import program as ghop_program_model


class GHOPTask(soc.models.linkable.Linkable):
  """Model for a task used in GHOP workflow.

  The scope property of Linkable will be set to the Organization to which
  this task belongs to. A link_id will be generated automatically and will
  have no specific meaning other than identification.
  """

  #: Required field indicating the "title" of the task
  title = db.StringProperty(required=True,
                            verbose_name=ugettext('Title'))
  title.help_text = ugettext('Title of the task')

  #: Required field containing the description of the task
  description = db.TextProperty(required=True, 
                                verbose_name=ugettext('Description'))
  description.help_text = ugettext('Complete description of the task')

  #: Field indicating the difficulty level of the Task. This is not
  #: mandatory so the it can be assigned at any later stage. 
  #: The options are configured by a Program Admin.
  difficulty = db.StringProperty(required=False,
                                 verbose_name=ugettext('Difficulty'))
  difficulty.help_text = ugettext('Difficulty Level of the task')

  #: Required field which contains the type of the task. These types are
  #: configured by a Program Admin.
  type = db.StringListProperty(required=True, 
                               verbose_name=ugettext('Task Type'))
  type.help_text = ugettext('Type of the task')

  #: A field which contains time allowed for completing the task (in hours)
  #: from the moment that this task has been assigned to a Student
  time_to_complete = db.IntegerProperty(required=True,
                                        verbose_name=('Time to Complete'))
  time_to_complete.help_text = ugettext(
      'Time allowed to complete the task, in hours, once it is claimed')

  #: List of Mentors assigned to this task. A Mentor who creates this
  #: task is assigned as the Mentor by default. An Org Admin will have
  #: to assign a Mentor upon task creation.
  mentors = db.ListProperty(item_type=db.Key, default=[])

  #: User profile to whom this task has been claimed by. This field
  #: is mandatory for claimed tasks
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=False,
                              collection_name='assigned_tasks')

  #: Student profile to whom this task is currently assigned to. If the user
  #: has registered as a Student than this field will be filled in. This field
  #: is mandatory for all Tasks in the closed state.
  student = db.ReferenceProperty(reference_class=soc.models.student.Student,
                                 required=False,
                                 collection_name='assigned_tasks')

  #: Program in which this Task has been created
  program = db.ReferenceProperty(
      reference_class=ghop_program_model.GHOPProgram,
      required=True, collection_name='tasks')

  #: Required property which holds the state, the Task is currently in.
  #: This is a hidden field not shown on forms. Handled by logic internally.
  #: The state can be one of the following:
  #: unapproved: If Task is created by a Mentor, this is the automatically
  #:   assigned state.
  #: unpublished: This Task is not published yet.
  #: open: This Task is open and ready to be claimed.
  #: reopened: This Task has been claimed but never finished and has been
  #:   reopened.
  #: claim_requested: A Student has requested to claim this task.
  #: claimed: This Task has been claimed and someone is working on it.
  #: action_needed: Work on this Task must be submitted for review within 
  #:   24 hours.
  #: closed: Work on this Task has been completed to the org's content.
  #: awaiting_registration: Student has completed work on this task, but
  #:   needs to complete Student registration before this task is closed.
  #: needs_work: This work on this Tasks needs a bit more brushing up. This
  #:   state is followed by a Mentor review.
  #: needs_review: Student has submitted work for this task and it should
  #:   be reviewed by a Mentor.
  status = db.StringProperty(
      required=True, verbose_name=ugettext('Status'),
      choices=['unapproved', 'unpublished', 'open', 'reopened', 
               'claim_requested', 'claimed', 'action_needed', 
               'closed', 'awaiting_registration', 'needs_work',
               'needs_review'],
      default='unapproved')

  #: A field which indicates if the Task was ever in the Reopened state.
  #: True indicates that its state was Reopened once, false indicated that it
  #: has never been in the Reopened state.
  was_reopened = db.BooleanProperty(default=False,
                                    verbose_name=ugettext('Has been reopened'))

  #: This field is set to the next deadline that will have consequences for
  #: this Task. For instance this will store a DateTime property which will
  #: tell when this Task should be completed.
  deadline = db.DateTimeProperty(required=False,
                                 verbose_name=ugettext('Deadline'))

  #: Required field containing the Mentor/Org Admin who created this task
  created_by = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                    required=True,
                                    collection_name='created_tasks',
                                    verbose_name=ugettext('Created by'))

  #: Date when the proposal was created
  created_on = db.DateTimeProperty(required=True, auto_now_add=True,
                                   verbose_name=ugettext('Created on'))

  #: Required field containing the Mentor/Org Admin who last edited this
  #: task. It changes only when Mentor/Org Admin changes title, description,
  #: difficulty, type, time_to_complete.
  modified_by = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                   required=True,
                                   collection_name='edited_tasks',
                                   verbose_name=ugettext('Modified by'))

  #: Date when the proposal was last modified, should be set manually on edit
  modified_on = db.DateTimeProperty(required=True, auto_now_add=True,
                                    verbose_name=ugettext('Modified on'))

  #: A field which holds the entire history of this task in JSON. The
  #: structure of this JSON string is as follows:
  #: {
  #:    timestamp1: {
  #:                   "user": User reference
  #:                   "student": Student reference
  #:                   ...
  #:                   "state": "Unapproved"
  #:                   ...
  #:                   "edited_by": Role reference
  #:                   
  #:               }
  #:    timestamp2: {
  #:                   "state": "Unpublished"
  #:               }
  #: }
  #: First dictionary item holds the values for all the properties in this
  #: model. The subsequent items hold the properties that changed at the
  #: timestamp given by the key.
  #: Reference properties will be stored by calling str() on their Key.
  history = db.TextProperty(required=True, default='')
