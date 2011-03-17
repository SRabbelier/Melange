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

  predefined = db.BooleanProperty(required=True, default=False)

  def __init__(self, *args, **kwds):
    """Initialization function.
    """

    Tag.__init__(self, *args, **kwds)
    if not self.predefined:
      self.auto_delete = True

  @classmethod
  def get_or_create(cls, scope, tag_name, predefined=False):
    """Get the Tag object that has the tag value given by tag_value.
    """

    tag_key_name = cls._key_name(scope.key().name(), tag_name)
    existing_tag = cls.get_by_key_name(tag_key_name)
    if existing_tag is None:
      # the tag does not yet exist, so create it.
      def create_tag_txn():
        new_tag = cls(key_name=tag_key_name, tag=tag_name, scope=scope,
            predefined=predefined)
        new_tag.put()
        return new_tag
      existing_tag = db.run_in_transaction(create_tag_txn)
    else:
      # the tag exists, but if predefined argument is True, let us make sure
      # that its value in the store is updated
      if predefined and not existing_tag.predefined:
        existing_tag.predefined = True
        existing_tag.put()
    return existing_tag

  @classmethod
  def get_predefined_for_scope(cls, scope):
    """Get a list of predefined tag objects that has a given scope.
    """

    return db.Query(cls).filter('scope = ', scope).filter(
        'predefined = ', True).fetch(1000)


class GSoCOrganization(Taggable, soc.models.organization.Organization):
  """GSoC Organization model extends the basic Organization model.
  """

  contrib_template = db.TextProperty(required=False, verbose_name=ugettext(
      'Application template'))
  contrib_template.help_text = ugettext(
      'This template can be used by contributors, such as students'
      ' and other non-member participants, when they apply to contribute'
      ' to the organization.')
  contrib_template.group = ugettext("1. Public Info")

  slots = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots allocated'))
  slots.help_text = ugettext(
      'The amount of slots allocated to this organization.')

  slots_desired = db.IntegerProperty(required=False, default=0,
      verbose_name=ugettext('Slots desired'))
  slots_desired.help_text = ugettext(
      'The amount of slots desired by this organization.')
  slots_desired.group = ugettext("4. Organization Preferences")

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

  scoring_disabled = db.BooleanProperty(required=False, default=False)
  scoring_disabled.help_text = ugettext(
      'Check this field if you want to disable private reviews for '
      'student proposals which have been sent to your organization.')
  scoring_disabled.group = ugettext("4. Organization Preferences")

  facebook = db.LinkProperty(
      required=False, verbose_name=ugettext("Facebook URL"))
  facebook.help_text = ugettext("URL of the Facebook page of your Organization")
  facebook.group = ugettext("1. Public Info")

  twitter = db.LinkProperty(
      required=False, verbose_name=ugettext("Twitter URL"))
  twitter.help_text = ugettext("URL of the Twitter profile of your Organization")
  twitter.group = ugettext("1. Public Info")

  blog = db.LinkProperty(
      required=False, verbose_name=ugettext("Blog URL"))
  blog.help_text = ugettext("URL of the Blog of your Organization")
  blog.group = ugettext("1. Public Info")

  org_tag = tag_property('org_tag')

  def __init__(self, parent=None, key_name=None, app=None, **entity_values):
    """Constructor for GSoCOrganization Model.

    Args:
        See Google App Engine APIs.
    """

    db.Model.__init__(self, parent, key_name, app, **entity_values)

    Taggable.__init__(self, org_tag=OrgTag)
