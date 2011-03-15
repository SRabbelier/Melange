#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module for the GSoC profile page.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

from django.forms import fields
from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

from soc.logic import cleaning
from soc.logic import dicts
from soc.views import forms
from soc.views import template

from soc.models.user import User

from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.profile import GSoCStudentInfo
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class EmptyForm(forms.ModelForm):
  pass


class UserForm(forms.ModelForm):
  """Django form for the user profile.
  """

  class Meta:
    model = User
    css_prefix = 'user'
    fields = ['link_id', 'name']

  clean_link_id = cleaning.clean_link_id('link_id')


class ProfileForm(forms.ModelForm):
  """Django form for profile page.
  """

  class Meta:
    model = GSoCProfile
    css_prefix = 'gosc_profile'
    exclude = ['link_id', 'user', 'scope', 'mentor_for', 'org_admin_for',
               'student_info', 'agreed_to_tos_on', 'scope_path', 'status',
               'name_on_documents']
    widgets = forms.choiceWidgets(GSoCProfile,
        ['res_country', 'ship_country',
         'tshirt_style', 'tshirt_size', 'gender'])

  clean_given_name = cleaning.clean_valid_shipping_chars('given_name')
  clean_surname = cleaning.clean_valid_shipping_chars('surname')
  clean_phone = cleaning.clean_phone_number('phone')
  clean_res_street = cleaning.clean_valid_shipping_chars('res_street')
  clean_res_street_extra = cleaning.clean_valid_shipping_chars(
      'res_street_extra')
  clean_res_city = cleaning.clean_valid_shipping_chars('res_city')
  clean_res_state = cleaning.clean_valid_shipping_chars('res_state')
  clean_res_postalcode = cleaning.clean_valid_shipping_chars(
      'res_postalcode')
  clean_ship_name = cleaning.clean_valid_shipping_chars('ship_name')
  clean_ship_street = cleaning.clean_valid_shipping_chars('ship_street')
  clean_ship_street_extra = cleaning.clean_valid_shipping_chars(
      'ship_street_extra')
  clean_ship_city = cleaning.clean_valid_shipping_chars('ship_city')
  clean_ship_state = cleaning.clean_valid_shipping_chars('ship_state')
  clean_ship_postalcode = cleaning.clean_valid_shipping_chars(
      'ship_postalcode')
  clean_home_page = cleaning.clean_url('home_page')
  clean_blog = cleaning.clean_url('blog')
  clean_photo_url = cleaning.clean_url('photo_url')


class StudentInfoForm(forms.ModelForm):
  """Django form for the student profile page.
  """

  class Meta:
    model = GSoCStudentInfo
    css_prefix = 'student_info'
    exclude = ['school', 'school_type']
    widgets = forms.choiceWidgets(GSoCStudentInfo,
        ['school_country', 'school_type', 'degree'])

  school_home_page = fields.URLField(required=True)
  clean_school_home_page =  cleaning.clean_url('school_home_page')

class ProfilePage(RequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/profile/%s$' % url_patterns.PROGRAM,
         self, name='edit_gsoc_profile'),
        url(r'^gsoc/profile/%s$' % url_patterns.PROFILE,
         self, name='create_gsoc_profile'),
    ]

  def checkAccess(self):
    check = access_checker.AccessChecker(self.data)
    check.isLoggedIn()
    check.isProgramActive()

    if 'role' in self.data.kwargs:
      role = self.data.kwargs['role']
      if role == 'student':
        check.isNotParticipatingInProgram()
        check.isActivePeriod('student_signup')
    else:
      check.isRoleActive()

  def templatePath(self):
    return 'v2/modules/gsoc/profile/base.html'

  def context(self):
    user_form = UserForm(self.data.POST or None, instance=self.data.user)
    profile_form = ProfileForm(self.data.POST or None, instance=self.data.role)

    role = self.data.kwargs.get('role')
    if self.data.student_info or role == 'student':
      student_info_form = StudentInfoForm(self.data.POST or None,
          instance=self.data.student_info)
    else:
      student_info_form = EmptyForm()

    if not role:
      page_name = 'Edit your Profile'
    elif role == 'student':
      page_name = 'Register as a Student'
    elif role == 'mentor':
      page_name = 'Register as a Mentor'
    elif role == 'org_admin':
      page_name = 'Register as Org Admin'
      
    return {
        'page_name': page_name,
        'user_form': user_form,
        'profile_form': profile_form,
        'student_info_form': student_info_form,
    }

  def validateUser(self, dirty):
    if self.data.user:
      return EmptyForm(self.data.POST)

    user_form = UserForm(self.data.POST)

    if not user_form.is_valid():
      return user_form

    key_name = user_form.cleaned_data['link_id']
    account = users.get_current_user()
    user_form.cleaned_data['account'] = account
    user_form.cleaned_data['user_id'] = account.user_id()
    self.data.user = user_form.create(commit=False, key_name=key_name)
    dirty.append(self.data.user)
    return profile_form

  def validateProfile(self, dirty):
    profile_form = ProfileForm(self.data.POST, instance=self.data.role)

    if not profile_form.is_valid():
      return profile_form, None

    key_name = '%s/%s' % (self.data.program.key().name(),
                          self.data.user.link_id)
    profile_form.cleaned_data['link_id'] = self.data.user.link_id
    profile_form.cleaned_data['user'] = self.data.user
    profile_form.cleaned_data['scope'] = self.data.program

    if self.data.role:
      profile = profile_form.save(commit=False)
    else:
      profile = profile_form.create(commit=False, key_name=key_name, parent=self.data.user)

    dirty.append(profile)

    return profile_form, profile

  def validateStudent(self, dirty, profile):
    if not (self.data.student_info or self.data.kwargs.get('role') == 'student'):
      return EmptyForm(self.data.POST)

    student_form = StudentInfoForm(self.data.POST, instance=self.data.student_info)

    if not(profile and student_form.is_valid()):
      return student_form

    key_name = profile.key().name()

    if self.data.student_info:
      student_info = student_form.save(commit=False)
    else:
      student_info = student_form.create(commit=False, key_name=key_name, parent=profile)
      profile.student_info = student_info

    dirty.append(student_info)

    return student_form

  def validate(self):
    dirty = []
    user_form = self.validateUser(dirty)
    profile_form, profile = self.validateProfile(dirty)
    student_form = self.validateStudent(dirty, profile)

    if user_form.is_valid() and profile_form.is_valid() and student_form.is_valid():
      db.run_in_transaction(db.put, dirty)
      return True
    else:
      return False

  def post(self):
    """Handler for HTTP POST request.
    """
    if self.validate():
      kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
      self.redirect(reverse('edit_gsoc_profile', kwargs=kwargs))
    else:
      self.get()
