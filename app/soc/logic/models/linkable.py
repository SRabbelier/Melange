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

"""Linkable (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic.models import base

import soc.models.linkable


class Logic(base.Logic):
  """Logic methods for the Linkable model.

  Note: Logic classes should not inherit from this class, instead
  it is meant to be referred to with scope_logic.
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(soc.models.linkable.Linkable)

  def getScopeDepth(self):
    """Returns the scope depth for this entity.

    As it is impossible to determine the scope depth of a Linkable,
    None is returned. This causes the scope regexp to match a scope
    with an arbitrary depth. 
    """

    return None


logic = Logic()
