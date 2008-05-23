#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""A Django template tag library containing forms helpers.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from django import template
register = template.Library()


@register.inclusion_tag('soc/templatetags/_field_as_table_row.html')
def field_as_table_row(field):
  """Prints a newforms field as a table row.

  This function actually does very little, simply passing the supplied
  form field instance in a simple context used by the _field_as_table_row.html
  template (which is actually doing all of the work).

  See soc/templates/soc/templatetags/_field_as_table_row.html for the CSS
  styles used by this template tag.

  Usage:
    {% load forms_helpers %}
    ...
    <table>
     {% field_as_table_row form.fieldname %}
     ...
    </table>

  Args:
    field: a Django newforms field instance

  Returns:
    a simple context containing the supplied newforms field instance:
      { 'field': field }
  """
  return {'field': field}
