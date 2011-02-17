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


class Form(object):
  """Form class that facilitates the rendering of forms.
  """

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


class BoundField(forms.BoundField):
  """
  """

  def is_required(self):
    return self.field.required

  def render(self):
    attrs = {}
    widget = self.field.widget
    if isinstance(widget, widgets.TextInput):
      attrs['class'] = 'text'
    elif isinstance(widget, widgets.Select):
      attrs['style'] = 'opacity: 0;'

    return self.as_widget(attrs=attrs)

class ModelForm(djangoforms.ModelForm):
  """
  """


  def __iter__(self):
    for name, field in self.fields.items():
      yield BoundField(self, field, name)
