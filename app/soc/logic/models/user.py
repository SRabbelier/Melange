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


from soc.logic import key_name
from soc.logic.models import base

import soc.models.user


class Logic(base.Logic):
  """Logic methods for the User model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "user"
    self._model = soc.models.user.User
    self._keyName = key_name.nameUser
    self._skip_properties = ['former_ids']

  def _updateField(self, model, name, value):
    """Special case logic for id.

    When the id is changed, the former_ids field should be appended
    with the old id.
    """
    if name == 'id' and model.id != value:
      model.former_ids.append(model.id)

    return True


logic = Logic()
