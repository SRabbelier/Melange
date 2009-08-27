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

"""GHOP module cleaning methods.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    ]


from django import forms
from django.utils.translation import ugettext


def cleanTaskComment(comment_field, action_field, ws_field):
  """Cleans the comment form and checks to see if there is either
  action or comment content.

  Raises ValidationError if:
    -There is no action taking place and no comment present
    -The action is needs_review and there is no comment or work submission
     present
  """

  def wrapper(self):
    """Decorator wrapper method.
    """
    cleaned_data = self.cleaned_data

    content = cleaned_data.get(comment_field)
    action = cleaned_data.get(action_field)
    work_submission = cleaned_data.get(ws_field)

    if action == 'noaction' and not content:
      raise forms.ValidationError(
          ugettext('You cannot have comment field empty with no action.'))
    if action == 'needs_review' and not content and not work_submission:
      raise forms.ValidationError(
          ugettext('You cannot have both comment field and work '
                   'submission fields empty.'))

    return cleaned_data

  return wrapper
