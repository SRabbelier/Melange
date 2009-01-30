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

"""Document (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.cache import sidebar
from soc.logic.models import work
from soc.logic.models import linkable as linkable_logic

import soc.models.document
import soc.models.work


class Logic(work.Logic):
  """Logic methods for the Document model
  """

  def __init__(self, model=soc.models.document.Document,
               base_model=soc.models.work.Work, scope_logic=linkable_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model=model, base_model=base_model,
                                scope_logic=scope_logic)

  def getKeyValues(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.prefix, entity.scope_path, entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['prefix'], fields['scope_path'], fields['link_id']]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['prefix', 'scope_path', 'link_id']

  def _updateField(self, entity, name, value):
    """Special logic for role. If state changes to active we flush the sidebar.
    """

    if (name == 'is_featured') and (entity.is_featured != value):
      sidebar.flush()

    return True

  def _onCreate(self, entity):
    """Flush the sidebar cache when a new active role entity has been created.
    """

    if entity.is_featured:
      sidebar.flush()


logic = Logic()
