#!/usr/bin/env python2.5
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

"""A Django template tag library containing GHOP forms helpers.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from django import template


register = template.Library()


@register.inclusion_tag(
    'modules/ghop/templatetags/_as_filter_multiselect.html')
def as_filter_multiselect(label, value):
  """Prints a field value and it's verbose name as a form multiple select .

  Args:
    label: label of the field to render
    value: value of the field to render

  Returns:
    a simple context containing the supplied newforms field instance:
      { 'field_label': field_label',
        'field_value': field_value'}
  """

  return {'field_label': label,
          'field_value': value}
