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

"""Host (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import key_name
from soc.logic.models import base

import soc.models.host


class Logic(base.Logic):
  """Logic methods for the Host model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "host"
    self._model = soc.models.host.Host
    self._keyName = key_name.nameHost
    self._skip_properties = []

  def getKeyValues(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.sponsor.link_name, entity.user.link_name]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['sponsor'].link_name, fields['user'].link_name]

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames
    """

    return ['sponsor_ln', 'user_ln']

logic = Logic()
