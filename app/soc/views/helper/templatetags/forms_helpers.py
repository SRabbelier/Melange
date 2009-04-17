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


import re

from django import template
from django.forms import forms as forms_in
from django.utils.encoding import force_unicode
from django.utils.html import escape

from soc.logic import accounts
from soc.logic import dicts
from soc.views.helper import widgets


register = template.Library()


@register.inclusion_tag('soc/templatetags/_as_user.html')
def as_user(user):
  """Prints a user as a hyperlinked link_id.
  """

  return {'user': user}


@register.inclusion_tag('soc/templatetags/_as_email.html')
def as_email(account):
  """Prints a user as a hyperlinked link_id.
  """

  denormalized = accounts.denormalizeAccount(account)

  return {'email': denormalized.email()}


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
def readonly_field_as_table_row(label, value):
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

  value = value.strip() if isinstance(value, basestring) else value

  return {'field_label': label,
          'field_value': value}


@register.inclusion_tag(
    'soc/templatetags/_readonly_field_as_twoline_table_row.html')
def readonly_field_as_twoline_table_row(label, value):
  """See readonly_field_as_table_row().
  """

  value = value.strip() if  isinstance(value, basestring) else value

  return {'field_label': label,
          'field_value': value}


@register.inclusion_tag(
    'soc/templatetags/_readonly_url_field_as_table_row.html')
def readonly_url_field_as_table_row(field_label, field_value):
  """See readonly_field_as_table_row().
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag(
    'soc/templatetags/_readonly_url_field_as_twoline_table_row.html')
def readonly_url_field_as_twoline_table_row(field_label, field_value):
  """See readonly_field_as_table_row().
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag(
    'soc/templatetags/_readonly_safe_field_as_table_row.html')
def readonly_safe_field_as_table_row(field_label, field_value):
  """See readonly_field_as_table_row().
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag(
    'soc/templatetags/_readonly_safe_field_as_twoline_table_row.html')
def readonly_safe_field_as_twoline_table_row(field_label, field_value):
  """See readonly_field_as_table_row().
  """
  return {'field_label': field_label,
          'field_value': field_value}


@register.inclusion_tag('soc/templatetags/_as_readonly_table.html',
                        takes_context=True)
def as_readonly_table(context, form):
  """Outputs a form as a properly formatted html table.

  Args:
    form: the form that should be converted to a table
  """

  # create the bound fields
  fields = [forms_in.BoundField(form, field, name) for name, field in
            form.fields.items() if field]

  return {'fields': fields}

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


def as_table_helper(context, form):
  """See as_table().
  """
  
  fields = []
  hidden_fields = []
  hidden_fields_errors = []
  errors = False
  
  # entity = context['entity']

  # Iterate over all fields and prepare it for adding 
  for name, field in form.fields.items():
    if not field:
      continue

    bf = forms_in.BoundField(form, field, name)
    attrs = {}

    if isinstance(field, widgets.ReferenceField):
      attrs = field.rf

    # If the field is hidden we display it elsewhere
    if not bf.is_hidden:
      if bf.errors:
        errors = True

      example_text = ''
      group = '0. '

      if hasattr(field, 'group'):
        group = field.group

      if hasattr(field, 'example_text'):
        example_text = force_unicode(field.example_text)

      item = {
          'field': bf,
          'required': field.required,
          'example_text': example_text,
          'group': group,
          }

      item.update(attrs)
      fields.append(item)
    else:
      hidden_fields.append(unicode(bf))

      for error in bf.errors:
        item = (name, force_unicode(error))
        hidden_fields_errors.append(item)

  grouped = dicts.groupby(fields, 'group')
  rexp = re.compile(r"\d+. ")
  fields = [(rexp.sub('', key), grouped[key]) for key in sorted(grouped)]

  context.update({
      'top_errors': form.non_field_errors() or '',
      'hidden_field_errors': hidden_fields_errors or '',
      'errors': errors,
      'groups': fields if fields else '',
      'hidden_fields': hidden_fields or '',
      })

  return context


@register.inclusion_tag('soc/templatetags/_as_table_row.html',
                        takes_context=True)
def as_table_row(context, item):
  """Outputs a field as a properly formatted html row.

  Args:
    item: the item that is being rendered
  """

  return as_table_row_helper(context, item)


@register.inclusion_tag('soc/templatetags/_as_twoline_table_row.html',
                        takes_context=True)
def as_twoline_table_row(context, item):
  """See as_table_row().
  """

  return as_table_row_helper(context, item)


def as_table_row_helper(context, item):
  """See as_table_row().
  """

  field = item['field']
  required = item['required']
  example_text = item['example_text']

  form = context['form']
  entity = context['entity']

  reference = item.get('reference_url')
  filter = item.get('filter')
  filter_fields = item.get('filter_fields')

  # Escape and cache in local variable.
  errors = [force_unicode(escape(error)) for error in field.errors]


  if reference:
    from soc.views.helper import redirects
    params = {
        'url_name': reference,
        }

    if entity:
      args = {}
      for filter_field, filter_value in filter_fields.iteritems():
        args[filter_field] = filter_value
      for filter_field in (i for i in filter if hasattr(entity, i)):
        args[filter_field] = getattr(entity, filter_field)

      if '__scoped__' in filter:
        args['scope_path'] = entity.key().id_or_name()

      # TODO: replace this hack needed to get org-scoped mentor 
      #       autocompletion on student proposals
      if '__org__' in filter:
        args['scope_path'] = entity.org.key().id_or_name()

      params['args'] = '&'.join(['%s=%s' % item for item in args.iteritems()])

    select_url = redirects.getSelectRedirect(params)

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
      'field': field,
      'field_id': field.auto_id,
      'required': required,
      'example_text': example_text,
      'select_url': select_url if reference else None,
      'errors': errors,
      })

  return context
