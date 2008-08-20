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

"""This module contains the User Model."""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]

from google.appengine.ext import db
from django.utils.translation import ugettext_lazy


class User(db.Model):
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

  """

  #: A Google Account, which also provides a "private" email address.
  #: This email address is only used in an automated fashion by 
  #: Melange web applications and is not made visible to other users 
  #: of any Melange application.
  id = db.UserProperty(required=True)

  #: Required field storing a nickname; displayed publicly.
  #: Nicknames can be any valid UTF-8 text.
  nick_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Nick name'))
      
  #: Required field storing linkname used in URLs to identify user.
  #: Lower ASCII characters only.
  link_name = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Link name'))
  link_name.help_text = ugettext_lazy(
      'Field used in URLs to identify user. '
      'Lower ASCII characters only.')

  @staticmethod
  def doesUserExist(user=None):
    """Returns if user already exists in the Datastore.
    
    Args:
      user: a Google Account object,
    """
    #: let's do a gql query and check if user exists in datastore
    data = self.getUser(user)
    if data:
      return True
    else:
      return False

  @staticmethod
  def getUser(user=None):
    """Returns User entity from datastore, or None if not found.  
    
    Args:
      user: a Google Account object,
    """
    return User.gql('WHERE id = :1', user).get()

  @staticmethod
  def getUserForLinkname(link_name=None):
    """Returns User entity for linkname or None if not found.
    
    Args:
      link_name: linkname used in URLs to identify user,
    """
    return User.gql('WHERE link_name = :1', link_name).get()
    