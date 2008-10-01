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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.ext import db

import polymodel

from django.utils.translation import ugettext_lazy

from soc.models import countries
import soc.models.user

class Group(polymodel.PolyModel):
  """Common data fields for all groups.
  """

  #: Required field storing name of the group.
  name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Name'))
  name.help_text = ugettext_lazy('Complete, formal name of the group.')  
  
  #: Required field storing linkname used in URLs to identify group.
  #: Lower ASCII characters only.
  link_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Link name'))
  link_name.help_text = ugettext_lazy(
      'Field used in URLs to identify group. '
      'Lower ASCII characters only.')
  
  #: Required field storing short name of the group.
  #: It can be used for displaying group as sidebar menu item.
  short_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Short name'))
  short_name.help_text = ugettext_lazy('Short name used for sidebar menu')

  #: Required many:1 relationship indicating the founding User of the
  #: Group (this relationship is needed to keep track of lifetime group
  #: creation limits, used to prevent spamming, etc.).
  founder = db.ReferenceProperty(reference_class=soc.models.user.User,
                                 required=True, collection_name="groups")  
  #: Optional field storing a home page URL of the group.
  home_page = db.LinkProperty(required=True,
      verbose_name=ugettext_lazy('Home Page URL'))
  
  #: Optional email address used as the "public" contact mechanism for
  #: the Group (as opposed to the founder.id email address which is kept
  #: secret, revealed only to Developers).
  email = db.EmailProperty(required=True,
      verbose_name=ugettext_lazy('Email'))  
  
  #: Optional field storing description of the group.
  description = db.TextProperty(required=True,
      verbose_name=ugettext_lazy('Description'))
      
  #: Optional field containing a group street address.
  #: Group street address can only be lower ASCII, not UTF-8 text, 
  #: because, if supplied, it is used as a shipping address.
  street = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Street address'))
  street.help_text = ugettext_lazy(
      'street number and name, lower ASCII characters only')

  #: Optional field containing group address city.
  #: City can only be lower ASCII, not UTF-8 text, because, if
  #: supplied, it is used as a shipping address.
  city = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('City'))
  city.help_text = ugettext_lazy('lower ASCII characters only')

  #: Optional field containing group address state or province.
  #: Group state/province can only be lower ASCII, not UTF-8
  #: text, because, if supplied, it is used as a shipping address.
  state = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('State/Province'))
  state.help_text = ugettext_lazy(
      'optional if country/territory does not have states or provinces, '
      'lower ASCII characters only')

  #: Optional field containing address country or territory of the group.
  country = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)

  #: Optional field containing address postal code of the group (ZIP code in
  #: the United States). Postal code can only be lower ASCII, not UTF-8 
  #: text, because, if supplied, it is used as a shipping address.
  postalcode = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('ZIP/Postal Code'))
  postalcode.help_text=ugettext_lazy('lower ASCII characters only')

  #: Optional contact phone number that will be, amongst other uses,
  #: supplied to shippers along with the shipping address; kept private.
  phone = db.PhoneNumberProperty(required=True,
      verbose_name=ugettext_lazy('Phone Number'))
  phone.help_text = ugettext_lazy(
      'include complete international calling number with country code')
