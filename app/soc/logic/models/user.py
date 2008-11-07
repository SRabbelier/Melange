#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""User (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic.models import base

import soc.models.user


class Logic(base.Logic):
  """Logic methods for the User model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "User"
    self._model = soc.models.user.User
    self._skip_properties = ['former_ids']

  def isFormerId(self, id):
    """Returns true if id is in former ids"""
    # TODO(pawel.solyga): replace 1000 with solution that works for any number of queries
    users_with_former_ids = soc.models.user.User.gql('WHERE former_ids != :1', None).fetch(1000)
    
    for former_id_user in users_with_former_ids: 
      if id in former_id_user.former_ids:
        return True
    
    return False

  def getKeyValues(self, entity):
    """See base.Logic.getKeyValues.
    """
    
    return [entity.id.email()]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    properties = {
        'link_name': fields['link_name']
        }

    entity = self.getForFields(properties, unique=True)
    return [entity.id.email()]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames
    """

    return ['email']

  def updateOrCreateFromId(self, properties, id):
    """Like updateOrCreateFromKeyName, but resolves id to a key_name first.
    """

    # attempt to retrieve the existing entity
    user = soc.models.user.User.gql('WHERE id = :1', id).get()
    
    if user:
      key_name = user.key().name()
    else:
      key_name  = self.getKeyNameForFields({'email': id.email()})

    return self.updateOrCreateFromKeyName(properties, key_name)

  def _updateField(self, model, name, value):
    """Special case logic for id.

    When the id is changed, the former_ids field should be appended
    with the old id.
    """
    if name == 'id' and model.id != value:
      model.former_ids.append(model.id)

    return True


logic = Logic()
