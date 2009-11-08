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

from taggable.taggable import Tag
from taggable.taggable import Taggable
from taggable.taggable import tag_property

import soc.models.linkable
import soc.models.role
import soc.models.student
import soc.models.user

import soc.modules.ghop.models.program


class TaskTag(Tag):
  """Model for storing all Task tags.
  """

  #: Each task_type tag is scoped under the program. 
  scope = db.ReferenceProperty(reference_class=soc.models.linkable.Linkable,
                               required=True,
                               collection_name='task_type_tags')

  order = db.IntegerProperty(required=True, default=0)

  @classmethod
  def __key_name(cls, scope_path, tag_name):
    """Create the key_name from program key_name as scope_path and tag_name.
    """
    return scope_path + '/' + tag_name

  @classmethod
  def get_by_name(cls, tag_name):
    """Get the list of tag objects that has the given tag_name.
    """
    tags = db.Query(cls).filter('tag =', tag_name).fetch(1000)
    return tags

  @classmethod
  def get_by_scope(cls, scope):
    """Get the list of tag objects that has the given scope.
    """
    tags = db.Query(cls).filter('scope =', scope).order('order').fetch(1000)
    return tags

  @classmethod
  def get_highest_order(cls, scope):
    """Get a tag with highest order.
    """
    tags = db.Query(cls).filter('scope =', scope).order('-order').fetch(1)
    if tags:
      return tags[0].order
    else:
      return -1

  @classmethod
  def get_by_scope_and_name(cls, scope, tag_name):
    """Get a tag by scope and name.

    There can be only one such tag.
    """

    tags = db.Query(cls).filter(
        'scope =', scope).filter('tag =', tag_name).fetch(1)
    if tags:
      return tags[0]
    else:
      return None

  @classmethod
  def update_order(cls, scope, tag_name, order):
    """Updates the order of the tag.
    """

    tag = cls.get_by_scope_and_name(scope, tag_name)
    if tag:
      tag.order = order
      tag.put()

    return tag

  @classmethod
  def copy_tag(cls, scope, tag_name, new_tag_name):
    """Copy a tag with a given scope and tag_name to another tag with
    new tag_name.
    """
    tag = cls.get_by_scope_and_name(scope, tag_name)

    if tag:
      tag_key_name = cls.__key_name(scope.key().name(), new_tag_name)
      existing_tag = cls.get_by_key_name(tag_key_name)

      if existing_tag is None:
        new_tag = cls(key_name=tag_key_name, tag=new_tag_name, scope=scope, 
                      added=tag.added, tagged=tag.tagged,
                      tagged_count=tag.tagged_count)
        new_tag.put()
        tag.delete()

        return new_tag

      return existing_tag

    return None

  @classmethod
  def delete_tag(cls, scope, tag_name):
    """Copy a tag with a given scope and tag_name to another tag with
    new tag_name.
    """
    tag = cls.get_by_scope_and_name(scope, tag_name)

    if tag:
      tag.delete()
      return True

    return False

  @classmethod
  def get_or_create(cls, scope, tag_name, order=0):
    """Get the Tag object that has the tag value given by tag_value.
    """
    tag_key_name = cls.__key_name(scope.key().name(), tag_name)
    existing_tag = cls.get_by_key_name(tag_key_name)
    if existing_tag is None:
      # the tag does not yet exist, so create it.
      if not order:
        order = cls.get_highest_order(scope=scope) + 1
      def create_tag_txn():
        new_tag = cls(key_name=tag_key_name, tag=tag_name,
                      scope=scope, order=order)
        new_tag.put()
        return new_tag
      existing_tag = db.run_in_transaction(create_tag_txn)
    return existing_tag


class TaskTypeTag(TaskTag):
  """Model for storing of task type tags.
  """

  pass


class TaskDifficultyTag(TaskTag):
  """Model for storing of task difficulty level tags.
  """

  pass


class TaskArbitraryTag(TaskTag):
  """Model for storing of arbitrary tags.
  """

  def __init__(self, *args, **kwds):
    """Initialization function.
    """

    TaskTag.__init__(self, *args, **kwds)
    self.auto_delete = True


class GHOPTask(Taggable, soc.models.linkable.Linkable):
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
  difficulty = tag_property('difficulty')

  #: Required field which contains the type of the task. These types are
  #: configured by a Program Admin.
  task_type = tag_property('task_type')

  #: Field which contains the arbitrary tags for the task. These tags can
  #: be assigned by Org Admins and mentors.
  arbit_tag = tag_property('arbit_tag')

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
      reference_class=soc.modules.ghop.models.program.GHOPProgram,
      required=True, collection_name='tasks')

  #: Required property which holds the state, the Task is currently in.
  #: This is a hidden field not shown on forms. Handled by logic internally.
  #: The state can be one of the following:
  #: Unapproved: If Task is created by a Mentor, this is the automatically
  #:   assigned state.
  #: Unpublished: This Task is not published yet.
  #: Open: This Task is open and ready to be claimed.
  #: Reopened: This Task has been claimed but never finished and has been
  #:   reopened.
  #: ClaimRequested: A Student has requested to claim this task.
  #: Claimed: This Task has been claimed and someone is working on it.
  #: ActionNeeded: Work on this Task must be submitted for review within 
  #:   24 hours.
  #: Closed: Work on this Task has been completed to the org's content.
  #: AwaitingRegistration: Student has completed work on this task, but
  #:   needs to complete Student registration before this task is closed.
  #: NeedsWork: This work on this Tasks needs a bit more brushing up. This
  #:   state is followed by a Mentor review.
  #: NeedsReview: Student has submitted work for this task and it should
  #:   be reviewed by a Mentor.
  #: Invalid: The Task is deleted either by an Org Admin/Mentor
  status = db.StringProperty(
      required=True, verbose_name=ugettext('Status'),
      choices=['Unapproved', 'Unpublished', 'Open', 'Reopened', 
               'ClaimRequested', 'Claimed', 'ActionNeeded', 
               'Closed', 'AwaitingRegistration', 'NeedsWork',
               'NeedsReview', 'Invalid'],
      default='Unapproved')

  #: This field is set to the next deadline that will have consequences for
  #: this Task. For instance this will store a DateTime property which will
  #: tell when this Task should be completed.
  deadline = db.DateTimeProperty(required=False,
                                 verbose_name=ugettext('Deadline'))

  #: Required field containing the Mentor/Org Admin who created this task.
  #: If site developer has created the task, it is empty.
  created_by = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                    required=False,
                                    collection_name='created_tasks',
                                    verbose_name=ugettext('Created by'))

  #: Date when the proposal was created
  created_on = db.DateTimeProperty(required=True, auto_now_add=True,
                                   verbose_name=ugettext('Created on'))

  #: Required field containing the Mentor/Org Admin who last edited this
  #: task. It changes only when Mentor/Org Admin changes title, description,
  #: difficulty, task_type, time_to_complete. If site developer has modified
  #: the task, it is empty.
  modified_by = db.ReferenceProperty(reference_class=soc.models.role.Role,
                                   required=False,
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
  history = db.TextProperty(required=False, default='')

  def __init__(self, parent=None, key_name=None, 
               app=None, **entity_values):
    """Constructor for GHOPTask Model.
    
    Args:
        See Google App Engine APIs.
    """

    # explicitly call the AppEngine datastore Model constructor
    db.Model.__init__(self, parent, key_name, app, **entity_values)

    # call the Taggable constructor to initialize the tags specified as
    # keyword arguments
    Taggable.__init__(self, task_type=TaskTypeTag, 
                      difficulty=TaskDifficultyTag,
                      arbit_tag=TaskArbitraryTag)
