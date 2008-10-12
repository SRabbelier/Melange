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
  '"Sverre Rabbelier" <sverer@rabbelier.nl>',
  ]


from soc.logic import key_name
from soc.logic.models import base
import soc.models.document


class Logic(base.Logic):
  """Logic methods for the Document model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "document"
    self._model = soc.models.document.Document
    self._keyName = key_name.nameDocument
    self._skip_properties = []


logic = Logic()
