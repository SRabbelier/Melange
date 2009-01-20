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

from django.utils.translation import ugettext_lazy

import soc.models.presence
import soc.models.timeline


class Program(soc.models.presence.Presence):
  """The Program model, representing a Program ran by a Sponsor.
  """

  #: Required field storing name of the group.
  name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Name'))
  name.help_text = ugettext_lazy('Complete, formal name of the program.')
  name.example_text = ugettext_lazy(
      '<small><i>e.g.</i></small> <tt>Google Summer of Code 2009</tt>')

  #: Required field storing short name of the group.
  #: It can be used for displaying group as sidebar menu item.
  short_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Short name'))
  short_name.help_text = ugettext_lazy('Short name used for sidebar menu')
  short_name.example_text = ugettext_lazy(
      '<small><i>e.g.</i></small> <tt>GSoC 2009</tt>')

  #: Optional field used to relate it to other programs
  #: For example, GSoC would be a group label for GSoC2008/GSoC2009
  group_label = db.StringProperty(
      verbose_name=ugettext_lazy('Group label'))
  group_label.help_text = ugettext_lazy(
      'Optional name used to relate this program to others.')
  group_label.example_text = ugettext_lazy(
      '<small><i>e.g.</i></small> <tt>GSoC</tt>')

  #: Required field storing description of the group.
  description = db.TextProperty(required=True,
      verbose_name=ugettext_lazy('Description'))
  description.example_text = ugettext_lazy(
      '<small><i>for example:</i></small><br>'
      '<tt><b>GSoC 2009</b> is the <i>Google Summer of Code</i>,'
      ' but in <u>2009</u>!</tt><br><br>'
      '<small><i>(rich text formatting is supported)</i></small>')
  
  #: Required field storing the type of workflow this program has
  workflow = db.StringProperty(required=True,
      choices=['gsoc', 'ghop'],
      verbose_name= ugettext_lazy('Workflow type'))
  workflow.example_text = ugettext_lazy(
      '<b><tt>Project-based</tt></b> for GSoC workflow type,<br>' 
      ' <b><tt>Task-based</tt></b> for GHOP workflow type.')

  #: Required 1:1 relationship indicating the Program the Timeline
  #: belongs to.
  timeline = db.ReferenceProperty(reference_class=soc.models.timeline.Timeline,
                                 required=True, collection_name="program",
                                 verbose_name=ugettext_lazy('Timeline'))
