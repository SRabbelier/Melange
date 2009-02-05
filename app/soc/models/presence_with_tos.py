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

"""This module contains the PresenceWithToS Model.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.presence


class PresenceWithToS(soc.models.presence.Presence):
  """Model of a Presence that has a Terms of Service.
  """

  #: Reference to Document containing optional Terms of Service
  tos = db.ReferenceProperty(
    reference_class=soc.models.document.Document,
    verbose_name=ugettext('Terms of Service'),
    collection_name='tos')
  tos.help_text = ugettext(
      'Document containing optional Terms of Service for participating.')
