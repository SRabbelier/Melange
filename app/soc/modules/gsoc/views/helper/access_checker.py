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

"""Module containing the AccessChecker class that contains helper functions
for checking access.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from google.appengine.ext import db

from django.utils.translation import ugettext

from soc.views.helper import access_checker

from soc.modules.gsoc.models.student_proposal import StudentProposal


DEF_MAX_PROPOSALS_REACHED = ugettext(
    'You have reached the maximum number of proposals allowed '
    'for this program.')


class AccessChecker(access_checker.AccessChecker):
  """Helper classes for access checking in GSoC module.
  """

  def canStudentPropose(self):
    """Checks if the student is eligible to submit a proposal.
    """

    # check if the timeline allows submitting proposals
    self.isActivePeriod('student_signup')

    # check how many proposals the student has already submitted 
    fields = {
        'scope': self.data.role
        }
    query = db.Query(StudentProposal)
    query.filter('scope = ', self.data.role).ancestor(self.data.user)

    if query.count() >= self.data.program.apps_tasks_limit:
      # too many proposals access denied
      raise out_of_band.AccessViolation(message_fmt=DEF_MAX_PROPOSALS_REACHED)
