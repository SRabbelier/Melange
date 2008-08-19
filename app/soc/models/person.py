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

"""This module contains the Person Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
]

from google.appengine.ext import db
from django.utils.translation import ugettext_lazy

from soc import models
import soc.models.user

from soc.models import countries


class Person(db.Model):
  """Common data fields for all Roles.

  A Person can only participate in a single Program.  To avoid duplication of
  data entry, facilities will be available for selecting an existing Person
  associated with a particular User to be duplicated for participation in a
  new Program.

  Some details of a Person are considered "public" information, and nearly
  all of these are optional (except for given_name, surname, and email).
  Other details of a Person are kept "private" and are only provided to
  other Persons in roles that "need to know" this information.  How these
  fields are revealed is usually covered by Program terms of service.

  A Person entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   author)  a 1:1 relationship of Person details for a specific Author.
     This relation is implemented as the 'author' back-reference Query of
     the Author model 'person' reference.

   docs)  a 1:many relationship of documents (Documentation) associated
     with the Person by Administrators.  This relation is implemented as
     the 'docs' back-reference Query of the Documentation model 'person'
     reference.
  """

  #: A required many:1 relationship that ties (possibly multiple
  #: entities of) Person details to a unique User.  A Person cannot
  #: exist unassociated from a login identity and credentials.  The
  #: back-reference in the User model is a Query named 'persons'.
  user = db.ReferenceProperty(reference_class=models.user.User,
                              required=True, collection_name='persons')

  #====================================================================
  #  (public) name information
  #====================================================================

  #: Required field storing the parts of the Person's name
  #: corresponding to the field names; displayed publicly.
  #: given_name can only be lower ASCII, not UTF-8 text, because it is
  #: used, for example, as part of the shipping (mailing) address.
  given_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('First (given) name'))
  given_name.help_text = ugettext_lazy('lower ASCII characters only')

  #: Required field storing the parts of the Person's name
  #: corresponding to the field names; displayed publicly.
  #: Surname can only be lower ASCII, not UTF-8 text, because it is
  #: used, for example, as part of the shipping (mailing) address.
  surname = db.StringProperty(
      required=True,
      verbose_name=ugettext_lazy('Last (family) name'))
  surname.help_text = ugettext_lazy('lower ASCII characters only')

  #: Optional field used as a display name, such as for awards
  #: certificates. Should be the entire display name in the format
  #: the Person would like it displayed (could be surname followed by
  #: given name in some cultures, for example). Display names can be
  #: any valid UTF-8 text.
  display_name = db.StringProperty(
      verbose_name=ugettext_lazy('Display Name'))
  display_name.help_text = ugettext_lazy(
      'Optional field used as a display name, such as for awards '
      'certificates. Should be the entire display name in the format '
      'the person would like it displayed (could be family name followed '
      'by given name in some cultures, for example). Display names can be '
      'any valid UTF-8 text.')

  #====================================================================
  #  (public) contact information
  #====================================================================

  #: Required field used as the 'public' contact mechanism for the
  #: Person (as opposed to the user.id email address which is
  #: kept secret).
  email = db.EmailProperty(
      required=True,
      verbose_name=ugettext_lazy('Email Address'))

  #: Optional field storing Instant Messaging network; displayed publicly.
  im_network = db.StringProperty(
      verbose_name=ugettext_lazy('IM Network'))
  im_network.help_text=ugettext_lazy(
      'examples: irc:irc.freenode.org xmpp:gmail.com/Home')

  #: Optional field storing Instant Messaging handle; displayed publicly.
  im_handle = db.StringProperty(
      verbose_name=ugettext_lazy('IM Handle'))
  im_handle.help_text=ugettext_lazy(
      'personal identifier, such as: screen name, IRC nick, user name')

  #: Optional field storing a home page URL; displayed publicly.
  home_page = db.LinkProperty(
      verbose_name=ugettext_lazy('Home Page URL'))

  #: Optional field storing a blog URL; displayed publicly.
  blog = db.LinkProperty(
      verbose_name=ugettext_lazy('Blog URL'))

  #: Optional field storing a URL to an image, expected to be a
  #: personal photo (or cartoon avatar, perhaps); displayed publicly.
  photo_url = db.LinkProperty(
      verbose_name=ugettext_lazy('Thumbnail Photo URL'))
  photo_url.help_text = ugettext_lazy(
      'URL of 64x64 pixel thumbnail image')

  #: Optional field storing the latitude provided by the Person; displayed
  #: publicly.
  latitude = db.FloatProperty(
      verbose_name=ugettext_lazy('Latitude'))
  latitude.help_text = ugettext_lazy(
      'decimal degrees northerly (N), use minus sign (-) for southerly (S)')

  #: Optional field storing the longitude provided by the Person; displayed
  #: publicly.
  longitude = db.FloatProperty(
      verbose_name=ugettext_lazy('Longitude'))
  longitude.help_text = ugettext_lazy(
      'decimal degrees easterly (E), use minus sign (-) for westerly (W)')

  #====================================================================
  # (private) contact information
  #====================================================================

  #: Required field containing residence street address; kept private.
  #: Residence street address can only be lower ASCII, not UTF-8 text, because
  #: it may be used as a shipping address.
  res_street = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Street address'))
  res_street.help_text = ugettext_lazy(
      'street number and name, lower ASCII characters only')

  #: Required field containing residence address city; kept private.
  #: Residence city can only be lower ASCII, not UTF-8 text, because it
  #: may be used as a shipping address.
  res_city = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('City'))
  res_city.help_text = ugettext_lazy('lower ASCII characters only')

  #: Required field containing residence address state or province; kept
  #: private.  Residence state/province can only be lower ASCII, not UTF-8
  #: text, because it may be used as a shipping address.
  res_state = db.StringProperty(
      verbose_name=ugettext_lazy('State/Province'))
  res_state.help_text = ugettext_lazy(
      'optional if country/territory does not have states or provinces, '
      'lower ASCII characters only')

  #: Required field containing residence address country or territory; kept
  #: private.
  res_country = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)

  #: Required field containing residence address postal code (ZIP code in
  #: the United States); kept private.  Residence postal code can only be
  #: lower ASCII, not UTF-8 text, because it may be used as a shipping address.
  res_postalcode = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('ZIP/Postal Code'))
  res_postalcode.help_text=ugettext_lazy('lower ASCII characters only')

  #: Optional field containing a separate shipping street address; kept
  #: private.  If shipping address is not present in its entirety, the
  #: residence address will be used instead.  Shipping street address can only
  #: be lower ASCII, not UTF-8 text, because, if supplied, it is used as a
  #: shipping address.
  ship_street = db.StringProperty(
      verbose_name=ugettext_lazy('Street address'))
  ship_street.help_text = ugettext_lazy(
      'street number and name, lower ASCII characters only')

  #: Optional field containing shipping address city; kept private.
  #: Shipping city can only be lower ASCII, not UTF-8 text, because, if
  #: supplied, it is used as a shipping address.
  ship_city = db.StringProperty(
      verbose_name=ugettext_lazy('City'))
  ship_city.help_text = ugettext_lazy('lower ASCII characters only')

  #: Optional field containing shipping address state or province; kept
  #: private.  Shipping state/province can only be lower ASCII, not UTF-8
  #: text, because, if supplied, it is used as a shipping address.
  ship_state = db.StringProperty(
      verbose_name=ugettext_lazy('State/Province'))
  ship_state.help_text = ugettext_lazy(
      'optional if country/territory does not have states or provinces, '
      'lower ASCII characters only')

  #: Optional field containing shipping address country or territory; kept
  #: private.
  ship_country = db.StringProperty(
      verbose_name=ugettext_lazy('Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)

  #: Optional field containing shipping address postal code (ZIP code in
  #: the United States); kept private.  Shipping postal code can only be
  #: lower ASCII, not UTF-8 text, because, if supplied, it is used as a
  #: shipping address.
  ship_postalcode = db.StringProperty(
      verbose_name=ugettext_lazy('ZIP/Postal Code'))
  ship_postalcode.help_text=ugettext_lazy('lower ASCII characters only')

  #: Required field containing a phone number that will be supplied
  #: to shippers; kept private.
  phone = db.PhoneNumberProperty(
      required=True,
      verbose_name=ugettext_lazy('Phone Number'))
  phone.help_text = ugettext_lazy(
      'include complete international calling number with country code')

  #====================================================================
  # (private) personal information
  #====================================================================

  #: Required field containing the Person's birthdate (for
  #: determining Program participation eligibility); kept private.
  birth_date = db.DateProperty(
      required=True,
      verbose_name=ugettext_lazy('Birth Date'))
  birth_date.help_text = ugettext_lazy(
      'required for determining program eligibility')

  #: Optional field indicating choice of t-shirt, from XXS to XXXL;
  #: kept private.
  tshirt_size = db.StringProperty(
      verbose_name=ugettext_lazy('T-shirt Size'),
      choices=('XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'))

  #: Optional field indicating choice of t-shirt fit; kept private.
  tshirt_style = db.StringProperty(
      verbose_name=ugettext_lazy('T-shirt Style'),
      choices=('male', 'female'))
