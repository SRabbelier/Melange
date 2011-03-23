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
      try:
        value = db.get(value)
      except db.BadKeyError, e:
        raise forms.ValidationError(unicode(e))
    return value


class ModelFormOptions(object):
  """A simple class to hold internal options for a ModelForm class.

  Instance attributes:
    model: a db.Model class, or None
    fields: list of field names to be defined, or None
    exclude: list of field names to be skipped, or None
    widgets: dictionary of widgets to be used per field, or None

  These instance attributes are copied from the 'Meta' class that is
  usually present in a ModelForm class, and all default to None.
  """


  def __init__(self, options=None):
    self.model = getattr(options, 'model', None)
    self.fields = getattr(options, 'fields', None)
    self.exclude = getattr(options, 'exclude', None)
    self.widgets = getattr(options, 'widgets', None)


class ModelFormMetaclass(djangoforms.ModelFormMetaclass):
  """The metaclass for the ModelForm class defined below.

  This is our analog of Django's own ModelFormMetaclass.  (We
  can't conveniently subclass that class because there are quite a few
  differences.)

  See the docs for ModelForm below for a usage example.
  """

  def __new__(cls, class_name, bases, attrs):
    """Constructor for a new ModelForm class instance.

    The signature of this method is determined by Python internals.

    All Django Field instances are removed from attrs and added to
    the base_fields attribute instead.  Additional Field instances
    are added to this based on the Datastore Model class specified
    by the Meta attribute.
    """
    fields = sorted(((field_name, attrs.pop(field_name))
                     for field_name, obj in attrs.items()
                     if isinstance(obj, forms.Field)),
                    key=lambda obj: obj[1].creation_counter)
    for base in bases[::-1]:
      if hasattr(base, 'base_fields'):
        fields = base.base_fields.items() + fields
    declared_fields = django.utils.datastructures.SortedDict()
    for field_name, obj in fields:
      declared_fields[field_name] = obj

    opts = ModelFormOptions(attrs.get('Meta', None))
    attrs['_meta'] = opts

    base_models = []
    for base in bases:
      base_opts = getattr(base, '_meta', None)
      base_model = getattr(base_opts, 'model', None)
      if base_model is not None:
        base_models.append(base_model)
    if len(base_models) > 1:
      raise django.core.exceptions.ImproperlyConfigured(
          "%s's base classes define more than one model." % class_name)

    if opts.model is not None:
      if base_models and base_models[0] is not opts.model:
        raise django.core.exceptions.ImproperlyConfigured(
            '%s defines a different model than its parent.' % class_name)

      model_fields = django.utils.datastructures.SortedDict()
      for name, prop in sorted(opts.model.properties().iteritems(),
                               key=lambda prop: prop[1].creation_counter):
        if opts.fields and name not in opts.fields:
          continue
        if opts.exclude and name in opts.exclude:
          continue
        form_field = prop.get_form_field()
        if form_field is not None:
          model_fields[name] = form_field
        if opts.widgets and name in opts.widgets:
          model_fields[name].widget = opts.widgets[name]

      model_fields.update(declared_fields)
      attrs['base_fields'] = model_fields

      props = opts.model.properties()
      for name, field in model_fields.iteritems():
        prop = props.get(name)
        if prop:
          def clean_for_property_field(value, prop=prop, old_clean=field.clean):
            value = old_clean(value)
            property_clean(prop, value)
            return value
          field.clean = clean_for_property_field
    else:
      attrs['base_fields'] = declared_fields

    return super(djangoforms.ModelFormMetaclass, cls).__new__(cls,
                                                  class_name, bases, attrs)

class ModelForm(djangoforms.ModelForm):
  """Django ModelForm class which uses our implementation of BoundField.
  """

  __metaclass__ = ModelFormMetaclass

  template_path = 'v2/modules/gsoc/_form.html'

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
      # pylint: disable=E1101
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

    rendered = loader.render_to_string(self.template_path, dictionary=context)
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
    ) if self.field.label else ''

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
