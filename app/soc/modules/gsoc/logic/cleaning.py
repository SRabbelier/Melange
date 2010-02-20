#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""GSOC module cleaning methods.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    ]


import re

from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning


NEWLINE_SEPATAROR = '\n'
COMMA_SEPARATOR = ', '

def cleanTagsList(field_name, separator=NEWLINE_SEPATAROR):
  """Clean method to check and validate list of tag values.
  """

  def wrapper(self):
    """Decorator wrapped method.
    """

    tag_values = cleaning.str2set(field_name, separator)(self)

    for index, tag_value in enumerate(tag_values):

      if not re.search('\A[\w#+\-\.]*\Z', tag_value):
        raise forms.ValidationError(ugettext(
            ('%s is not a valid tag value. Please see help for more details.'
            % tag_value)))

      tag_values[index] = tag_value.lower()

    return tag_values
  return wrapper
