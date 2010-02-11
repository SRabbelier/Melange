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

"""A Django template tag library containing list helpers.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import template

register = template.Library()

@register.inclusion_tag('soc/templatetags/_as_lists.html')
def as_lists(lists_data):
  """Prints multiple lists as html.
  """

  return {
      'list': lists_data,
  }

@register.inclusion_tag('soc/templatetags/_as_list.html')
def as_list(list_data):
  """Prints a list as html.
  """

  return {
      'list': list_data,
  }
