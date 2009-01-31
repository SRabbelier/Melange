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

"""Group (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.cache import sidebar
from soc.logic.models import base

import soc.models.group


class Logic(base.Logic):
  """Logic methods for the Group model.
  """

  def __init__(self, model=soc.models.group.Group,
               base_model=None, scope_logic=None):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def getKeyValues(self, entity):
    """Extracts the key values from entity and returns them.

    The default implementation for Groups assumes that the Group is site-wide
    and thus has no scope.  Such Groups include Sponsors and Clubs.  Any
    Group that exists per-Program or per-Year will need to override this
    method.

    Args:
      entity: the entity from which to extract the key values
    """

    return [entity.link_id]

  def getKeyValuesFromFields(self, fields):
    """Extracts the key values from a dict and returns them.

    The default implementation for Groups assumes that the Group is site-wide
    and thus has no scope.  Such Groups include Sponsors and Clubs.  Any
    Group that exists per-Program or per-Year will need to override this
    method.

    Args:
      fields: the dict from which to extract the key values
    """

    return [fields['link_id']]

  def getKeyFieldNames(self):
    """Returns an array with the names of the Key Fields.

    The default implementation for Groups assumes that the Group is site-wide
    and thus has no scope.  Such Groups include Sponsors and Clubs.  Any
    Group that exists per-Program or per-Year will need to override this
    method.
    """

    return ['link_id']


  def isDeletable(self, entity):
    """Returns whether the specified Group entity can be deleted.

    Generically, a Group can always be deleted.  Subclasses of group.Logic
    should add their own deletion prerequisites.
    
    Args:
      entity: an existing Group entity in the Datastore
    """

    return True


logic = Logic()
