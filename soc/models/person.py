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

from soc import models
import soc.models.user


class Person(db.Model):
  """Common data fields for all Roles.

  A Person can only participate in a single Program.  To avoid duplication of
  data entry, facilities will be available for selecting an existing Person
  associated with a particular User to be duplicated for participation in a
  new Program.

  Some details of a Person are considered "public" information, and nearly
  all of these are optional (except for givenname, surname, and email).
  Other details of a Person are kept "private" and are only provided to
  other Persons in roles that "need to know" this information.  How these
  fields are revealed is usually covered by Program terms of service.

  A Person entity participates in a number of relationships:
     
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
                              required=True, 
                              collection_name="persons")

  #====================================================================
  #  (public) name information
  #====================================================================

  #: Required field storing the parts of the Person's name
  #: corresponding to the field names; displayed publicly.
  #: Givenname can only be lower ASCII, not UTF-8 text, because it is
  #: used, for example, as part of the shipping (mailing) address. 
  givenname = db.StringProperty(required=True)

  #: Required field storing the parts of the Person's name 
  #: corresponding to the field names; displayed publicly.
  #: Surname can only be lower ASCII, not UTF-8 text, because it is
  #: used, for example, as part of the shipping (mailing) address. 
  surname = db.StringProperty(required=True)  # last name

  #: Optional field storing a nickname; displayed publicly.
  #: Nicknames can be any valid UTF-8 text. 
  nickname = db.StringProperty()
  
  #: optional field used as a display name, such as for awards
  #: certificates. Should be the entire display name in the format 
  #: the Person would like it displayed (could be surname followed by
  #: given name in some cultures, for example). Display names can be
  #: any valid UTF-8 text.
  displayname = db.StringProperty() 

  #====================================================================
  #  (public) contact information
  #====================================================================

  #: Required field used as the "public" contact mechanism for the
  #: Person (as opposed to the user.id email address which is
  #: kept secret).
  email = db.EmailProperty(required=True)

  #: Optional field storing Instant Messaging network contact
  #: information; displayed publicly.
  im = db.IMProperty()

  #: Optional field storing a home page URL; displayed publicly.
  homepage = db.LinkProperty()

  #: Optional field storing a blog URL; displayed publicly.
  blog = db.LinkProperty()

  #: Optional field storing a URL to an image, expected to be a
  #: personal photo (or cartoon avatar, perhaps); displayed publicly.
  photo = db.LinkProperty()

  #: Optional field storing the latitude and longitude provided by
  #: the Person; displayed publicly.
  location = db.GeoPtProperty()

  #====================================================================
  # (private) contact information
  #====================================================================

  #: Required field containing residence address; kept private.
  residence = db.PostalAddressProperty(required=True)

  #: Optional field containg a separate shipping; kept private.
  shipping = db.PostalAddressProperty()

  #: Required field containing a phone number that will be supplied
  #: to shippers; kept private.
  phone = db.PhoneNumberProperty(required=True) 
  
  #====================================================================
  # (private) personal information
  #====================================================================

  #: Required field containing the Person's birthdate (for 
  #: determining Program participation eligibility); kept private.
  birthdate = db.DateProperty(required=True)

  #: Optional field indicating choice of t-shirt, from XXS to XXXL; 
  #: kept private.
  tshirtsize = db.StringProperty(
      choices=set(("XXS", "XS", "S", "M", "L", "XL", "XXL", "XXXL")))

  #: Optional field indicating choice of male or t-shirt
  #: fit; kept private.
  tshirt_gender = db.StringProperty(choices=set(("male", "female")))

