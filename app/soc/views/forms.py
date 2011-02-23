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


from google.appengine.ext import db
from google.appengine.ext.db import djangoforms

from django.forms import forms
from django.forms import widgets
from django.template import loader
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext


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


class ModelForm(djangoforms.ModelForm):
  """Django ModelForm class which uses our implementation of BoundField.
  """

  def __iter__(self):
    for name, field in self.fields.items():
      yield BoundField(self, field, name)

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
        '<label>%s%s%s</label>' % (
        self.as_widget(attrs=attrs),
        self.field.label,
        self._render_is_required()
        ))

  def renderTextArea(self):
    attrs = {
        'id': self.name,
        'class': 'textarea'
        }

    return mark_safe('%s%s%s' % (
        self._render_label(),
        self._render_error(),  
        self.as_widget(attrs=attrs)))

  def renderTextInput(self):
    attrs = {
        'id': self.name,
        'class': 'text',
        }

    return mark_safe('%s%s%s' % (
        self._render_label(),
        self._render_error(),  
        self.as_widget(attrs=attrs)))

  def renderSelect(self):
    attrs = {
        'id': self.name,
        'style': 'opacity: 100;',
        }

    return mark_safe(('%s%s') % (
        self.as_widget(attrs=attrs),
        self._render_is_required()))

  def _render_label(self):
    return '<label>%s%s</label>' % (
        self.field.label,        
        self._render_is_required())

  def _render_error(self):
    if not self.errors:
      return ''
    else:
      return '<span class="error-message">%s</span>' % (
          self.errors[0])

  def _render_is_required(self):
    if self.field.required:
      return '<span class="req">*</span>'
    else:
      return ''

  def div_class(self):
    name = self.name
    if self.errors:
      name += ' error'
    return name
