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

"""Module containing enhanced db.Model classes.

The classes in this module are intended to serve as base classes for all
Melange Datastore Models.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
]


from google.appengine.ext import db

from soc.views import helper

import soc.views.helper.forms


class ModelWithFieldAttributes(db.Model):
  """A db.Model extension that provides access to Model properties attributes.
  
  Due to the way the Property class in Google App Engine implements __get__()
  and __set__(), it is not possible to access attributes of Model properties,
  such as verbose_name, from within a Django template.  This class works
  around that limitation by creating an inner Form class per Model class,
  since an unbound Form object contains (most of?) the property attributes
  attached to each corresponding Form field.
  
  Some are attributes are renamed during the conversion from a Model Property
  to a Form field; for example, verbose_name becomes label.  This is tolerable
  because any actual Form code refers to these new names, so they are should
  be familiar to view creators.  
  """

  _fields_cache = None
  
  @classmethod
  def fields(cls):
    """Called by the Django template engine during template instantiation.
    
    Since the attribute names use the Form fields naming instead of the
    Property attribute naming, accessing, for example:
      {{ entity.property.verbose_name }}
    is accomplished using:
      {{ entity.fields.property.label }}
    
    Args:
      cls: Model class, so that each Model class can create its own
        unbound Form the first time fields() is called by the Django
        template engine.
 
    Returns:
      A (created-on-first-use) unbound Form object that can be used to
      access Property attributes that are not accessible from the
      Property itself via the Model entity.
    """
    if not cls._fields_cache or (cls != cls._fields_cache.__class__.Meta.model):
      class FieldsProxy(helper.forms.DbModelForm):
        """Form used as a proxy to access User model properties attributes.
        """
      
        class Meta:
          """Inner Meta class that pairs the User Model with this "form".
          """
          #: db.Model subclass for which to access model properties attributes
          model = cls
      
      cls._fields_cache = FieldsProxy()

    return cls._fields_cache
