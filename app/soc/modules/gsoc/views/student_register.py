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

"""Module containing the view for GSoC student registration page.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import access_checker
from soc.modules.gsoc.views.helper import url_patterns


class StudentRegister(RequestHandler):
  """Encapsulate all the methods required to generate GSoC student
  registration page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/homepage/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        (r'^gsoc/register/student/%s$' % url_patterns.PROGRAM, self)
    ]

  def checkAccess(self):
    """Access checks for GSoC student registration page.
    """

    checker = access_checker.AccessChecker(self.data)
    checker.checkIsUser()
    checker.checkIsActivePeriod('student_signup')
    checker.checkIsNotParticipatingInProgram()

  def context(self):
    """Handler to for GSoC student registration page HTTP get request.
    """

    return {
        'page_name': 'Register as a student',
        'program': self.data.program,
    }
