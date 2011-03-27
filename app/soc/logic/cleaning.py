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

"""Generic cleaning methods.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Todd Larsen" <tlarsen@google.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
    ]

import re

from htmlsanitizer import HtmlSanitizer
from htmlsanitizer import safe_html

from google.appengine.api import users

from django import forms
from django.core import validators
from django.forms.util import ErrorList
from django.utils.translation import ugettext

from soc.logic import validate
from soc.logic.models import document as document_logic
from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic
from soc.models import document as document_model
from soc.modules import callback


DEF_VALID_SHIPPING_CHARS = re.compile('^[A-Za-z0-9\s-]+$')

DEF_LINK_ID_IN_USE_MSG = ugettext(
    'This link ID is already in use, please specify another one')

DEF_NO_RIGHTS_FOR_ACL_MSG = ugettext(
    'You do not have the required rights for that ACL.')

DEF_ORGANZIATION_NOT_ACTIVE_MSG = ugettext(
    "This organization is not active or doesn't exist.")

DEF_NO_SUCH_DOCUMENT_MSG = ugettext(
    "There is no such document with that link ID under this entity.")

DEF_MUST_BE_ABOVE_AGE_LIMIT_FMT = ugettext(
    "To sign up as a student for this program, you "
    "must be at least %d years of age, as of %s.")

DEF_MUST_BE_ABOVE_LIMIT_FMT = ugettext(
    "Must be at least %d characters, it has %d characters.")

DEF_MUST_BE_UNDER_LIMIT_FMT = ugettext(
    "Must be under %d characters, it has %d characters.")

DEF_2_LETTER_STATE_FMT = ugettext(
    "State should be 2-letter field since country is '%s'.")


DEF_ROLE_TARGET_COUNTRY = "United States"

DEF_ROLE_COUNTRY_PAIRS = [("res_country", "res_state"),
                          ("ship_country", "ship_state")]


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

    user_entity = user_logic.getCurrentUser()
    # pylint: disable=E1103
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

    current_user_entity = user_logic.getCurrentUser()
    # pylint: disable=E1103
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
          "with this email address.")

    return user_account
  return wrapped


def clean_valid_shipping_chars(field_name):
  """Clean method for cleaning a field that must comply with Google's character
  requirements for shipping.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapper method.
    """
    value = self.cleaned_data.get(field_name)

    if value and not DEF_VALID_SHIPPING_CHARS.match(value):
      raise forms.ValidationError(
          'Invalid characters, only A-z, 0-9, - and whitespace are allowed.')

    return value
  return wrapper


def clean_content_length(field_name, min_length=0, max_length=500):
  """Clean method for cleaning a field which must contain at least min and
     not more then max length characters.

  Args:
    field_name: the name of the field needed cleaning
    min_length: the minimum amount of allowed characters
    max_length: the maximum amount of allowed characters
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapper method.
    """

    value = self.cleaned_data[field_name]
    value_length = len(value)

    if value_length < min_length:
      raise forms.ValidationError(DEF_MUST_BE_ABOVE_LIMIT_FMT %(
          min_length, value_length))

    if value_length > max_length:
      raise forms.ValidationError(DEF_MUST_BE_UNDER_LIMIT_FMT %(
          max_length, value_length))

    return value
  return wrapper


def clean_phone_number(field_name):
  """Clean method for cleaning a field that may only contain numerical values.
  """

  @check_field_is_empty(field_name)
  def wrapper(self):
    """Decorator wrapped method.
    """

    value = self.cleaned_data.get(field_name)

    # allow for a '+' prefix which means '00'
    if value[0] == '+':
      value = '00' + value[1:]

    if not value.isdigit():
      raise forms.ValidationError("Only numerical characters are allowed")

    return value
  return wrapper


def clean_feed_url(field_name):
  """Clean method for cleaning feed url.
  """

  def wrapper(self):
    """Decorator wrapped method.
    """
    feed_url = self.cleaned_data.get(field_name)

    if feed_url == '':
      # feed url not supplied (which is OK), so do not try to validate it
      return None

    if not validate.isFeedURLValid(feed_url):
      raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

    return feed_url
  return wrapper


def clean_html_content(field_name):
  """Clean method for cleaning HTML content.
  """

  @check_field_is_empty(field_name)
  def wrapped(self):
    """Decorator wrapper method.
    """
    from HTMLParser import HTMLParseError

    content = self.cleaned_data.get(field_name)

    # clean_html_content is called when writing data into GAE rather than
    # when reading data from GAE. This short-circuiting of the sanitizer
    # only affects html authored by developers. The isDeveloper test for
    # example allows developers to add javascript.
    if user_logic.isDeveloper():
      return content

    try:
      cleaner = HtmlSanitizer.Cleaner()
      cleaner.string = content
      cleaner.clean()
    except (HTMLParseError, safe_html.IllegalHTML), msg:
      raise forms.ValidationError(msg)

    content = cleaner.string
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
    validator = validators.URLValidator()

    # call the Django URLField cleaning method to
    # properly clean/validate this field
    try:
      validator(value)
    except forms.ValidationError, e:
      if e.code == 'invalid':
        msg = ugettext(u'Enter a valid URL.')
        raise forms.ValidationError(msg, code='invalid')
    return value
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
                       group_logic):
  """Clean method used to clean the group application or new group form.

    Raises ValidationError if:
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


def validate_student_project(org_field, mentor_field, student_field):
  """Validates the form of a student proposal.

  Args:
    org_field: Field containing key_name for org
    mentor_field: Field containing the link_id of the mentor
    student_field: Field containing the student link_id

  Raises ValidationError if:
    -A valid Organization does not exist for the given key_name
    -The mentor link_id does not match a mentor for the active organization
    -The student link_id does not match a student in the org's Program
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
    from soc.modules.gsoc.logic.models.organization import logic as org_logic
    from soc.modules.gsoc.logic.models.student import logic as student_logic

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


def validate_role():
  """Validates the form of a user role.

  Args:
    pairs: a list of 'country'/'state' tuples

  Raises ValidationError if:
    - The country field has the specified value, and state is not a 2 letters
  """

  target_country = DEF_ROLE_TARGET_COUNTRY
  pairs = DEF_ROLE_COUNTRY_PAIRS

  def wrapper(self):
    """Wrapper method.
    """

    cleaned_data = self.cleaned_data

    for country_field, state_field in pairs:
      country = cleaned_data.get(country_field)
      state = cleaned_data.get(state_field)

      if country is None or state is None:
        continue

      if country != target_country:
        continue

      if len(state) != 2:
        raise forms.ValidationError(DEF_2_LETTER_STATE_FMT % target_country)

    return cleaned_data

  return wrapper


def validate_student(program_logic):
  """Checks if the student is eligible to sign up, determined
  by his birth_date given in field_name.

  Also checks if the school information has been correctly filled in.

  Args:
    birth_date_field: Field containing birth_date of student
    school_type_field: The field containing the type of student
    major_field: The field containing the major of a University student
    degree_field: The field containing the type of degree for a University
                  student
    grade_field: The field containing the grade of a High School student
    scope_field: Field containing scope_path of the student entity
    program_logic: Logic instance of the program

  Raises ValidationError if:
    -The student's age is less than the minimum age required by the program
  """

  def wrapper(self):
    """Wrapper method.
    """

    validator = validate_role()
    cleaned_data = validator(self)

    birth_date = cleaned_data.get('birth_date')
    program_key_name = cleaned_data.get('scope_path')

    if not birth_date or not program_key_name:
      # nothing to check, field validator will find these errors
      return cleaned_data

    # get the current program entity
    entity = program_logic.getFromKeyName(program_key_name)

    if not entity:
      raise forms.ValidationError(
          ugettext("No valid program found"))

    school_type = cleaned_data.get('school_type')
    major = cleaned_data.get('major')
    degree = cleaned_data.get('degree')
    grade = cleaned_data.get('grade')

    # TODO: when school_type is required this can be removed
    if not school_type:
      raise forms.ValidationError("School type cannot be left blank.")

    # if school_type is University, check if the rest of data is correct
    if school_type == 'University':
      # check for major
      if not major:
        raise forms.ValidationError("Major cannot be left blank.")

      # check for degree
      if not degree:
        raise forms.ValidationError("Degree must be selected from "
                                    "the given options.")

      # make sure that grade is not set
      if grade is not None:
        raise forms.ValidationError("If school type is University, "
                                    "grade value must be left blank.")

    # if school_type is High School, check the rest of data is correct
    if school_type == 'High School':
      # check for grade
      if grade is None:
        raise forms.ValidationError("Grade cannot be left blank.")

      # check if the grade value is in proper range
      if grade < 0 or grade > 20:
        raise forms.ValidationError("Grade value must be an integer "
                                    "between 0 and 20.")

      # make sure that neither major nor degree are set
      if major or degree:
        raise forms.ValidationError("If school type is High School, "
                                    "both major and degree values must be "
                                    "left blank.")

    if entity.student_min_age and entity.student_min_age_as_of:
      # only check if both the min_age and min_age_as_of are defined
      min_year = entity.student_min_age_as_of.year - entity.student_min_age
      min_date = entity.student_min_age_as_of.replace(year=min_year)

      if birth_date > min_date:
        # this Student is not old enough
        self._errors['birth_date'] = ErrorList(
            [DEF_MUST_BE_ABOVE_AGE_LIMIT_FMT %(
            entity.student_min_age,
            entity.student_min_age_as_of.strftime('%A, %B %d, %Y'))])
        del cleaned_data['birth_date']

    return cleaned_data
  return wrapper


def validate_document_acl(view, creating=False):
  """Validates that the document ACL settings are correct.
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    cleaned_data = self.cleaned_data

    fields = ['read_access', 'write_access', 'prefix', 'link_id', 'scope_path']

    if not all((i in cleaned_data) for i in fields):
      return cleaned_data

    read_access = cleaned_data['read_access']
    write_access = cleaned_data['write_access']

    if read_access != 'public':
      ordening = document_model.Document.DOCUMENT_ACCESS
      if ordening.index(read_access) < ordening.index(write_access):
        raise forms.ValidationError(
            "Read access should be less strict than write access.")

    params = view.getParams()
    rights = params['rights']

    user = user_logic.getCurrentUser()

    # pylint: disable=E1103
    rights.setCurrentUser(user.account, user)

    prefix = self.cleaned_data['prefix']
    link_id = self.cleaned_data['link_id']
    scope_path = self.cleaned_data['scope_path']

    validate_access(self, view, rights, prefix, scope_path, 'read_access')
    validate_access(self, view, rights, prefix, scope_path, 'write_access')

    if creating:
      key_fields = {
          'prefix': prefix,
          'link_id': link_id,
          'scope_path': scope_path,
          }
      if document_logic.logic.getFromKeyFields(key_fields):
        raise forms.ValidationError(
            "A document with that link_id and scope already exists.")
      if not has_access(rights, 'restricted', scope_path, prefix):
        raise forms.ValidationError(
            "You do not have the required access to create this document.")

    return cleaned_data

  return wrapper


def has_access(rights, access_level, scope_path, prefix):
  """Checks whether the current user has the required access.
  """

  checker = callback.getCore().getRightsChecker(prefix)
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


def str2set(string_field, separator=','):
  """Clean method for cleaning comma separated strings.

  Obtains the separated string from the form and returns it as
  a set of strings.
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    cleaned_data = self.cleaned_data

    string_data = cleaned_data.get(string_field)

    list_data = []
    for string in string_data.split(separator):
      string_strip = string.strip()
      if string_strip and string_strip not in list_data:
        list_data.append(string_strip)

    return list_data

  return wrapper
