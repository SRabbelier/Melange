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

"""Generic cleaning methods.
"""

__authors__ = [
    '"Todd Larsen" <tlarsen@google.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    ]


import feedparser

from google.appengine.api import users

from django import forms
from django.forms.util import ErrorList
from django.utils.translation import ugettext

from soc.logic import rights as rights_logic
from soc.logic import validate
from soc.logic.models import document as document_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.models import document as document_model


DEF_LINK_ID_IN_USE_MSG = ugettext(
    'This link ID is already in use, please specify another one')

DEF_NO_RIGHTS_FOR_ACL_MSG = ugettext(
    'You do not have the required rights for that ACL.')

DEF_ORGANZIATION_NOT_ACTIVE_MSG = ugettext(
    "This organization is not active or doesn't exist.")

DEF_NO_SUCH_DOCUMENT_MSG = ugettext(
    "There is no such document with that link ID under this entity.")


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
      """Decorator wrapper method.
      """
      field_content = self.cleaned_data.get(field_name)

      if not field_content:
        # field has no content so bail out
        return None
      else:
        # field has contents
        return fun(self)
    return wrapper

  return decorator


def clean_empty_field(field_name):
  """Incorporates the check_field_is_empty as regular cleaner.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapper method.
    """
    return self.cleaned_data.get(field_name)

  return wrapper


def clean_link_id(field_name):
  """Checks if the field_name value is in a valid link ID format.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapper method.
    """
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
    """Decorator wrapper method.
    """
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
    """Decorator wrapper method.
    """
    agrees_to_tos = self.cleaned_data.get(field_name)

    if not site_logic.getToS(site_logic.getSingleton()):
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
    """Decorator wrapper method.
    """
    link_id = clean_link_id(field_name)(self)

    user_entity = user_logic.getFromKeyFields({'link_id': link_id})

    if not user_entity:
      # user does not exist
      raise forms.ValidationError("This user does not exist.")

    return user_entity
  return wrapped


def clean_user_is_current(field_name, as_user=True):
  """Check if the field_name value is a valid link_id and resembles the
     current user.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    """Decorator wrapper method.
    """
    link_id = clean_link_id(field_name)(self)

    user_entity = user_logic.getForCurrentAccount()

    if not user_entity or user_entity.link_id != link_id:
      # this user is not the current user
      raise forms.ValidationError("This user is not you.")

    return user_entity if as_user else link_id
  return wrapped


def clean_user_not_exist(field_name):
  """Check if the field_name value is a valid link_id and a user with the
     link id does not exist.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    """Decorator wrapper method.
    """
    link_id = clean_link_id(field_name)(self)

    user_entity = user_logic.getFromKeyFields({'link_id': link_id})

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
    """Decorator wrapper method.
    """
    clean_user_field = clean_existing_user(field_name)
    user_entity = clean_user_field(self)

    current_user_entity = user_logic.getForCurrentAccount()

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
    """Decorator wrapper method.
    """
    email_adress = self.cleaned_data[field_name]
    return users.User(email_adress)

  return wrapped


def clean_user_account_not_in_use(field_name):
  """Check if the field_name value contains an email
     address that hasn't been used for an existing account.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    """Decorator wrapper method.
    """
    email_adress = self.cleaned_data.get(field_name).lower()

    # get the user account for this email and check if it's in use
    user_account = users.User(email_adress)

    fields = {'account': user_account}
    user_entity = user_logic.getForFields(fields, unique=True)

    if user_entity or user_logic.isFormerAccount(user_account):
      raise forms.ValidationError("There is already a user "
          "with this email adress.")

    return user_account
  return wrapped


def clean_ascii_only(field_name):
  """Clean method for cleaning a field that may only contain ASCII-characters.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapper method.
    """

    value = self.cleaned_data.get(field_name)

    try:
      # encode to ASCII
      value = value.encode("ascii")
    except UnicodeEncodeError:
      # can not encode as ASCII
      raise forms.ValidationError("Only ASCII characters are allowed")

    return value
  return wrapper


def clean_numeric_only(field_name):
  """Clean method for cleaning a field that may only contain numerical values.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapped method.
    """

    value = self.cleaned_data.get(field_name)

    if not value.isdigit():
      raise forms.ValidationError("Only numerical characters are allowed")

    return value
  return wrapper


def clean_feed_url(self):
  """Clean method for cleaning feed url.
  """

  feed_url = self.cleaned_data.get('feed_url')

  if feed_url == '':
    # feed url not supplied (which is OK), so do not try to validate it
    return None

  if not validate.isFeedURLValid(feed_url):
    raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

  return feed_url


def clean_html_content(field_name):
  """Clean method for cleaning HTML content.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    """Decorator wrapper method.
    """

    content = self.cleaned_data.get(field_name)

    if user_logic.isDeveloper():
      return content

    sanitizer = feedparser._HTMLSanitizer('utf-8')
    sanitizer.feed(content)
    content = sanitizer.output()
    content = content.strip().replace('\r\n', '\n')

    return content

  return wrapped


def clean_url(field_name):
  """Clean method for cleaning a field belonging to a LinkProperty.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    """Decorator wrapper method.
    """

    value = self.cleaned_data.get(field_name)

    # call the Django URLField cleaning method to
    # properly clean/validate this field
    return forms.URLField.clean(self.fields[field_name], value)
  return wrapped


def clean_refs(params, fields):
  """Cleans all references to make sure they are valid.
  """

  logic = params['logic']

  def wrapped(self):
    """Decorator wrapper method.
    """

    scope_path = logic.getKeyNameFromFields(self.cleaned_data)

    key_fields = {
        'scope_path': scope_path,
        'prefix': params['document_prefix'],
        }

    for field in fields:
      link_id = self.cleaned_data.get(field)

      if not link_id:
        continue

      key_fields['link_id'] = link_id
      ref = document_logic.logic.getFromKeyFields(key_fields)

      if not ref:
        self._errors[field] = ErrorList([DEF_NO_SUCH_DOCUMENT_MSG])
        del self.cleaned_data[field]
      else:
        self.cleaned_data['resolved_%s' % field] = ref

    return self.cleaned_data

  return wrapped


def validate_user_edit(link_id_field, account_field):
  """Clean method for cleaning user edit form.

  Raises ValidationError if:
    -Another User has the given email address as account
    -Another User has the given email address in it's FormerAccounts list
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    cleaned_data = self.cleaned_data

    link_id = cleaned_data.get(link_id_field)
    user_account = cleaned_data.get(account_field)

    # if both fields were valid do this check
    if link_id and user_account:
      # get the user from the link_id in the form

      user_entity = user_logic.getFromKeyFields({'link_id': link_id})

      # if it's not the user's current account
      if user_entity.account != user_account:

        # get the user having the given account
        fields = {'account': user_account}
        user_from_account_entity = user_logic.getForFields(fields,
            unique=True)

        # if there is a user with the given account or it's a former account
        if user_from_account_entity or \
            user_logic.isFormerAccount(user_account):
          # raise an error because this email address can't be used
          raise forms.ValidationError("There is already a user with "
              "this email address.")

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
    """Decorator wrapper method.
    """
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
      user_entity = user_logic.getForCurrentAccount()

      # if the proposal has not been accepted or it's not the applicant
      # creating the new group then show link ID in use message
      if group_app_entity and (group_app_entity.status != 'accepted' or (
          group_app_entity.applicant.key() != user_entity.key())):
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

def validate_student_proposal(org_field, scope_field,
                              student_logic, org_logic):
  """Validates the form of a student proposal.

  Raises ValidationError if:
    -The organization link_id does not match an active organization
    -The hidden scope path is not a valid active student
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    cleaned_data = self.cleaned_data

    org_link_id = cleaned_data.get(org_field)
    scope_path = cleaned_data.get(scope_field)

    # only if both fields are valid
    if org_link_id and scope_path:
      filter = {'scope_path': scope_path,
                'status': 'active'}

      student_entity = student_logic.logic.getFromKeyName(scope_path)

      if not student_entity or student_entity.status != 'active':
        # raise validation error, access checks should have prevented this
        raise forms.ValidationError(
            ugettext("The given student is not valid."))

      filter = {'link_id': org_link_id,
                'scope': student_entity.scope,
                'status': 'active'}

      org_entity = org_logic.logic.getForFields(filter, unique=True)

      if not org_entity:
        #raise validation error, non valid organization entered
        self._errors['organization'] = ErrorList(
            [DEF_ORGANZIATION_NOT_ACTIVE_MSG])
        del cleaned_data['organization']

    return cleaned_data
  return wrapper

def validate_new_student_project(org_field, mentor_field, student_field):
  """Validates the form of a student proposal.

  Args:
    org_field: Field containing key_name for org
    mentor_field: Field containing the link_id of the mentor
    student_field: Field containing the student link_id

  Raises ValidationError if:
    -A valid Organization does not exist for the given keyname
    -The mentor link_id does not match the mentors for the active organization
    -The student link_id does not match a student in the org's Program
  """

  def wrapper(self):

    from soc.logic.models.mentor import logic as mentor_logic
    from soc.logic.models.organization import logic as org_logic
    from soc.logic.models.student import logic as student_logic

    cleaned_data = self.cleaned_data

    org_key_name = cleaned_data.get(org_field)
    mentor_link_id = cleaned_data.get(mentor_field)
    student_link_id = cleaned_data.get(student_field)

    if not (org_key_name and mentor_link_id and student_link_id):
      # we can't do the check the other cleaners will pickup empty fields
      return cleaned_data

    org_entity = org_logic.getFromKeyName(org_key_name)

    if not org_entity:
      # show error message
      raise forms.ValidationError(
          ugettext("The given Organization is not valid."))

    fields = {'link_id': mentor_link_id,
              'scope': org_entity,
              'status': 'active'}

    mentor_entity = mentor_logic.getForFields(fields, unique=True,)

    if not mentor_entity:
      # show error message
      raise forms.ValidationError(
          ugettext("The given Mentor is not valid."))

    fields = {'link_id': student_link_id,
              'scope': org_entity.scope,
              'status': 'active'}

    student_entity = student_logic.getForFields(fields, unique=True)

    if not student_entity:
      #show error message
      raise forms.ValidationError(
          ugettext("The given Student is not valid."))

    # successfully validated
    return cleaned_data

  return wrapper

def validate_document_acl(view, creating=False):
  """Validates that the document ACL settings are correct.
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    cleaned_data = self.cleaned_data
    read_access = cleaned_data.get('read_access')
    write_access = cleaned_data.get('write_access')

    if not (read_access and write_access and ('prefix' in cleaned_data)):
      return cleaned_data

    if read_access != 'public':
      ordening = document_model.Document.DOCUMENT_ACCESS
      if ordening.index(read_access) < ordening.index(write_access):
        raise forms.ValidationError(
            "Read access should be less strict than write access.")

    params = view.getParams()
    rights = params['rights']

    user = user_logic.getForCurrentAccount()

    rights.setCurrentUser(user.account, user)

    prefix = self.cleaned_data['prefix']
    scope_path = self.cleaned_data['scope_path']

    validate_access(self, view, rights, prefix, scope_path, 'read_access')
    validate_access(self, view, rights, prefix, scope_path, 'write_access')

    if creating and not has_access(rights, 'restricted', scope_path, prefix):
      raise forms.ValidationError(
          "You do not have the required access to create this document.")

    return cleaned_data

  return wrapper


def has_access(rights, access_level, scope_path, prefix):
  """Checks whether the current user has the required access.
  """

  checker = rights_logic.Checker(prefix)
  roles = checker.getMembership(access_level)

  django_args = {
      'scope_path': scope_path,
      'prefix': prefix,
      }

  return rights.hasMembership(roles, django_args)

def validate_access(self, view, rights, prefix, scope_path, field):
  """Validates that the user has access to the ACL for the specified fields.
  """

  access_level = self.cleaned_data[field]

  if not has_access(rights, access_level, scope_path, prefix):
    self._errors[field] = ErrorList([DEF_NO_RIGHTS_FOR_ACL_MSG])
    del self.cleaned_data[field]
