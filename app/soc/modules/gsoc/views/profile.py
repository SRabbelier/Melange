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
from soc.views.template import Template

from soc.models.user import User

from soc.modules.gsoc.models.organization import GSoCOrganization
from soc.modules.gsoc.models.profile import GSoCProfile
from soc.modules.gsoc.models.profile import GSoCStudentInfo
from soc.modules.gsoc.views.base import RequestHandler
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


class EditUserForm(forms.ModelForm):
  """Django form for the user profile.
  """

  class Meta:
    model = User
    css_prefix = 'user'
    fields = ['name']


class ProfileForm(forms.ModelForm):
  """Django form for profile page.
  """

  class Meta:
    model = GSoCProfile
    css_prefix = 'gsoc_profile'
    exclude = ['link_id', 'user', 'scope', 'mentor_for', 'org_admin_for',
               'student_info', 'agreed_to_tos_on', 'scope_path', 'status',
               'name_on_documents', 'agreed_to_tos']
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

  def clean(self):
    country = self.cleaned_data.get('res_country')
    state = self.cleaned_data['res_state']
    if country == 'United States' and (not state or len(state) != 2):
      self._errors['res_state'] = ["Please use a 2-letter state name"]

    country = self.cleaned_data.get('ship_country')
    state = self.cleaned_data['ship_state']
    if country == 'United States' and (not state or len(state) != 2):
      self._errors['ship_state'] = ["Please use a 2-letter state name"]
    return self.cleaned_data


class CreateProfileForm(ProfileForm):
  """Django edit form for profiles.
  """

  class Meta:
    model = ProfileForm.Meta.model
    css_prefix = ProfileForm.Meta.css_prefix
    exclude = ['link_id', 'user', 'scope', 'mentor_for', 'org_admin_for',
               'student_info', 'agreed_to_tos_on', 'scope_path', 'status',
               'name_on_documents']
    widgets = ProfileForm.Meta.widgets

  def __init__(self, tos_content, *args, **kwargs):
    super(CreateProfileForm, self).__init__(*args, **kwargs)
    self.tos_content = tos_content
    self.fields['agreed_to_tos'].widget = forms.TOSWidget(tos_content)

  def clean_agreed_to_tos(self):
    value = self.cleaned_data['agreed_to_tos']
    # no tos set, no need to clean it
    if not self.tos_content:
      return value

    if not value:
      self._errors['agreed_to_tos'] = [
          "You cannot register without agreeing to the Terms of Service"]

    return value



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


class LoggedInMsg(Template):
  """Template to render user login message at the top of the profile form.
  """
  def __init__(self, data):
    self.data = data

  def context(self):
    context = {
        'logout_link': users.create_logout_url(self.data.full_path),
        'user_email': self.data.gae_user.email(),
    }

    if self.data.timeline.orgsAnnounced() and self.data.student_info:
      context['apply_link'] = self.data.redirect.acceptedOrgs().url()

    return context

  def templatePath(self):
    return "v2/modules/gsoc/profile/_form_loggedin_msg.html"


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
    self.check.isLoggedIn()
    self.check.isProgramActive()

    if 'role' in self.data.kwargs:
      role = self.data.kwargs['role']
      kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
      edit_url = reverse('edit_gsoc_profile', kwargs=kwargs)
      if role == 'student':
        self.check.canApplyStudent(edit_url)
      else:
        self.check.canApplyNonStudent(role, edit_url)
    else:
      self.check.isProfileActive()

  def templatePath(self):
    return 'v2/modules/gsoc/profile/base.html'

  def context(self):
    role = self.data.kwargs.get('role')
    if self.data.student_info or role == 'student':
      student_info_form = StudentInfoForm(self.data.POST or None,
          instance=self.data.student_info)
    else:
      student_info_form = EmptyForm()

    tos_content = None

    program = self.data.program
    if not role:
      page_name = 'Edit your Profile'
    elif role == 'student':
      page_name = 'Register as a Student'
      if program.student_agreement:
        tos_content = program.student_agreement.content
    elif role == 'mentor':
      page_name = 'Register as a Mentor'
      if program.mentor_agreement:
        tos_content = program.mentor_agreement.content
    elif role == 'org_admin':
      page_name = 'Register as Org Admin'
      if program.org_admin_agreement:
        tos_content = program.org_admin_agreement.content

    form = EditUserForm if self.data.user else UserForm
    user_form = form(self.data.POST or None, instance=self.data.user)
    form = ProfileForm if self.data.profile else CreateProfileForm
    profile_form = form(tos_content, self.data.POST or None,
                        instance=self.data.profile)
    error = user_form.errors or profile_form.errors or student_info_form.errors

    context = {
        'page_name': page_name,
        'form_top_msg': LoggedInMsg(self.data),
        'forms': [user_form, profile_form, student_info_form],
        'has_profile': bool(self.data.profile),
        'error': error,
    }

    return context

  def validateUser(self, dirty):
    if self.data.user:
      user_form = EditUserForm(self.data.POST, instance=self.data.user)
    else:
      user_form = UserForm(self.data.POST)

    if not user_form.is_valid():
      return user_form

    if self.data.user:
      user_form.save(commit=False)
      dirty.append(self.data.user)
      return user_form

    key_name = user_form.cleaned_data['link_id']
    account = users.get_current_user()
    user_form.cleaned_data['account'] = account
    user_form.cleaned_data['user_id'] = account.user_id()
    self.data.user = user_form.create(commit=False, key_name=key_name)
    dirty.append(self.data.user)
    return user_form

  def validateProfile(self, dirty):
    # we just want to pass some dummy variable as a place holder for
    # tos_content. While validating the form, the value for this variable
    # doesn't matter.
    tos_content = None
    profile_form = ProfileForm(tos_content, self.data.POST,
                               instance=self.data.profile)

    if not profile_form.is_valid():
      return profile_form, None

    key_name = '%s/%s' % (self.data.program.key().name(),
                          self.data.user.link_id)
    profile_form.cleaned_data['link_id'] = self.data.user.link_id
    profile_form.cleaned_data['user'] = self.data.user
    profile_form.cleaned_data['scope'] = self.data.program

    if self.data.profile:
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
    if not self.validate():
      self.get()
      return

    link_id = self.data.GET.get('org')
    if link_id:
      key_name = '%s/%s' % (
          self.data.program.name(), link_id
          )
      organization = GSoCOrganization.get_by_key_name(key_name)
    else:
      organization = None

    if not organization:
      self.redirect.program()
      self.redirect.to('edit_gsoc_profile', validated=True)
      return

    self.redirect.organization(organization)

    if self.data.student_info:
      link = 'submit_gsoc_proposal'
    else:
      link = 'gsoc_org_home'

    self.redirect.to(link)
