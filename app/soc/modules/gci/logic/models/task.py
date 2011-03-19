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

"""GCITask (Model) query functions.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime

from google.appengine.ext import db

from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import tags
from soc.logic.models import base
from soc.logic.models.site import logic as site_logic

from soc.modules.gci.logic.models.comment import logic as gci_comment_logic

import soc.models.linkable

import soc.modules.gci.logic.models.organization
import soc.modules.gci.models.task


STATE_TRANSITIONS = {
    'Claimed': 'transitFromClaimed',
    'NeedsReview': 'transitFromNeedsReview',
    'ActionNeeded': 'transitFromActionNeeded',
    'NeedsWork': 'transitFromNeedsWork',
    'Invalid': 'transitFromInvalid',
    }

TAG_NAMES = ['arbit_tag', 'difficulty', 'task_type']

class Logic(base.Logic):
  """Logic methods for the GCITask model.
  """

  DEF_ACTION_NEEDED_MSG = ugettext(
      '(The Melange Automated System has detected that the intial '
      'deadline has been passed and it has set the task status to '
      'ActionNeeded.)')

  DEF_INVALID_MSG = ugettext(
      '(This task was marked invalid by an administrator. Please '
      'contact the %(site_name)s team if you have any questions '
      'regarding the same.)')

  DEF_NO_MORE_WORK_MSG = ugettext(
      '(The Melange Automated System has detected that the deadline '
      'has been passed and no more work can be submitted.)')

  DEF_REOPENED_MSG = ugettext(
      '(The Melange Automated System has detected that the final '
      'deadline has been passed and it has Reopened the task.)')


  def __init__(self, model=soc.modules.gci.models.task.GCITask,
               base_model=soc.models.linkable.Linkable, 
               scope_logic=soc.modules.gci.logic.models.organization):
    """Defines the name, key_name and model for this entity.
    """

    self.tags_service = tags.TagsService(TAG_NAMES)

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def updateEntityProperties(self, entity, entity_properties,
                             silent=False, store=True):
    """See base.Logic.updateEntityProperties().

    Also ensures that the history property of the task is updated in the same
    datastore operation.
    """

    # TODO: History needs a proper test drive and perhaps a refactoring
    history = {}

    # we construct initial snapshot of the task when it is published
    # for the first time.
    if entity_properties and 'status' in entity_properties:
      if entity.status == 'Unpublished' or entity.status == 'Unapproved':
        if entity_properties['status'] == 'Open':
          history = {
              'title': entity.title,
              'description': entity.description,
              'difficulty': entity.taskDifficulty().tag,
              'task_type': [type.tag for type in entity.task_type],
              'time_to_complete': entity.time_to_complete,
              'mentors': [m_key.id_or_name() for m_key in entity.mentors],
              'user': '',
              'student': '',
              'status': entity.status,
              'deadline': '',
              'created_by': entity.created_by.key().id_or_name(),
              'created_on': str(entity.created_on),
              'modified_on': str(entity.modified_on),
              }

          if entity.modified_by:
            history['modified_by'] = entity.modified_by.key().id_or_name()

          # initialize history
          task_history = {}
      # extract the existing json history from the entity to update it
    elif entity.history:
      task_history = simplejson.loads(entity.history)
    else:
      task_history = {}

      # we construct history for only changed entity properties
      if entity_properties:
        for property in entity_properties:
          changed_val = getattr(entity, property)
          if changed_val != entity_properties[property]:
            if property == 'deadline':
              history[property] = str(changed_val)
            else:
              history[property] = changed_val

    if history:
      # create a dictionary for the new history update with timestamp as key
      tstamp = str(datetime.datetime.now())
      new_history = {tstamp: history}

      # update existing history
      task_history.update(new_history)
      task_history_str = simplejson.dumps(task_history)

      # update the task's history property
      history_property = {
          'history': task_history_str
          }
      entity_properties.update(history_property)

    entity = self.tags_service.setTagValuesForEntity(entity, entity_properties)

    # call the base logic method to store the updated Task entity
    return super(Logic, self).updateEntityProperties(
        entity, entity_properties, silent=silent, store=store)

  def updateEntityPropertiesWithCWS(self, entity, entity_properties,
                                    comment_properties=None, 
                                    ws_properties=None, silent=False):
    """Updates the GCITask entity properties and creates a comment
    entity.

    Args:
      entity: a model entity
      entity_properties: keyword arguments that correspond to entity
          properties and their values
      comment_properties: keyword arguments that correspond to the
          GCITask's to be created comment entity
      silent: iff True does not call post store methods.
    """

    # pylint: disable=W0621
    from soc.modules.gci.logic.models.work_submission import logic as \
        gci_work_submission_logic
    from soc.modules.gci.models import comment as gci_comment_model
    from soc.modules.gci.models import work_submission as \
        gci_work_submission_model

    if entity_properties:
      entity = self.updateEntityProperties(entity, entity_properties, 
                                           silent=silent, store=False)

    comment_entity = gci_comment_model.GCIComment(**comment_properties)

    ws_entity = None
    if ws_properties:
      ws_entity = gci_work_submission_model.GCIWorkSubmission(
          **ws_properties)

    def comment_create():
      """Method to be run in transaction that stores Task, Comment and
      WorkSubmission.
      """
      entity.put()
      if ws_entity:
        ws_entity.put()
        comment_entity.content = comment_entity.content % (
            ws_entity.key().id_or_name())
        comment_entity.put()
        return entity, comment_entity, ws_entity
      else:
        comment_entity.put()
        return entity, comment_entity, None

    entity, comment_entity, ws_entity = db.run_in_transaction(
        comment_create)

    if not silent:
      # call the _onCreate methods for the Comment and WorkSubmission
      if comment_entity:
        gci_comment_logic._onCreate(comment_entity)

      if ws_entity:
        gci_work_submission_logic._onCreate(ws_entity)

    return entity, comment_entity, ws_entity

  def updateOrCreateFromFields(self, properties, silent=False):
    """See base.Logic.updateOrCreateFromFields().
    """

    # TODO: History needs to be tested and perhaps refactored
    if properties.get('status') == 'Open':
      history = {
          'title': properties['title'],
          'description': properties['description'],
          'difficulty': properties['difficulty']['tags'],
          'task_type': properties['type_tags'],
          'time_to_complete': properties['time_to_complete'],
          'mentors': [m_key.id_or_name() for m_key in properties['mentors']],
          'user': '',
          'student': '',
          'status': properties['status'],
          'deadline': '',
          'created_on': str(properties['created_on']),
          'modified_on': str(properties['modified_on']),
          }

      if 'created_by' in properties and properties['created_by']:
        history['created_by'] = properties['created_by'].key().id_or_name()
        history['modified_by'] = properties['modified_by'].key().id_or_name()

      # Constructs new history from the _constructNewHistory method, assigns
      # it as a value to the dictionary key with current timestamp and dumps
      # a JSON string.
      task_history_str = simplejson.dumps({
          str(datetime.datetime.now()): history,
          })

      # update the task's history property
      history_property = {
          'history': task_history_str
          }
      properties.update(history_property)

    entity = super(Logic, self).updateOrCreateFromFields(properties, silent)

    self.tags_service.setTagValuesForEntity(entity, properties)

    return entity

  def _onCreate(self, entity):
    """See base.Logic._onCreate().
    """

    from soc.modules.gci.logic.models import task_subscription as \
        gci_ts_logic

    gci_ts_logic.logic.subscribeUser(entity, entity.created_by.user)

    return super(Logic, self)._onCreate(entity)

  def getFromKeyFieldsWithCWSOr404(self, fields):
    """Returns the Task, all Comments and all WorkSubmissions for the Task
    specified by the fields argument.

    For args see base.getFromKeyFieldsOr404().
    """

    # pylint: disable=W0621
    from soc.modules.gci.logic.models.work_submission import logic as \
        gci_work_submission_logic
 
    entity = self.getFromKeyFieldsOr404(fields)

    comment_entities = gci_comment_logic.getForFields(
        ancestors=[entity], order=['created_on'])

    ws_entities = gci_work_submission_logic.getForFields(
        ancestors=[entity], order=['submitted_on'])

    return entity, comment_entities, ws_entities

  def updateTaskStatus(self, entity):
    """Method used to transit a task from a state to another state
    depending on the context. Whenever the deadline has passed.

    Args:
      entity: The GCITask entity

    Returns:
      Task entity and a Comment entity if the occurring transit created one.
    """

    from soc.modules.gci.tasks import task_update

    if entity.deadline and datetime.datetime.now() >= entity.deadline:
      # calls a specific method to make a transition depending on the
      # task's current state
      transit_func = getattr(self, STATE_TRANSITIONS[entity.status])
      update_dict = transit_func(entity)

      comment_properties = {
          'parent': entity,
          'scope_path': entity.key().id_or_name(),
          'created_by': None,
          'content': update_dict['content'],
          'changes': update_dict['changes'],
          }

      entity, comment_entity, _ = self.updateEntityPropertiesWithCWS(
          entity, update_dict['properties'], comment_properties)

      if entity.deadline:
        # only if there is a deadline set we should schedule another task
        task_update.spawnUpdateTask(entity)
    else:
      comment_entity = None

    return entity, comment_entity

  def transitFromClaimed(self, entity):
    """Makes a state transition of a GCI Task from Claimed state
    to a relevant state.

    Args:
      entity: The GCITask entity
    """

    # deadline is extended by 24 hours.
    deadline = entity.deadline + datetime.timedelta(
        hours=24)

    properties = {
        'status': 'ActionNeeded',
        'deadline': deadline,
        }

    changes = [ugettext('User-MelangeAutomatic'),
               ugettext('Action-Warned for action'),
               ugettext('Status-%s' % (properties['status']))]

    content = self.DEF_ACTION_NEEDED_MSG

    update_dict = {
        'properties': properties,
        'changes': changes,
        'content': content,
        }

    return update_dict

  def transitFromNeedsReview(self, entity):
    """Makes a state transition of a GCI Task from NeedsReview state
    to a relevant state.

    Args:
      entity: The GCITask entity
    """

    properties = {
        'deadline': None,
        }

    changes = [ugettext('User-MelangeAutomatic'),
               ugettext('Action-Deadline passed'),
               ugettext('Status-%s' % (entity.status))]

    content = self.DEF_NO_MORE_WORK_MSG

    update_dict = {
        'properties': properties,
        'changes': changes,
        'content': content,
        }

    return update_dict

  def transitFromActionNeeded(self, entity):
    """Makes a state transition of a GCI Task from ActionNeeded state
    to a relevant state.

    Args:
      entity: The GCITask entity
    """

    properties = {
        'user': None,
        'student': None,
        'status': 'Reopened',
        'deadline': None,
        }

    changes = [ugettext('User-MelangeAutomatic'),
               ugettext('Action-Forcibly reopened'),
               ugettext('Status-Reopened')]

    content = self.DEF_REOPENED_MSG

    update_dict = {
        'properties': properties,
        'changes': changes,
        'content': content,
        }

    return update_dict

  def transitFromNeedsWork(self, entity):
    """Makes a state transition of a GCI Task from NeedsWork state
    to a relevant state.

    Args:
      entity: The GCITask entity
    """

    properties = {
        'user': None,
        'student': None,
        'status': 'Reopened',
        'deadline': None,
        }

    changes = [ugettext('User-MelangeAutomatic'),
               ugettext('Action-Forcibly reopened'),
               ugettext('Status-Reopened')]
    
    update_dict = {
        'properties': properties,
        'changes': changes,
        'content': None,
        }

    return update_dict

  def transitFromInvalid(self, entity):
    """The task was invalidated manually. So post a comment about it
    and unset the deadline.

    Args:
      entity: The GCITask entity
    """

    # do not unset the user and student properties since if student
    # challenges the manual invalidation of the task we should still
    # be able to retrieve the task. So just unset the deadline.
    properties = {
        'deadline': None,
        }

    changes = [ugettext('User-MelangeAutomatic'),
               ugettext('Action-None'),
               ugettext('Status-Invalid')]

    content = self.DEF_INVALID_MSG % {
        'site_name': site_logic.getSingleton().site_name,
        }

    update_dict = {
        'properties': properties,
        'changes': changes,
        'content': content,
        }

    return update_dict

  def delete(self, entity):
    """Delete existing entity from datastore.
    """
    
    def task_delete_txn(entity):
      """Performs all necessary operations in a single transaction when a task
      is deleted.
      """

      to_delete = []    
      to_delete += gci_comment_logic.getForFields(ancestors=[entity])
      to_delete += [entity]
    
      db.delete(to_delete)
  
    self.tags_service.removeAllTagsForEntity(entity)
    db.run_in_transaction(task_delete_txn, entity)


logic = Logic()
