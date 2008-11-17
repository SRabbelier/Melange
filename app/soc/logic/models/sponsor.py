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

"""Sponsor (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import key_name
from soc.logic.models import base

import soc.models.group
import soc.models.sponsor


class Logic(base.Logic):
  """Logic methods for the Sponsor model.
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """
    base.Logic.__init__(self, soc.models.sponsor.Sponsor,
                        base_model=soc.models.group.Group)

  def getKeyValues(self, entity):
    """See base.Logic.getKeyNameValues.
    """

    return [entity.link_name]

  def getKeyValuesFromFields(self, fields):
    """See base.Logic.getKeyValuesFromFields.
    """

    return [fields['link_name']] 

  def getKeyFieldNames(self):
    """See base.Logic.getKeyFieldNames.
    """

    return ['link_name']


  def isDeletable(self, entity):
    """Returns whether the specified Sponsor entity can be deleted.
    
    Args:
      entity: an existing Sponsor entity in datastore
    """
    # TODO(pawel.solyga): Check if Sponsor can be deleted (no Hosts, Programs)
    return True

logic = Logic()
