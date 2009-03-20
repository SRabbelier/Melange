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

"""This module contains the Program Model.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.presence
import soc.models.timeline


class Program(soc.models.presence.Presence):
  """The Program model, representing a Program ran by a Sponsor.
  """

  #: Required field storing name of the group.
  name = db.StringProperty(required=True,
      verbose_name=ugettext('Name'))
  name.help_text = ugettext('Complete, formal name of the program.')
  name.example_text = ugettext(
      '<small><i>e.g.</i></small> <tt>Google Summer of Code 2009</tt>')

  #: Required field storing short name of the group.
  #: It can be used for displaying group as sidebar menu item.
  short_name = db.StringProperty(required=True,
      verbose_name=ugettext('Short name'))
  short_name.help_text = ugettext('Short name used for sidebar menu')
  short_name.example_text = ugettext(
      '<small><i>e.g.</i></small> <tt>GSoC 2009</tt>')

  #: Optional field used to relate it to other programs
  #: For example, GSoC would be a group label for GSoC2008/GSoC2009
  group_label = db.StringProperty(
      verbose_name=ugettext('Group label'))
  group_label.help_text = ugettext(
      'Optional name used to relate this program to others.')
  group_label.example_text = ugettext(
      '<small><i>e.g.</i></small> <tt>GSoC</tt>')

  #: Required field storing description of the group.
  description = db.TextProperty(required=True,
      verbose_name=ugettext('Description'))
  description.example_text = ugettext(
      '<small><i>for example:</i></small><br>'
      '<tt><b>GSoC 2009</b> is the <i>Google Summer of Code</i>,'
      ' but in <u>2009</u>!</tt><br><br>'
      '<small><i>(rich text formatting is supported)</i></small>')

  #: Required field storing description of the group.
  accepted_orgs_msg = db.TextProperty(required=False,
      verbose_name=ugettext('Accepted Organizations Message'))
  accepted_orgs_msg.help_text = ugettext(
      '<small><i>for example:</i></small><br>'
      '<tt>Students who wish to participate can find out more about'
      ' each mentoring organization below.</tt><br><br>'
      '<small><i>(rich text formatting is supported)</i></small>')

  #: Required field storing application/tasks limit of the program.
  apps_tasks_limit = db.IntegerProperty(required=True,
      verbose_name=ugettext('Application/Tasks Limit'))
  apps_tasks_limit.example_text = ugettext(
      '<small><i>e.g.</i></small> '
      '<tt><b>20</b> is the student applications limit for <i>Google Summer '
      'of Code</i>, but <b>1</b> is the tasks limit that the student can work '
      'on at the same time during <i>GHOP</i></tt>')

  #: Required field storing slots limit of the program.
  slots = db.IntegerProperty(required=True,
      verbose_name=ugettext('Slots'))
  slots.example_text = ugettext(
      '<small><i>e.g.</i></small> '
      '<tt><b>500</b> might be an amount of slots for <i>Google Summer '
      'of Code</i>, which indicates how many students can be accepted '
      'to the program.<br>For <i>GHOP</i> this indicates how '
      'many tasks can be completed.</tt>')

  #: Required field storing the type of workflow this program has
  workflow = db.StringProperty(required=True,
      choices=['gsoc', 'ghop'],
      verbose_name= ugettext('Workflow type'))
  workflow.example_text = ugettext(
      '<tt><b>Project-based</b> for GSoC workflow type,<br>' 
      '<b>Task-based</b> for GHOP workflow type.</tt>')

  #: Required 1:1 relationship indicating the Program the Timeline
  #: belongs to.
  timeline = db.ReferenceProperty(reference_class=soc.models.timeline.Timeline,
                                 required=True, collection_name="program",
                                 verbose_name=ugettext('Timeline'))

  #: Whether the slots allocations are visible
  allocations_visible = db.BooleanProperty(default=False,
      verbose_name=ugettext('Slot allocations visible'))
  allocations_visible.help_text = ugettext(
      'Field used to indicate if the slot allocations should be visible.')

  #: Document reference property used for the Org Admin Agreement
  org_admin_agreement = db.ReferenceProperty(
    reference_class=soc.models.document.Document,
    verbose_name=ugettext('Organization Admin Agreement'),
    collection_name='org_admin_agreement')
  org_admin_agreement.help_text = ugettext(
      'Document containing optional Mentor Agreement for participating as a '
      'Organization admin.')

  #: Document reference property used for the Mentor Agreement
  mentor_agreement = db.ReferenceProperty(
    reference_class=soc.models.document.Document,
    verbose_name=ugettext('Mentor Agreement'),
    collection_name='mentor_agreement')
  mentor_agreement.help_text = ugettext(
      'Document containing optional Mentor Agreement for participating as a '
      'Mentor.')

  #: Document reference property used for the Student Agreement
  student_agreement = db.ReferenceProperty(
    reference_class=soc.models.document.Document,
    verbose_name=ugettext('Student Agreement'),
    collection_name='student_agreement')
  student_agreement.help_text = ugettext(
      'Document containing optional Student Agreement for participating as a '
      'Student.')

  #: Status of the program
  #: Invisible: Program Stealth-Mode Visible to Hosts and Devs only
  #: Visible: Visible to everyone.
  #: Inactive: Not visible in sidebar but can be reached for date retention
  #: Invalid: Not visible or editable by anyone
  status = db.StringProperty(required=True, default='invisible',
      verbose_name=ugettext('Program Status'),
      choices=['invisible', 'visible', 'inactive', 'invalid'])
  status.example_text = ugettext(
      '<tt>Invisible: Program Stealth-Mode Visible to Hosts and Devs only.<br/>'
      'Visible: Visible to everyone.<br/>'
      'Inactive: Not visible in sidebar, not editable.<br/>'
      'Invalid: Not visible or editable by anyone.</tt>')
