#!/usr/bin/env python2.5
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

"""This module contains the GSoC specific Program Model.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.program


class GSoCProgram(soc.models.program.Program):
  """GSoC Program model extends the basic Program model.
  """

  #: Required field storing application limit of the program.
  apps_tasks_limit = db.IntegerProperty(required=True,
      verbose_name=ugettext('Application/Tasks Limit'))
  apps_tasks_limit.example_text = ugettext(
      '<small><i>e.g.</i></small> '
      '<tt><b>20</b> is the student applications limit for <i>Google Summer '
      'of Code</i>.</tt>')

  #: Optional field storing minimum slots per organization
  min_slots = db.IntegerProperty(required=False, default=2,
      verbose_name=ugettext('Min slots per org'))
  min_slots.help_text = ugettext(
      'The amount of slots each org should get at the very least.')

  #: Optional field storing maximum slots per organization
  max_slots = db.IntegerProperty(required=False, default=50,
      verbose_name=ugettext('Max slots per org'))
  max_slots.help_text = ugettext(
      'The amount of slots each organization should get at most.')

  #: Required field storing slots limit of the program.
  slots = db.IntegerProperty(required=True,
      verbose_name=ugettext('Slots'))
  slots.example_text = ugettext(
      '<small><i>e.g.</i></small> '
      '<tt><b>500</b> might be an amount of slots for <i>Google Summer '
      'of Code</i>, which indicates how many students can be accepted.</tt>')

  #: Optional field storing the allocation of slots for this program
  slots_allocation = db.TextProperty(required=False,
      verbose_name=ugettext('the allocation of slots.'))

  #: Whether the slots allocations are visible
  allocations_visible = db.BooleanProperty(default=False,
      verbose_name=ugettext('Slot allocations visible'))
  allocations_visible.help_text = ugettext(
      'Field used to indicate if the slot allocations should be visible.')
