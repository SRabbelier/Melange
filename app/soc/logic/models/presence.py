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

"""Presence (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from google.appengine.ext import db

from soc.logic.models import base
from soc.logic.models import linkable as linkable_logic

import soc.models.presence


class Logic(base.Logic):
  """Logic methods for the Presence model.
  """

  def __init__(self, model=soc.models.presence.Presence,
               base_model=None, scope_logic=linkable_logic):
    """Defines the name, key_name and model for this entity.
    """

    super(Logic, self).__init__(model, base_model=base_model,
                                scope_logic=scope_logic)

  def getToS(self, entity):
    """Returns the ToS Document of the Presence entity, or None if no ToS.

    Args:
      entity:  Presence (or one of its sub-classes) entity that may or may
        not have a ToS Document attached
    """
    if not entity:
      return None

    try:
      tos_doc = entity.tos
    except db.Error:
      return None

    return tos_doc


logic = Logic()
