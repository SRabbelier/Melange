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

"""This module contains the Role Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.models import countries

import soc.models.linkable
import soc.models.user


class Role(soc.models.linkable.Linkable):
  """Information common to Program participation for all Roles.

  Some details of a Role are considered "public" information, and nearly
  all of these are optional (except for given_name, surname, and email).
  Other details of a Role are kept "private" and are only provided to
  other Users in roles that "need to know" this information.  How these
  fields are revealed is usually covered by Program terms of service.

  Role is the entity that is created when a User actually participates
  in some fashion in a Program. Role details could *possibly* be collected
  without actual participation (voluntary, opt-in, of course).

  A Role is a User's participation in a single Program.  To avoid
  duplication of data entry, facilities will be available for selecting
  an existing Role associated with a particular User to be duplicated for
  participation in a new Program.

  A User has to have at least one Role in order to be able to create
  any Work (such as a Document) on the site.  The easiest-to-obtain Role is
  probably Club Member (though Clubs can set their own membership criteria).

  A Role entity participates in the following relationships implemented
  as a db.ReferenceProperty elsewhere in another db.Model:

   documentation) a 1:many relationship of Documentation (tax forms,
     letters from schools, etc.) associated with the Role by Hosts.  This
     relation is implemented as the 'documentation' back-reference Query of
     the Documentation model 'role' reference.

   works) a many:many relationship with Works, stored in a separate
     WorksRoles model, representing the Work authored by this Role.
     See the WorksRoles model class for details.
  """

  #: A required many:1 relationship that ties (possibly multiple
  #: entities of) Role details to a unique User. A Role cannot
  #: exist unassociated from a login identity and credentials. The
  #: back-reference in the User model is a Query named 'roles'.
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name='roles')


  #====================================================================
  #  (public) name information
  #====================================================================

  #: Required field storing the parts of the Role's name
  #: corresponding to the field names; displayed publicly.
  #: given_name can only be lower ASCII, not UTF-8 text, because it is
  #: used, for example, as part of the shipping (mailing) address.
  given_name = db.StringProperty(required=True,
      verbose_name=ugettext('First (given) name'))
  given_name.help_text = ugettext('lower ASCII characters only')
  given_name.group = ugettext("1. Public Info")

  #: Required field storing the parts of the Role's name
  #: corresponding to the field names; displayed publicly.
  #: Surname can only be lower ASCII, not UTF-8 text, because it is
  #: used, for example, as part of the shipping (mailing) address.
  surname = db.StringProperty(
      required=True,
      verbose_name=ugettext('Last (family) name'))
  surname.help_text = ugettext('lower ASCII characters only')
  surname.group = ugettext("1. Public Info")

  #: Optional field used as a display name, such as for awards
  #: certificates. Should be the entire name in the format
  #: the Role would like it displayed (could be surname followed by
  #: given name in some cultures, for example). Display names can be
  #: any valid UTF-8 text.
  name_on_documents = db.StringProperty(
      verbose_name=ugettext('Name on documents'))
  name_on_documents.help_text = ugettext(
      'Optional field used as a display name, such as for documents like '
      'awards certificates. Should be the entire name in the format '
      'the person would like it displayed (could be family name followed '
      'by given name in some cultures, for example). Name on documents can be '
      'any valid UTF-8 text.')
  name_on_documents.group = ugettext("1. Public Info")

  #====================================================================
  #  (public) contact information
  #====================================================================

  #: Required field used as the 'public' contact mechanism for the
  #: Role (as opposed to the user.account email address which is
  #: kept secret).
  email = db.EmailProperty(
      required=True,
      verbose_name=ugettext('Email Address'))
  email.group = ugettext("1. Public Info")

  #: Optional field storing Instant Messaging network; displayed publicly.
  im_network = db.StringProperty(
      verbose_name=ugettext('IM Network'))
  im_network.help_text = ugettext(
      'examples: irc:irc.freenode.net xmpp:gmail.com/Home')
  im_network.group = ugettext("1. Public Info")

  #: Optional field storing Instant Messaging handle; displayed publicly.
  im_handle = db.StringProperty(
      verbose_name=ugettext('IM Handle'))
  im_handle.help_text = ugettext(
      'personal identifier, such as: screen name, IRC nick, user name')
  im_handle.group = ugettext("1. Public Info")

  #: Optional field storing a home page URL; displayed publicly.
  home_page = db.LinkProperty(
      verbose_name=ugettext('Home Page URL'))
  home_page.group = ugettext("1. Public Info")

  #: Optional field storing a blog URL; displayed publicly.
  blog = db.LinkProperty(
      verbose_name=ugettext('Blog URL'))
  blog.group = ugettext("1. Public Info")

  #: Optional field storing a URL to an image, expected to be a
  #: personal photo (or cartoon avatar, perhaps); displayed publicly.
  photo_url = db.LinkProperty(
      verbose_name=ugettext('Thumbnail Photo URL'))
  photo_url.help_text = ugettext(
      'URL of 64x64 pixel thumbnail image')
  photo_url.group = ugettext("1. Public Info")

  #: Optional field storing the latitude provided by the Role; displayed
  #: publicly.
  latitude = db.FloatProperty(
      verbose_name=ugettext('Latitude'))
  latitude.help_text = ugettext(
      'decimal degrees northerly (N), use minus sign (-) for southerly (S)')
  latitude.group = ugettext("1. Public Info")

  #: Optional field storing the longitude provided by the Role; displayed
  #: publicly.
  longitude = db.FloatProperty(
      verbose_name=ugettext('Longitude'))
  longitude.help_text = ugettext(
      'decimal degrees easterly (E), use minus sign (-) for westerly (W)')
  longitude.group = ugettext("1. Public Info")

  #====================================================================
  # (private) contact information
  #====================================================================

  #: Required field containing residence street address; kept private.
  #: Residence street address can only be lower ASCII, not UTF-8 text, because
  #: it may be used as a shipping address.
  res_street = db.StringProperty(required=True,
      verbose_name=ugettext('Street address'))
  res_street.help_text = ugettext(
      'street number and name, lower ASCII characters only')
  res_street.group = ugettext("2. Contact Info (Private)")

  #: Required field containing residence address city; kept private.
  #: Residence city can only be lower ASCII, not UTF-8 text, because it
  #: may be used as a shipping address.
  res_city = db.StringProperty(required=True,
      verbose_name=ugettext('City'))
  res_city.help_text = ugettext('lower ASCII characters only')
  res_city.group = ugettext("2. Contact Info (Private)")

  #: Optional field containing residence address state or province; kept
  #: private.  Residence state/province can only be lower ASCII, not UTF-8
  #: text, because it may be used as a shipping address.
  res_state = db.StringProperty(
      verbose_name=ugettext('State/Province'))
  res_state.help_text = ugettext(
      'optional if country/territory does not have states or provinces, '
      'lower ASCII characters only')
  res_state.group = ugettext("2. Contact Info (Private)")

  #: Required field containing residence address country or territory; kept
  #: private.
  res_country = db.StringProperty(required=True,
      verbose_name=ugettext('Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)
  res_country.group = ugettext("2. Contact Info (Private)")

  #: Required field containing residence address postal code (ZIP code in
  #: the United States); kept private.  Residence postal code can only be
  #: lower ASCII, not UTF-8 text, because it may be used as a shipping address.
  res_postalcode = db.StringProperty(required=True,
      verbose_name=ugettext('ZIP/Postal Code'))
  res_postalcode.help_text = ugettext('lower ASCII characters only')
  res_postalcode.group = ugettext("2. Contact Info (Private)")

  #: Required field containing a phone number that will be used to
  #: contact the user, also supplied to shippers; kept private.
  phone = db.PhoneNumberProperty(
      required=True,
      verbose_name=ugettext('Phone Number'))
  phone.help_text = ugettext(
      'include complete international calling number with country code')
  phone.example_text = ugettext(
      "e.g. 1650253000 for Google's Corp HQ number in the United States")
  phone.group = ugettext("2. Contact Info (Private)")

  #: field storing whether the User has agreed to publish his location
  publish_location = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('Publish my location'))
  publish_location.help_text = ugettext(
      'Indicates whether the user agreed to publish location.')
  publish_location.group = ugettext("2. Contact Info (Private)")

  #: Optional field containing a separate shipping street address; kept
  #: private.  If shipping address is not present in its entirety, the
  #: residence address will be used instead.  Shipping street address can only
  #: be lower ASCII, not UTF-8 text, because, if supplied, it is used as a
  #: shipping address.
  ship_street = db.StringProperty(
      verbose_name=ugettext('Shipping Street address'))
  ship_street.help_text = ugettext(
      'street number and name, lower ASCII characters only, '
      'fill in only if not same as above')
  ship_street.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing shipping address city; kept private.
  #: Shipping city can only be lower ASCII, not UTF-8 text, because, if
  #: supplied, it is used as a shipping address.
  ship_city = db.StringProperty(
      verbose_name=ugettext('Shipping City'))
  ship_city.help_text = ugettext('lower ASCII characters only'
                                 'fill in only if not same as above')
  ship_city.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing shipping address state or province; kept
  #: private.  Shipping state/province can only be lower ASCII, not UTF-8
  #: text, because, if supplied, it is used as a shipping address.
  ship_state = db.StringProperty(
      verbose_name=ugettext('Shipping State/Province'))
  ship_state.help_text = ugettext(
      'optional if country/territory does not have states or provinces, '
      'lower ASCII characters only, fill in only if not same as above')
  ship_state.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing shipping address country or territory; kept
  #: private.
  ship_country = db.StringProperty(
      verbose_name=ugettext('Shipping Country/Territory'),
      choices=countries.COUNTRIES_AND_TERRITORIES)
  ship_country.help_text = ugettext('fill in only if not same as above')
  ship_country.group = ugettext("3. Shipping Info (Private and Optional)")

  #: Optional field containing shipping address postal code (ZIP code in
  #: the United States); kept private.  Shipping postal code can only be
  #: lower ASCII, not UTF-8 text, because, if supplied, it is used as a
  #: shipping address.
  ship_postalcode = db.StringProperty(
      verbose_name=ugettext('Shipping ZIP/Postal Code'))
  ship_postalcode.help_text = ugettext('lower ASCII characters only'
                                       'fill in only if not same as above')
  ship_postalcode.group = ugettext("3. Shipping Info (Private and Optional)")
  

  #====================================================================
  # (private) personal information
  #====================================================================

  #: Required field containing the Role's birthdate (for
  #: determining Program participation eligibility); kept private.
  birth_date = db.DateProperty(
      required=True,
      verbose_name=ugettext('Birth Date'))
  birth_date.help_text = ugettext(
      'required for determining program eligibility')
  birth_date.group = ugettext("4. Private Info")
  birth_date.example_text = ugettext(
      'e.g. 1999-12-31 or 12/31/1999')

  #: Optional field indicating choice of t-shirt, from XXS to XXXL;
  #: kept private.
  tshirt_size = db.StringProperty(
      verbose_name=ugettext('T-shirt Size'),
      choices=('XXS', 'XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'))
  tshirt_size.group = ugettext("4. Private Info")
  tshirt_size.example_text = ugettext('See also '
      '<a href="http://en.wikipedia.org/wiki/US_standard_clothing_size">'
      'this article</a>.')

  #: Optional field indicating choice of t-shirt fit; kept private.
  tshirt_style = db.StringProperty(
      verbose_name=ugettext('T-shirt Style'),
      choices=('male', 'female'))
  tshirt_style.group = ugettext("4. Private Info")

  #: field storing wheter the User has agreed to the site-wide Terms of Service.
  #: (Not a required field because the Terms of Service might not be present
  #: when the first User profile is created when bootstrapping the site.)
  agreed_to_tos = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('I Agree to the Terms of Service'))
  agreed_to_tos.help_text = ugettext(
      'Indicates whether the user agreed to this role Terms of Service.')
  agreed_to_tos.group = ugettext("99. Terms of Service")

  #: field storing when the User has agreed to the site-wide Terms of Service.
  #: (Not a required field because the Terms of Service might not be present
  #: when the first User profile is created when bootstrapping the site.)
  agreed_to_tos_on = db.DateTimeProperty(required=False, default=None,
      verbose_name=ugettext('Has agreed to the Terms of Service on'))
  agreed_to_tos_on.help_text = ugettext(
      'Indicates when the user agreed to this role Terms of Service.')
  agreed_to_tos.group = ugettext("99. Terms of Service")

  #: field storing the status of this role
  #: Active means that this role can exercise all it's privileges.
  #: Invalid mean that this role cannot exercise it's privileges.
  #: Inactive means that this role cannot exercise it's data-editing
  #: privileges but should be able to see the data. For instance when a program
  #: has been marked inactive an Organization Admin should still be able to see
  #: the student applications.
  status = db.StringProperty(default='active',
      choices=['active','invalid','inactive'],
      verbose_name=ugettext('Status of this Role'))
  status.help_text = ugettext('Indicates the status of the role '
      'concerning which privileges may be used.')

  def name(self):
    """Property as 'name' for use in common templates.
    """
    return '%s %s' %(self.given_name, self.surname)

  def document_name(self):
    """Property as 'document_name' used on for example award certificates.
    """
    if self.name_on_documents:
      return self.name_on_documents
    else:
      return self.name()
