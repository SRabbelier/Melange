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

"""Priority Group (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic.models import base

import soc.models.priority_group


class Logic(base.Logic):
  """Logic methods for the Priority Group model.
  """

  def __init__(self, model=soc.models.priority_group.PriorityGroup,
               base_model=None, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    # pylint: disable-msg=C0103
    self.EMAIL = 'emails'
    self.CONVERT = 'convert'

    self.groups = {
        self.EMAIL: 'Send out emails',
        self.CONVERT: 'Convert one entity to another type',
        }

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def getKeyValuesFromEntity(self, entity):
    """See base.Logic.getKeyValuesFromEntity.
    """

    return [entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['link_id']

  def getGroup(self, key_name):
    """Return the specified Priority Group entity.
    """

    if key_name not in self.groups:
      raise base.InvalidArgumentError("Unknown priority group %s." % key_name)

    group = self.getFromKeyName(key_name)

    if not group:
      fields = {
          'link_id': key_name,
          'name': self.groups[key_name],
          'priority': 0,
          }

      group = self.updateOrCreateFromKeyName(fields, key_name)

    return group


logic = Logic()
