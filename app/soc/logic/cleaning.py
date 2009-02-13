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

"""Generic cleaning methods.
"""

__authors__ = [
    '"Todd Larsen" <tlarsen@google.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    ]


from google.appengine.api import users

from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext

from soc.logic import validate
from soc.logic.models import site as site_logic
from soc.logic.models import user as user_logic


DEF_LINK_ID_IN_USE_MSG = ugettext(
    'This link ID is already in use, please specify another one')


def check_field_is_empty(field_name):
  """Returns decorator that bypasses cleaning for empty fields.
  """

  def decorator(fun):
    """Decorator that checks if a field is empty if so doesn't do the cleaning.

    Note Django will capture errors concerning required fields that are empty.
    """
    from functools import wraps

    @wraps(fun)
    def wrapper(self):
      field_content = self.cleaned_data.get(field_name)

      if not field_content:
        # field has no content so bail out
        return None
      else:
        # field has contents
        return fun(self)
    return wrapper

  return decorator


def clean_link_id(field_name):
  """Checks if the field_name value is in a valid link ID format.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    # convert to lowercase for user comfort
    link_id = self.cleaned_data.get(field_name).lower()
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
    return link_id
  return wrapper


def clean_scope_path(field_name):
  """Checks if the field_name value is in a valid scope path format.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    # convert to lowercase for user comfort
    scope_path = self.cleaned_data.get(field_name).lower()
    if not validate.isScopePathFormatValid(scope_path):
      raise forms.ValidationError("This scope path is in wrong format.")
    return scope_path
  return wrapper


def clean_agrees_to_tos(field_name):
  """Checks if there is a ToS to see if it is allowed to leave 
     the field_name field false.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    agrees_to_tos = self.cleaned_data.get(field_name)

    if not site_logic.logic.getToS(site_logic.logic.getSingleton()):
      return agrees_to_tos

    # Site settings specify a site-wide ToS, so agreement is *required*
    if agrees_to_tos:
      return True
    
    # there was no agreement made so raise an error
    raise forms.ValidationError(
        'The site-wide Terms of Service must be accepted to participate'
        ' on this site.')

  return wrapper


def clean_existing_user(field_name):
  """Check if the field_name field is a valid user.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    link_id = clean_link_id(field_name)(self)
  
    user_entity = user_logic.logic.getForFields({'link_id': link_id}, 
        unique=True)
  
    if not user_entity:
      # user does not exist
      raise forms.ValidationError("This user does not exist.")
  
    return user_entity
  return wrapped


def clean_user_not_exist(field_name):
  """Check if the field_name value is a valid link_id and a user with the
     link id does not exist.
  """ 

  @check_field_is_empty(field_name)
  def wrapped(self):
    link_id = clean_link_id(field_name)(self)
  
    user_entity = user_logic.logic.getForFields({'link_id': link_id}, 
        unique=True)
  
    if user_entity:
      # user exists already
      raise forms.ValidationError("There is already a user with this link id.")
  
    return link_id
  return wrapped


def clean_users_not_same(field_name):
  """Check if the field_name field is a valid user and is not 
     equal to the current user.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    
    clean_user_field = clean_existing_user(field_name)
    user_entity = clean_user_field(self)
    
    current_user_entity = user_logic.logic.getForCurrentAccount()
    
    if user_entity.key() == current_user_entity.key():
      # users are equal
      raise forms.ValidationError("You cannot enter yourself here.")
    
    return user_entity
  return wrapped


def clean_user_account(field_name):
  """Returns the User with the given field_name value.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    email_adress = self.cleaned_data.get(field_name).lower()

    # get the user account for this email
    user_account = users.User(email_adress)

    return user_account
  return wrapped


def clean_user_account_not_in_use(field_name):
  """Check if the field_name value contains an email 
     address that hasn't been used for an existing account.
  """ 

  @check_field_is_empty(field_name)
  def wrapped(self):
    email_adress = self.cleaned_data.get(field_name).lower()

    # get the user account for this email and check if it's in use
    user_account = users.User(email_adress)

    fields = {'account': user_account}
    user_entity = user_logic.logic.getForFields(fields, unique=True)

    if user_entity or user_logic.logic.isFormerAccount(user_account):
      raise forms.ValidationError("There is already a user with this email adress.")

    return user_account
  return wrapped


def clean_feed_url(self):
  feed_url = self.cleaned_data.get('feed_url')

  if feed_url == '':
    # feed url not supplied (which is OK), so do not try to validate it
    return None
  
  if not validate.isFeedURLValid(feed_url):
    raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

  return feed_url


def clean_url(field_name):
  """Clean method for cleaning a field belonging to a LinkProperty.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):

    value = self.cleaned_data.get(field_name)

    # call the Django URLField cleaning method to properly clean/validate this field
    return forms.URLField.clean(self.fields[field_name], value)
  return wrapped


def validate_user_edit(link_id_field, account_field):
  """Clean method for cleaning user edit form.
  
  Raises ValidationError if:
    -Another User has the given email address as account
    -Another User has the given email address in it's FormerAccounts list
  """

  def wrapper(self):
    cleaned_data = self.cleaned_data

    link_id = cleaned_data.get(link_id_field)
    user_account = cleaned_data.get(account_field)

    # if both fields were valid do this check
    if link_id and user_account:
      # get the user from the link_id in the form
      fields = {'link_id': link_id}
      user_entity = user_logic.logic.getForFields(fields, unique=True)

      # if it's not the user's current account
      if user_entity.account != user_account:

        # get the user having the given account
        fields = {'account': user_account}
        user_from_account_entity = user_logic.logic.getForFields(fields, 
            unique=True)

        # if there is a user with the given account or it's a former account
        if user_from_account_entity or user_logic.logic.isFormerAccount(user_account):
          # raise an error because this email address can't be used
          raise forms.ValidationError("There is already a user with this email address.")

    return cleaned_data
  return wrapper


def validate_new_group(link_id_field, scope_path_field, 
                       group_logic, group_app_logic):
  """Clean method used to clean the group application or new group form.
  
    Raises ValidationError if:
    -A application with this link id and scope path already exists
    -A group with this link id and scope path already exists
  """

  def wrapper(self):
      cleaned_data = self.cleaned_data

      fields = {}

      link_id = cleaned_data.get(link_id_field)

      if link_id:
        fields['link_id'] = link_id

        scope_path = cleaned_data.get(scope_path_field)
        if scope_path:
          fields['scope_path'] = scope_path

        # get the application
        group_app_entity = group_app_logic.logic.getForFields(fields, unique=True)

        # get the current user
        user_entity = user_logic.logic.getForCurrentAccount()

        # make sure it's not the applicant creating the new group
        if group_app_entity and (
            group_app_entity.applicant.key() != user_entity.key()):
          # add the error message to the link id field
          self._errors[link_id_field] = ErrorList([DEF_LINK_ID_IN_USE_MSG])
          del cleaned_data[link_id_field]
          # return the new cleaned_data
          return cleaned_data

        # check if there is already a group for the given fields
        group_entity = group_logic.logic.getForFields(fields, unique=True)

        if group_entity:
          # add the error message to the link id field
          self._errors[link_id_field] = ErrorList([DEF_LINK_ID_IN_USE_MSG])
          del cleaned_data[link_id_field]
          # return the new cleaned_data
          return cleaned_data

      return cleaned_data
  return wrapper
