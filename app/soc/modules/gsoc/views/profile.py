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


from soc.views.template import Template

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns

class Form(object):
  """Form class that facilitates the rendering of forms.
  """

  def render(self):
    """Renders the template to a string.

    Uses the context method to retrieve the appropriate context, uses the
    self.templatePath() method to retrieve the template that should be used.
    """

    context = self.context()
    tepmlate_path = 'v2/modules/gsoc/_form.html'
    rendered = loader.render_to_string(template_path, dictionary=context)
    return rendered

  def context(self):
    """Returns the context for the current template.
    """

    return {}


class ProfileForm(Form):
  """Template for profiles.
  """

  def context(self):
    return {

    }


class Profile(RequestHandler):
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
        'form': None,
    }
