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

"""This module contains the Work Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]


import polymodel

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.user


class Work(polymodel.PolyModel):
  """Model of a Work created by one or more Persons in Roles.

  Work is a "base entity" of other more specific "works" created by Persons
  serving in "roles".

    reviews)  a 1:many relationship between a Work and the zero or more
      Reviews of that Work.  This relation is implemented as the 'reviews'
      back-reference Query of the Review model 'reviewed' reference.
  """

  #: Required 1:1 relationship indicating the User who initially authored the
  #: Work (this relationship is needed to keep track of lifetime document
  #: creation limits, used to prevent spamming, etc.).
  author = db.ReferenceProperty(reference_class=soc.models.user.User,
                                 required=True, collection_name="documents",
                                 verbose_name=ugettext_lazy('Created by'))

  #: Required field indicating the "title" of the work, which may have
  #: different uses depending on the specific type of the work. Works
  #: can be indexed, filtered, and sorted by 'title'.
  title = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Title'))
  title.help_text = ugettext_lazy(
      'title of the document; often used in the window title')

  #: Required path, prepended to a "link name" to form the document URL.
  #: The combined path and link name must be globally unique on the
  #: site.  Except in /site/document (Developer) forms, this field is not
  #: usually directly editable by the User, but is instead set by controller
  #: logic to match the "scope" of the document.
  partial_path = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Partial path'))
  partial_path.help_text = ugettext_lazy(
    'path portion of URLs, prepended to link name')

  #: Required link name, appended to a "path" to form the document URL.
  #: The combined path and link name must be globally unique on the
  #: site (but, unlike some link names, a Work link name can be reused,
  #: as long as the combination with the preceding path is unique).
  link_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Link name'))
  link_name.help_text = ugettext_lazy('link name used in URLs')

  #: short name used in places such as the sidebar menu and breadcrumb trail
  #: (optional: title will be used if short_name is not present)
  short_name = db.StringProperty(verbose_name=ugettext_lazy('Short name'))
  short_name.help_text = ugettext_lazy(
      'short name used, for example, in the sidebar menu')

  #: Required db.TextProperty containing the contents of the Work.
  #: The content is only to be displayed to Persons in Roles eligible to
  #: view them (which may be anyone, for example, with the site front page).
  content = db.TextProperty(verbose_name=ugettext_lazy('Content'))
  
  #: date when the work was created
  created = db.DateTimeProperty(auto_now_add=True)
  
  #: date when the work was last modified
  modified = db.DateTimeProperty(auto_now=True)

  # TODO: some sort of access control preferences are needed at this basic
  #   level.  Works need to be restrict-able to:
  #    * the authors only
  #    * the administrators of the Groups that the authors are in
  #    * any member of the authors' Groups
  #    * logged-in User with a profile
  #    * logged-in Users, but no profile is necessary
  #    * anyone, even those not logged in
  #  (and possibly others)

  #: field storing whether a link to the Work should be featured in
  #: the sidebar menu (and possibly elsewhere); FAQs, Terms of Service,
  #: and the like are examples of "featured" Works
  is_featured = db.BooleanProperty(
      verbose_name=ugettext_lazy('Is Featured'))
  is_featured.help_text = ugettext_lazy(
      'Field used to indicate if a Work should be featured, for example,'
      ' in the sidebar menu.')
