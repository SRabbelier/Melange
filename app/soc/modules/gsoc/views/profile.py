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


from google.appengine.ext.db import djangoforms

from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

from soc.views import forms
from soc.views import template

from soc.models.user import User
from soc.models.role import Role

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class UserForm(forms.ModelForm):
  """
  """

  class Meta:
    model = User
    fields = ['link_id']


class ProfileForm(forms.ModelForm):
  """Django form for profile page.
  """

  class Meta:
    model = Role
    exclude = ['link_id', 'user', 'scope', 'mentor_for', 'org_admin_for',
        'student_info', 'agreed_to_tos_on', 'scope_path', 'status']
    widgets = forms.choiceWidgets(Role,
        ['res_country', 'ship_country',
         'tshirt_style', 'tshirt_size', 'gender'])


class StudentInfoForm(forms.ModelForm):
  """
  """


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
    return {
        'page_name': 'Register',
        'user_form': UserForm().render(),
        'profile_form': ProfileForm().render(),
    }

  def post(self):
    """Handler for HTTP POST request.
    """
    if not self.data.user:
      form = UserForm(self.data.POST)
      if form.is_valid():
        key_name = form.link_id
        user = form.create(key_name=key_name)

    form = ProfileForm(self.data.POST, instance=self.data.role)
    if not self.data.role and form.is_valid():
      key_name = '%(sponsor)s/%(program)s/%(link_id)s' % self.data.POST
      profile = form.create(key_name=key_name, parent=user)

    if self.data.kwargs.get('role') == 'student':
      key_name = profile.key().name()
      form = StudentInfoForm(self.data.POST)
      student_info = form.create(key_name=key_name, parent=profile)

    kwargs = dicts.filter(self.data, ['sponsor', 'program'])
    self.redirect(reverse('edit_gsoc_profile', kwargs))
