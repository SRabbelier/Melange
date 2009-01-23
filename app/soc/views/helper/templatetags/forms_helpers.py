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


from google.appengine.ext import db

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


@register.inclusion_tag('soc/templatetags/_as_table.html', takes_context=True)
def as_table(context, form):
  """Outputs a form as a properly formatted html table.

  Args:
    form: the form that should be converted to a table
  """

  return as_table_helper(context, form)


@register.inclusion_tag('soc/templatetags/_as_twoline_table.html',
                        takes_context=True)
def as_twoline_table(context, form):
  """Outputs a form as a properly formatted html table.

  Args:
    form: the form that should be converted to a table
  """

  return as_table_helper(context, form)


def get_reference_url(form, name):
  """Retrieves the reference url from a field

  Args:
    form: the form the field is defined in
    name: the name of the field
  """

  if not hasattr(form, 'Meta'):
    return None

  if not hasattr(form.Meta, 'model'):
    return None

  if not hasattr(form.Meta.model, name):
    return None

  field = getattr(form.Meta.model, name)

  if not isinstance(field, db.ReferenceProperty):
    return None

  return getattr(field, 'redirect_url', None)


def as_table_helper(context, form):
  fields = []
  hidden_fields = []
  hidden_fields_errors = []
  entity = context['entity']

  # Iterate over all fields and prepare it for adding 
  for name, field in form.fields.items():
    bf = forms_in.BoundField(form, field, name)
    reference = None

    if name.endswith('_link_id'):
      reference = get_reference_url(form, name[:-8])

    # If the field is hidden we display it elsewhere
    if not bf.is_hidden:
      example_text = ''
      if hasattr(field, 'example_text'):
        example_text = force_unicode(field.example_text)

      item = (bf, field.required, example_text, reference)
      fields.append(item)
    else:
      hidden_fields.append(unicode(bf))

      for e in bf.errors:
        item = (name, force_unicode(e))
        hidden_fields_errors.append(item)

  context.update({
      'top_errors': form.non_field_errors() or '',
      'hidden_field_errors': hidden_fields_errors or '',
      'fields': fields or '',
      'hidden_fields': hidden_fields or '',
      })

  return context


@register.inclusion_tag('soc/templatetags/_as_table_row.html',
                        takes_context=True)
def as_table_row(context, field, required, example_text, reference):
  """Outputs a field as a properly formatted html row.

  Args:
    form: the form that the row belongs to
    field: the field that should be converted to a row
    required: whether the field is required
    example_text: the example_text for this row
    reference: the entity_suffix if the field is a reference
  """

  return as_table_row_helper(context, field, required, example_text, reference)


@register.inclusion_tag('soc/templatetags/_as_twoline_table_row.html',
                        takes_context=True)
def as_twoline_table_row(context, field, required, example_text, reference):
  """See as_table_row().
  """

  return as_table_row_helper(context, field, required, example_text, reference)


def as_table_row_helper(context, field, required, example_text, reference):
  """See as_table_row().
  """

  # Escape and cache in local variable.
  errors = [force_unicode(escape(error)) for error in field.errors]

  form = context['form']
  entity = context['entity']

  if reference:
    from soc.views.helper import redirects
    params = {
        'url_name': reference,
        'field_name': field.name,
        'return_url': context['return_url']
        }
    select_url = redirects.getSelectRedirect(entity, params)

  if field.label:
    label = escape(force_unicode(field.label))

    # Only add the suffix if the label does not end in punctuation.
    if form.label_suffix and (label[-1] not in ':?.!'):
      label += form.label_suffix

    label = field.label_tag(label) or ''

  field_class_type = 'formfield%slabel' % ('error' if errors else '')

  help_text = field.help_text

  context.update({
      'help_text': force_unicode(help_text) if help_text else '',
      'field_class_type': field_class_type,
      'label': force_unicode(label) if field.label else '',
      'field': unicode(field),
      'required': required,
      'example_text': example_text,
      'select_url': select_url if reference else None,
      'errors': errors,
      })

  return context
