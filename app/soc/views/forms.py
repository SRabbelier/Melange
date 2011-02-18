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


from google.appengine.ext.db import djangoforms

from django.forms import forms
from django.forms import widgets
from django.template import loader
from django.utils.safestring import mark_safe


class ModelForm(djangoforms.ModelForm):
  """
  """

  def __iter__(self):
    for name, field in self.fields.items():
      yield BoundField(self, field, name)


class Form(object):
  """Form class that facilitates the rendering of forms.
  """

  class Form(ModelForm):
    """Django Form associated with the class.
    """

    pass

  def render(self):
    """Renders the template to a string.

    Uses the context method to retrieve the appropriate context, uses the
    self.templatePath() method to retrieve the template that should be used.
    """

    context = self.context()
    template_path = 'v2/modules/gsoc/_form.html'
    rendered = loader.render_to_string(template_path, dictionary=context)
    return rendered

  def context(self):
    """Returns the context for the current template.
    """

    return {}

  def getForm(self):
    """Returns the Django form object associated with the class.
    The specialized forms should be defined in subclasses.
    """

    return self.Form()

class BoundField(forms.BoundField):
  """
  """

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

    return self.as_widget(attrs=attrs)

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

  def renderTextInput(self):
    attrs = {
        'id': self.name,
        'class': 'text',
        }

    return mark_safe('%s%s' % (
        self._render_label(), self.as_widget(attrs=attrs)))

  def renderSelect(self):
    attrs = {
        'id': self.name,
        'style': 'opacity: 100;',
        }

    return mark_safe(('<label>%s%s</label>%s') % (
        self.field.label,
        self._render_is_required(),
        self.as_widget(attrs=attrs)))

  def _render_label(self):
    return '<label>%s%s</label>' % (
        self.field.label,        
        self._render_is_required())
    
  def _render_is_required(self):
    if self.field.required:
      return '<span class="req">*</span>'
    else:
      return ''
