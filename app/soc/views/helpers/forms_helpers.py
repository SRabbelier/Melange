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
  '"Chen Lunpeng" <forever.clp@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.ext.db import djangoforms

from django import newforms as forms
from django.utils import safestring


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


class SelectQueryArgForm(forms.Form):
  """URL query argument change control implemented as a Django form.
  """

  ONCHANGE_JAVASCRIPT_FMT = '''
<script type="text/javascript"> 
  function changeArg_%(arg_name)s(item) 
  {
    var idx=item.selectedIndex;
    item.selected=true;
    var value=item.value 
    var url = location.href 
    var reg = /%(arg_name)s=\d+/ 
    url = url.replace(reg, "%(arg_name)s="+value) 
    if(url.match(reg))
      document.location.href = url 
   else
      document.location.href = "%(page_path)s?%(arg_name)s="+value; 
  }
</script>
'''

  def __init__(self, page_path, arg_name, choices, field_name,
               *form_args, **form_kwargs):
    """
    Args:
      page_path: (usually request.path)
      arg_name: the URL query parameter that determines which choice is
        selected in the selection control
      choices: list (or tuple) of value/label string two-tuples, for example:
        (('10', '10 items per page'), ('25', '25 items per page'))
      field_name: name of the selection field in the form
      *form_args: positional arguments passed on to the Form base
        class __init__()
      *form_kwargs: keyword arguments passed on to the Form base
        class __init__()
    """
    super(SelectQueryArgForm, self).__init__(*form_args, **form_kwargs)
    
    self._script = safestring.mark_safe(self.ONCHANGE_JAVASCRIPT_FMT % {
        'arg_name': arg_name, 'page_path': page_path,})
 
    onchange_js_call = 'changeArg_%s(this)' % arg_name
    
    self.fields[field_name] = forms.ChoiceField(
        label='', choices=choices,
        widget=forms.widgets.Select(attrs={'onchange': onchange_js_call}))
      
  def as_table(self):
    """Returns form rendered as HTML <tr> rows -- with no <table></table>.
    
    Prepends <script> section with onchange function included.
    """
    return self._script + super(SelectQueryArgForm, self).as_table()

  def as_ul(self):
    """Returns form rendered as HTML <li> list items -- with no <ul></ul>.
    
    Prepends <script> section with onchange function included.
    """
    return self._script + super(SelectQueryArgForm, self).as_ul()

  def as_p(self):
    """Returns form rendered as HTML <p> paragraphs.
    
    Prepends <script> section with onchange function included.
    """
    return self._script + super(SelectQueryArgForm, self).as_p()


DEF_SELECT_QUERY_ARG_FIELD_NAME_FMT = 'select_query_arg_%(arg_name)s'

def makeSelectQueryArgForm(
    request, arg_name, initial_value, choices,
    field_name_fmt=DEF_SELECT_QUERY_ARG_FIELD_NAME_FMT):
  """Wrapper that creates a customized SelectQueryArgForm.

  Args:
    request: the standard Django HTTP request object
    arg_name: the URL query parameter that determines which choice is
      selected in the selection control
    initial_value: the initial value of the selection control
    choices: list (or tuple) of value/label string two-tuples, for example:
      (('10', '10 items per page'), ('25', '25 items per page'))
    field_name_fmt: optional form field name format string; default is
      DEF_SELECT_QUERY_ARG_FIELD_NAME_FMT; contains these named format
      specifiers:
        arg_name: replaced with the arg_name argument

  Returns:
    a Django form implementing a query argument selection control, for
    insertion into a template
  """
  field_name = field_name_fmt % {'arg_name': arg_name}
  return SelectQueryArgForm(request.path, arg_name, choices, field_name,
                            initial={field_name: initial_value})
