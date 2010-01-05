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

"""This module contains the GSoC specific Organization Model.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from taggable.taggable import Tag
from taggable.taggable import Taggable
from taggable.taggable import tag_property

import soc.models.organization


class OrgTag(Tag):
  """Model for storing all Organization tags.
  """

  pass


class GSoCOrganization(Taggable, soc.models.organization.Organization):
  """GSoC Organization model extends the basic Organization model.
  """

  slots = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots allocated'))
  slots.help_text = ugettext(
      'The amount of slots allocated to this organization.')

  slots_desired = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots desired'))
  slots_desired.help_text = ugettext(
      'The amount of slots desired by this organization.')

  slots_calculated = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots calculated'))
  slots_calculated.help_text = ugettext(
      'The amount of slots calculated for this organization.')

  nr_applications = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Amount of applications received'))
  nr_applications.help_text = ugettext(
      'The amount of applications received by this organization.')

  nr_mentors = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Amount of mentors assigned'))
  nr_mentors.help_text = ugettext(
      'The amount of mentors assigned to a proposal by this organization.')

  org_tag = tag_property('org_tag')

  def __init__(self, parent=None, key_name=None, app=None, **entity_values):
    """Constructor for GSoCOrganization Model.

    Args:
        See Google App Engine APIs.
    """

    db.Model.__init__(self, parent, key_name, app, **entity_values)

    Taggable.__init__(self, org_tag=OrgTag)
