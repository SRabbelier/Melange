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

"""Various (Model) query functions.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverer@rabbelier.nl>',
  ]


import key_name
import model
import soc.models.document
import soc.models.sponsor
import soc.models.work
import soc.models.site_settings


class DocumentLogic(model.BaseLogic):
  """Logic methods for the Document model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "document"
    self._model = soc.models.document.Document
    self._keyName = key_name.nameDocument
    self._skip_properties = []


class SettingsLogic(model.BaseLogic):
  """Logic methods for the Settings model
  """


  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "settings"
    self._model = soc.models.site_settings.SiteSettings
    self._keyName = key_name.nameSiteSettings
    self._skip_properties = []


class SponsorLogic(model.BaseLogic):
  """Logic methods for the Sponsor model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "sponsor"
    self._model = soc.models.sponsor.Sponsor
    self._keyName = key_name.nameSponsor
    self._skip_properties = []


class UserLogic(model.BaseLogic):
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

class WorkLogic(model.BaseLogic):
  """Logic methods for the Work model
  """

  def __init__(self):
    """Defines the name, key_name and model for this entity.
    """

    self._name = "work"
    self._model = soc.models.work.Work
    self._keyName = key_name.nameWork
    self._skip_properties = []
    # TODO(tlarsen) write a nameWork method


document_logic = DocumentLogic()
settings_logic = SettingsLogic()
sponsor_logic = SponsorLogic()
user_logic = UserLogic()
work_logic = WorkLogic()
