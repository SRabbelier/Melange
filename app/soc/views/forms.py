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

"""Module containing the boiler plate required to construct templates
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import collections
import re

from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

from django.forms import forms
from django.forms import widgets
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext

import django


def choiceWidget(field):
  """Returns a Select widget for the specified field.
  """
  label = field.verbose_name

  choices = []
  choices.append(('', label))
  for choice in field.choices:
    choices.append((str(choice), unicode(choice)))
  return widgets.Select(choices=choices)


def choiceWidgets(model, fields):
  """Returns a dictionary of Select widgets for the specified fields.
  """
  return dict((i, choiceWidget(getattr(model, i))) for i in fields)


class ReferenceProperty(djangoforms.ReferenceProperty):
  # ReferenceProperty field allows setting to None.

  __metaclass__ = djangoforms.monkey_patch

  def get_form_field(self):
    """Return a Django form field appropriate for a reverse reference.

    This defaults to a CharField instance.
    """
    return django.forms.CharField(required=self.required)

  def make_value_from_form(self, value):
    """Convert a form value to a property value.

    This turns a key string or object into a model instance.
    Returns None if value is ''.
    """

    if not value:
      return None
    if not isinstance(value, db.Model):
      value = db.get(value)
    return value


class ModelForm(djangoforms.ModelForm):
  """Django ModelForm class which uses our implementation of BoundField.
  """

  def __init__(self, *args, **kwargs):
    """Fixes label and help_text issues after parent initialization.

    Args:
      *args, **kwargs:  passed through to parent __init__() constructor
    """

    super(djangoforms.ModelForm, self).__init__(*args, **kwargs)

    renames = {
        'verbose_name': 'label',
        'help_text': 'help_text',
        'example_text': 'example_text',
        'group': 'group',
        }

    for field_name in self.fields.iterkeys():
      field = self.fields[field_name]

      # Since fields can be added only to the ModelForm subclass, check to
      # see if the Model has a corresponding field first.
      # pylint: disable-msg=E1101
      if not hasattr(self.Meta.model, field_name):
        continue

      model_prop = getattr(self.Meta.model, field_name)

      for old, new in renames.iteritems():
        value = getattr(model_prop, old, None)
        if value and not getattr(field, new, None):
          setattr(field, new, value)

  def __iter__(self):
    grouping = collections.defaultdict(list)

    for name, field in self.fields.items():
      bound = BoundField(self, field, name)
      group = getattr(field, 'group', '0. ')
      grouping[group].append(bound)

    rexp = re.compile(r"\d+. ")

    for group, fields in sorted(grouping.items()):
      yield rexp.sub('', group), fields

  def create(self, commit=True, key_name=None, parent=None):
    """Save this form's cleaned data into a new model instance.

    Args:
      commit: optional bool, default True; if true, the model instance
        is also saved to the datastore.
      key_name: the key_name of the new model instance, default None
      parent: the parent of the new model instance, default None

    Returns:
      The model instance created by this call.
    Raises:
      ValueError if the data couldn't be validated.
    """
    if not self.is_bound:
      raise ValueError('Cannot save an unbound form')
    opts = self._meta
    instance = self.instance
    if self.instance:
      raise ValueError('Cannot create a saved form')
    if self.errors:
      raise ValueError("The %s could not be created because the data didn't "
                       'validate.' % opts.model.kind())
    cleaned_data = self._cleaned_data()
    converted_data = {}
    for name, prop in opts.model.properties().iteritems():
      value = cleaned_data.get(name)
      if value is not None:
        converted_data[name] = prop.make_value_from_form(value)
    try:
      instance = opts.model(key_name=key_name, parent=parent, **converted_data)
      self.instance = instance
    except db.BadValueError, err:
      raise ValueError('The %s could not be created (%s)' %
                       (opts.model.kind(), err))
    if commit:
      instance.put()
    return instance

  def render(self):
    """Renders the template to a string.

    Uses the context method to retrieve the appropriate context, uses the
    self.templatePath() method to retrieve the template that should be used.
    """

    context = {
      'form': self,
    }
    template_path = 'v2/modules/gsoc/_form.html'
    rendered = loader.render_to_string(template_path, dictionary=context)
    return rendered


class BoundField(forms.BoundField):
  """
  """

  NOT_SUPPORTED_MSG_FMT = ugettext('Widget %s is not supported.')

  def is_required(self):
    return self.field.required

  def render(self):
    attrs = {
        'id': self.name
        }

    widget = self.field.widget

    if isinstance(widget, widgets.TextInput):
      return self.renderTextInput()
    elif isinstance(widget, widgets.DateInput):
      return self.renderTextInput()
    elif isinstance(widget, widgets.Select):
      return self.renderSelect()
    elif isinstance(widget, widgets.CheckboxInput):
      return self.renderCheckboxInput()
    elif isinstance(widget, widgets.Textarea):
      return self.renderTextArea()

    return self.NOT_SUPPORTED_MSG_FMT % (
        widget.__class__.__name__)

  def renderCheckboxInput(self):
    attrs = {
        'id': self.name,
        'style': 'opacity: 100;',
        }

    return mark_safe(
        '<label>%s%s%s%s</label>%s' % (
        self.as_widget(attrs=attrs),
        self.field.label,
        self._render_is_required(),
        self._render_error(),
        self._render_note(),
        ))

  def renderTextArea(self):
    attrs = {
        'id': self.name,
        'class': 'textarea'
        }

    return mark_safe('%s%s%s%s' % (
        self._render_label(),
        self.as_widget(attrs=attrs),
        self._render_error(),  
        self._render_note(),
    ))

  def renderTextInput(self):
    attrs = {
        'id': self.name,
        'class': 'text',
        }

    return mark_safe('%s%s%s%s' % (
        self._render_label(),
        self.as_widget(attrs=attrs),
        self._render_error(),
        self._render_note(),
    ))

  def renderSelect(self):
    attrs = {
        'id': self.name,
        'style': 'opacity: 100;',
        }

    return mark_safe('%s%s%s%s' % (
        self.as_widget(attrs=attrs),
        self._render_is_required(),
        self._render_error(),
        self._render_note(),
    ))

  def _render_label(self):
    return '<label>%s%s</label>' % (
        self.field.label,
        self._render_is_required(),
    )

  def _render_error(self):
    if not self.errors:
      return ''

    return '<div class="error-message">%s</div>' % (
        self.errors[0])

  def _render_is_required(self):
    if not self.field.required:
      return ''

    return '<span class="req">*</span>'

  def _render_note(self):
    return '<span class="note">%s</span>' % (
        self.help_text)

  def div_class(self):
    name = self.form.Meta.css_prefix + '_' + self.name
    if self.errors:
      name += ' error'
    return name
