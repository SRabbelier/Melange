#!/usr/bin/env python2.5
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

"""This module defines classes and functions for Dynamic Forms.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    ]


from google.appengine.ext.db import djangoforms

from soc.logic import dicts


class DynaFormMetaclass(djangoforms.ModelFormMetaclass):
  """The DynaForm Meta class, adding support for dynamically defined fields.

  The new DynaForm class that is created by class function is very
  similar to one created by the regular djangoforms.ModelFormMetaclass.
  The only difference is that is the form class has a Meta property,
  it's 'dynaconf' field will be used to define additional properties
  in the form class.

  The 'dynaconf' field (if present), is expected to be iterable as a
  dictionary (with iteritems). The keys are used as the property names,
  and the values are used as the property value.
  """

  def __new__(mcs, class_name, bases, attrs):
    """See djangoforms.ModelFormMetaclass on how the __new__ method
    is used, for an explanation on how this class modifies the default
    behavior, see the DynaFormMetaclass's docstring.
    """

    # Retrieve the Meta class, if present
    meta = attrs.get('Meta', None)
    conf = None

    # Try to retrieve the dynaconf property
    if meta:
      conf = getattr(meta, 'dynaconf', None)

    # When found, extend the form's attribute's with the specified ones
    if conf:
      for key, value in conf.iteritems():
        attrs[key] = value

    # Leave the rest to djangoforms.ModelFormMetaclass.
    return super(DynaFormMetaclass, mcs).__new__(mcs, class_name, bases, attrs)


def newDynaForm(dynamodel=None, dynabase=None, dynainclude=None, 
                dynaexclude=None, dynaproperties=None):
  """Creates a new form DynaForm class.

  The returned class extends dynabase, but with the following additions:
  * It has a Meta class with the 'model', 'include', and 'exclude'
  fields set as specified by newDynaForm's keyword arguments.
  * It's __metaclass__ is set to DynaFormMetaclass (which inherits from
  the default djangoforms.ModelFormMetaclass).
  * The Meta class has an additional dynaconf field which is set to
  the dyanfields keyword argument passed to newDynaForm.

  See DynaFormMetaclass for an explanation on how the dynaproperties
  property is used to construct the DynaForm class.
  """

  class DynaForm(dynabase):
    """The dynamically created Form class
    """

    __metaclass__ = DynaFormMetaclass

    class Meta:
      """Inner Meta class that defines some behavior for the form.
      """

      model = dynamodel
      fields = dynainclude
      exclude = dynaexclude
      dynaconf = dynaproperties

  return DynaForm


def extendDynaForm(dynaform, dynainclude=None, dynaexclude=None, 
                   dynaproperties=None, append=False):
  """Extends an existing dynaform.

  If any of dynainclude, dynaexclude or dynaproperties are not present,
  they are retrieved from dynaform (if present in it's Meta class).

  While it is rather useless to extend from a dynaform that does not have
  a Meta class, it is allowed, the resulting DynaForm is the same as if
  newDynaForm was called with all extendDynForm's keyword arguments.

  If append is True, the form's original values for include and
  exclude will be appended to the supplied dynainclude and
  dynaexclude, which both are still allowed to be None.
  """

  # Retrieve the Meta class from the existing dynaform
  meta = getattr(dynaform, 'Meta')

  dynamodel = getattr(meta, 'model', None)

  originclude = getattr(meta, 'include', [])
  origexclude = getattr(meta, 'exclude', [])

  if not dynainclude:
    dynainclude = originclude
    originclude = []
  if not dynaexclude:
    dynaexclude = origexclude
    origexclude = []

  if append:
    dynainclude += originclude
    dynaexclude += origexclude

  # The most interesting parameter, the 'extra fields' dictionary
  dynaconf = getattr(meta, 'dynaconf', {})
  dynaproperties = dicts.merge(dynaproperties, dynaconf)

  # Create a new DynaForm, using the properties we extracted
  return newDynaForm(
      dynamodel=dynamodel,
      dynabase=dynaform,
      dynainclude=dynainclude,
      dynaexclude=dynaexclude,
      dynaproperties=dynaproperties)


class DynaFieldMetaclass(type):
  """The DynaField Meta class, adding support for dynamic properties.

  The new DynaField class that is created by class function is only
  modified slightly. The only difference is that if the field class has
  a dynaproperties property, it will be used to define additional properties
  for the field.

  The 'dynaproperties' property (if present), is expected to be iterable as a
  dictionary (with iteritems). The keys are used as the property names,
  and the values are used as the property value.
  """

  def __new__(mcs, name, bases, attrs):
    """See djangoforms.ModelFormMetaclass on how the __new__ method
    is used, for an explanation on how this class modifies the default
    behavior, see the DynaFormMetaclass's docstring.
    """

    # Retrieve the Meta class, if present
    dynaproperties = attrs.get('dynaproperties', {})

    for key, value in dynaproperties.iteritems():
      attrs[key] = value

    # Leave the rest to type
    return super(DynaFieldMetaclass, mcs).__new__(mcs, name, bases, attrs)


def newDynaField(field, base, passthrough):
  """Creates a new form DynaField class.

  The returned class extends base, but with the following additions:
  * It has a dynaproperties attribute as extracted from field.
  * It's __metaclass__ is set to DynaFieldMetaclass (which inherits from
  the default type class).

  See DynaFieldMetaclass for an explanation on how the dynaproperties
  property is used to construct the DynaForm class.
  """

  # pass only known accepted arguments to super
  init_args = dicts.filter(field, passthrough)

  properties = field.copy()

  # all pass through arguments are handled by super
  for key in passthrough:
    if key in properties:
      del properties[key]

  # pylint: disable=E1002
  class DynaField(base):
    """The dynamically created Field class.
    """

    __metaclass__ = DynaFieldMetaclass
    dynaproperties = properties

    def __init__(self):
      """Pass through the init args to super.
      """

      super(DynaField, self).__init__(**init_args)

  return DynaField
