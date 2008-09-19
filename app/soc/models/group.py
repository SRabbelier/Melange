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

"""This module contains the Group Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

from soc.models import base
import soc.models.user


class Group(base.ModelWithFieldAttributes):
  """Common data fields for all groups.

  A Group entity participates in the following relationships implemented as
  a db.ReferenceProperty elsewhere in another db.Model:

   school), club), sponsor), org)
     a 1:1 relationship with each entity containing a more specific type of
     Group.  These relationships are represented explicitly in the other
     "group" models by a db.ReferenceProperty named 'group'.  The
     collection_name argument to db.ReferenceProperty should be set to the
     singular of the entity model name of the other "group" class.  The
     above relationship names correspond, respectively to these Models:
       School, Club, Sponsor, Organization
     The relationships listed here are mutually exclusive.  For example,
     a Group cannot be both a School and a Club at the same time.
  """

  #: Required many:1 relationship indicating the founding User of the
  #: Group (this relationship is needed to keep track of lifetime group
  #: creation limits, used to prevent spamming, etc.).
  founder = db.ReferenceProperty(reference_class=soc.models.user.User,
                                 required=True, collection_name="groups")

  #: Required organization name; can only be lower ASCII, not UTF-8
  #: text, because it is used, for example, as part of the shipping
  #: address.
  name = db.StringProperty(required=True)

  #: Optional field used as a display name, such in Group lists displayed
  #: in the web application.  Should be the entire display name in the
  #: format the Group would like it displayed. Display names can be any
  #: valid UTF-8 text.
  displayname = db.StringProperty()

  #: Required email address used as the "public" contact mechanism for
  #: the Group (as opposed to the founder.id email address which is kept
  #: secret, revealed only to Developers).
  email = db.EmailProperty(required=True)

  #: Required home page URL.
  homepage = db.LinkProperty(required=True)

  # TODO(pawel.solyga): merge in the (required) mailing address stuff here...

  # TODO(pawel.solyga): merge in the (optional) shipping address stuff here...

  #: Required contact phone number that will be, amongst other uses,
  #: supplied to shippers along with the shipping address; kept private.
  phone = db.PhoneNumberProperty(required=True)

