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

import soc.models.document
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

  #: Whether the duplicates are visible
  duplicates_visible = db.BooleanProperty(default=False,
      verbose_name=ugettext('Duplicate proposals visible'))
  duplicates_visible.help_text = ugettext(
      'Field used to indicate if the duplicate proposal should be visible.')

  #: The document entity which contains "About" page for the program
  about_page = db.ReferenceProperty(
      reference_class=soc.models.document.Document,
      verbose_name=ugettext('About page document'))
  about_page.collection_name = 'about_page'
  about_page.help_text = ugettext('The document with <b>About</b>')

  #: The document entity which contains "Events & Timeline" page
  #: for the program
  events_page = db.ReferenceProperty(
      reference_class=soc.models.document.Document,
      verbose_name=ugettext('Events page document'))
  events_page.collection_name = 'events_page'
  events_page.help_text = ugettext(
      'The document with <b>Events & Timeline</b>')

  #: The document entity which contains "Connect With Us" page
  #: for the program
  connect_with_us_page = db.ReferenceProperty(
      reference_class=soc.models.document.Document,
      verbose_name=ugettext('Connect with us document'))
  connect_with_us_page.collection_name = 'connect_with_us_page'
  connect_with_us_page.help_text = ugettext(
      'The document with <b>Connect With Us</b>')

  privacy_policy = db.ReferenceProperty(
      reference_class=soc.models.document.Document,
      verbose_name=ugettext("Privacy Policy Document"))
  privacy_policy.collection_name = 'privacy_policy_page'
  privacy_policy.help_text = ugettext(
      "The document containing <b>Privacy Policy</b>")

  facebook = db.LinkProperty(
      required=False, verbose_name=ugettext("Facebook URL"))
  facebook.help_text = ugettext("URL of the Facebook page for the program")
  facebook.group = ugettext("1. Public Info")

  twitter = db.LinkProperty(
      required=False, verbose_name=ugettext("Twitter URL"))
  twitter.help_text = ugettext("URL of the Twitter profile for the program")
  twitter.group = ugettext("1. Public Info")

  blogger = db.LinkProperty(
      required=False, verbose_name=ugettext("Blogger URL"))
  blogger.help_text = ugettext("URL of the Blogger home page for the program")
  blogger.group = ugettext("1. Public Info")

  email = db.EmailProperty(
      required=False, verbose_name=ugettext("Program email"))
  email.help_text = ugettext("Contact email address for the program")
  email.group = ugettext("1. Public Info")

  irc = db.EmailProperty(
      required=False, verbose_name=ugettext("IRC URL"))
  irc.help_text = ugettext("URL of the irc channel for the program in "
                           "the format irc://<channel>@server")
  irc.group = ugettext("1. Public Info")
