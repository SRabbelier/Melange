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

from django.forms import forms as dj_forms

from soc.views import forms
from soc.views import template

from soc.models.role import Role

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class Profile(forms.Form):
  """Template for profiles.
  """

  class Form(forms.ModelForm): 
    """Django form for profile page.
    """
    
    class Meta:
      model = Role
      exclude = ['link_id', 'user', 'scope', 'mentor_for', 'org_admin_for', 
          'student_info', 'agreed_to_tos_on']
#      widgets = {
#        'res_country': djangoforms.ModelChoiceField(Role,
#         empty_label='sadsadssads'),
#         }

  def context(self):
    return {
        'form': self.Form()
    }


class ProfilePage(RequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        (r'^gsoc/profile/%s$' % url_patterns.PROGRAM, self),
        (r'^gsoc/profile/%s$' % url_patterns.PROFILE, self),
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
        'form': Profile().render(),
    }
