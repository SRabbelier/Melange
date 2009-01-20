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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import template
from django.forms import forms as forms_in
from django.utils.encoding import force_unicode
from django.utils.html import escape


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


@register.inclusion_tag('soc/templatetags/_readonly_field_as_table_row.html')
def readonly_field_as_table_row(field_label, field_value):
  """Prints a field value and it's verbose name as a table row.

  This function actually does very little, simply passing the 
  supplied field_label and field_value in a simple context used by the 
  _readonly_field_as_table_row.html template (which is actually 
  doing all of the work).

  See soc/templates/soc/templatetags/_readonly_field_as_table_row.html for
  the CSS styles used by this template tag.

  Usage:
    {% load forms_helpers %}
    ...
    <table>
     {% readonly_field_as_table_row field_label field_value %}
     ...
    </table>

  Args:
    field_label: label of the field to render
    field_value: value of the field to render

  Returns:
    a simple context containing the supplied newforms field instance:
      { 'field_label': field_label',
        'field_value': field_value'}
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag('soc/templatetags/_readonly_field_as_twoline_table_row.html')
def readonly_field_as_twoline_table_row(field_label, field_value):
  """See readonly_field_as_table_row().
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag(
    'soc/templatetags/_readonly_multiline_field_as_table_row.html')
def readonly_multiline_field_as_table_row(field_label, field_value):
  """See readonly_field_as_table_row, but with a different template tag.
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag('soc/templatetags/_as_table.html')
def as_table(form):
  """Outputs a form as a properly formatted html table.

  Args:
    form: the form that should be converted to a table
  """

  return as_table_helper(form)


@register.inclusion_tag('soc/templatetags/_as_twoline_table.html')
def as_twoline_table(form):
  """Outputs a form as a properly formatted html table.

  Args:
    form: the form that should be converted to a table
  """

  return as_table_helper(form)


def as_table_helper(form):
  fields = []
  hidden_fields = []
  hidden_fields_errors = []

  # Iterate over all fields and prepare it for adding 
  for name, field in form.fields.items():
    bf = forms_in.BoundField(form, field, name)

    # If the field is hidden we display it elsewhere
    if not bf.is_hidden:
      example_text = ''
      if hasattr(field, 'example_text'):
        example_text = force_unicode(field.example_text)

      item = (bf, field.required, example_text)
      fields.append(item)
    else:
      hidden_fields.append(unicode(bf))

      for e in bf.errors:
        item = (name, force_unicode(e))
        hidden_fields_errors.append(item)

  return {
      'top_errors': form.non_field_errors() or '',
      'hidden_field_errors': hidden_fields_errors or '',
      'form': form,
      'fields': fields or '',
      'hidden_fields': hidden_fields or '',
      }


@register.inclusion_tag('soc/templatetags/_as_table_row.html')
def as_table_row(form, field, required, example_text):
  """Outputs a field as a properly formatted html row.

  Args:
    form: the form that the row belongs to
    field: the field that should be converted to a row
    required: whether the field is required
    example_text: the example_text for this row
  """

  return as_table_row_helper(form, field, required, example_text)


@register.inclusion_tag('soc/templatetags/_as_twoline_table_row.html')
def as_twoline_table_row(form, field, required, example_text):
  """Outputs a field as a properly formatted html row.

  Args:
    form: the form that the row belongs to
    field: the field that should be converted to a row
    required: whether the field is required
    example_text: the example_text for this row
  """

  return as_table_row_helper(form, field, required, example_text)


def as_table_row_helper(form, field, required, example_text):
  # Escape and cache in local variable.
  errors = [force_unicode(escape(error)) for error in field.errors]

  if field.label:
    label = escape(force_unicode(field.label))

    # Only add the suffix if the label does not end in punctuation.
    if form.label_suffix and (label[-1] not in ':?.!'):
      label += form.label_suffix

    label = field.label_tag(label) or ''

  field_class_type = 'formfield%slabel' % ('error' if errors else '')

  help_text = field.help_text

  return {
      'help_text': force_unicode(help_text) if help_text else '',
      'field_class_type': field_class_type,
      'label': force_unicode(label) if field.label else '',
      'field': unicode(field),
      'required': required,
      'example_text': example_text,
      'errors': errors,
      }
