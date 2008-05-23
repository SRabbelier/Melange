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

"""Helpers used to display various views that are forms.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.ext.db import djangoforms


class DbModelForm(djangoforms.ModelForm):
  """Subclass of Django ModelForm that fixes some label and help_text issues.

  The default behavior of ModelForm is to use the verbose_name in all
  lowercase, capitalizing only the first character, as the displayed field
  label.  This class uses verbose_name unaltered as the visible field label
  instead.

  The Property classes used by the App Engine Datastore do not have a
  help_text parameter to their constructor.  In a Model class, a help_text
  attribute *can* be added to the property after it is created, but the
  help text will not be automatically passed along to the Django ModelForm.
  This class detects the presence of a help_text attribute and adds it to
  the corresponding form field object.

  ugettext_lazy() proxies used for internationalization in the Model will
  still work correctly with this new behavior, as long as the original
  strings are used as the translation keys.
  """

  def __init__(self, *args, **kwargs):
    """Fixes label and help_text issues after parent initialization.

    Args:
      *args, **kwargs:  passed through to parent __init__() constructor
    """
    super(DbModelForm, self).__init__(*args, **kwargs)

    for field_name in self.fields.iterkeys():
      # Since fields can be added only to the ModelForm subclass, check to
      # see if the Model has a corresponding field first.
      if hasattr(self.Meta.model, field_name):
        model_prop = getattr(self.Meta.model, field_name)

        # Check if the Model property defined verbose_name, and copy that
        # verbatim to the corresponding field label.
        if hasattr(model_prop, 'verbose_name'):
          self.fields[field_name].label = model_prop.verbose_name

        # Check if the Model property added help_text, and copy that verbatim
        # to the corresponding field help_text.
        if hasattr(model_prop, 'help_text'):
          self.fields[field_name].help_text = model_prop.help_text
