#!/usr/bin/env python2.5
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

"""This module contains the User Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.api import users
from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.linkable


class User(soc.models.linkable.Linkable):
  """A user and associated login credentials, the fundamental identity entity.

  User is a separate Model class from Person because the same login 
  ID may be used to, for example, serve as Contributor in one Program 
  and a Reviewer in another.

  Also, this allows a Person to, in the future, re-associate that 
  Person entity with a different Google Account if necessary.

  A User entity participates in the following relationships implemented 
  as a db.ReferenceProperty elsewhere in another db.Model:

   persons)  a 1:many relationship of Person entities identified by the
     User.  This relation is implemented as the 'persons' back-reference
     Query of the Person model 'user' reference.
     
   documents)  a 1:many relationship of Document entities identified by the
     User.  This relation is implemented as the 'user' back-reference
     Query of the Document model 'user' reference.

   groups)  a 1:many relationship of Group entities "founded" by the User.
     This relation is implemented as the 'groups' back-reference Query of
     the Group model 'founder' reference.

   responses)  a 1:many relationship of Reponse entities submitted by the
     User.  This relation is implemented as the 'responses' back-reference
     Query of the Response model 'respondent' reference.
  """

  #: A Google Account, which also provides a "private" email address.
  #: This email address is only used in an automated fashion by 
  #: Melange web applications and is not made visible to other users 
  #: of any Melange application.
  account = db.UserProperty(required=True,
      verbose_name=ugettext('User account'))
  account.help_text = ugettext(
      'A valid Google Account.')

  #: Google Account unique user id
  user_id = db.StringProperty(required=False)

  #: A list (possibly empty) of former Google Accounts associated with
  #: this User.
  former_accounts = db.ListProperty(users.User)

  #: Required field storing publicly-displayed name.  Can be a real name
  #: (though this is not recommended), or a nick name or some other public
  #: alias.  Public names can be any valid UTF-8 text.
  name = db.StringProperty(required=True,
      verbose_name=ugettext('Public name'))
  name.help_text = ugettext(
      'Human-readable name (UTF-8) that will be displayed publicly on the'
      ' site.')
      
  #: field storing whether User is a Developer with site-wide access.
  is_developer = db.BooleanProperty(default=False,
      verbose_name=ugettext('Is Developer'))
  is_developer.help_text = ugettext(
      'Field used to indicate user with site-wide Developer access.')

  #: List of Sponsors that the user is a Host for
  host_for = db.ListProperty(item_type=db.Key, default=[])
  host_for.help_text = ugettext('List of program owners which '
      'the user is a program administrator for.')

  #: field storing the user preference as whether to disable TinyMCE
  disable_tinymce = db.BooleanProperty(default=False,
      verbose_name=ugettext('Disable TinyMCE'))
  disable_tinymce.help_text = ugettext(
      'Disable the TinyMCE editor.')
  disable_tinymce.example_text = ugettext(
      'If ticked, this will disable the TinyMCE editor')

  #: field storing wheter the User has agreed to the site-wide Terms of Service.
  #: (Not a required field because the Terms of Service might not be present
  #: when the first User profile is created when bootstrapping the site.)
  agreed_to_tos = db.BooleanProperty(required=False, default=False,
      verbose_name=ugettext('I Agree to the Terms of Service'))
  agreed_to_tos.help_text = ugettext(
      'Indicates whether the user agreed to the site-wide Terms of Service.')

  #: field storing when the User has agreed to the site-wide Terms of Service.
  #: (Not a required field because the Terms of Service might not be present
  #: when the first User profile is created when bootstrapping the site.)
  agreed_to_tos_on = db.DateTimeProperty(required=False, default=None,
      verbose_name=ugettext('Has agreed to the Terms of Service on'))
  agreed_to_tos_on.help_text = ugettext(
      'Indicates when the user agreed to the site-wide Terms of Service.')

  #: field storing the status of this User.
  #: valid: Is just that, it's a valid User.
  #: invalid: This means that this User has been excluded 
  #:          from using the website.
  status = db.StringProperty(required=True, default='valid',
      choices=['valid', 'invalid'],)
  status.help_text = ugettext(
      'Indicates the status of the User. Invalid means that this account '
      'has been excluded from using the website.')
