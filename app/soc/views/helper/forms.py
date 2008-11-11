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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.ext.db import djangoforms

from django import forms
from django.forms import forms as forms_in
from django.forms import util
from django.utils import encoding
from django.utils import safestring
from django.utils.encoding import force_unicode
from django.utils.html import escape
from django.utils.safestring import mark_safe


class CustomErrorList(util.ErrorList):
  """A collection of errors that knows how to display itself in various formats.
  
  This class has customized as_text method output which puts errors inside <span>
  with formfielderrorlabel class.
  """
  def __unicode__(self):
    return self.as_text()
  
  def as_text(self):
    """Returns error list rendered as text inside <span>."""
    if not self:
      return u''
    errors_text = u'\n'.join([u'%s' % encoding.force_unicode(e) for e in self])
    return u'<span class="formfielderrorlabel">%(errors)s</span><br />' % \
        {'errors': errors_text}


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


class BaseForm(DbModelForm):
  """Subclass of DbModelForm that extends as_table HTML output.
  
  BaseForm has additional class names in HTML tags for label and help text
  and those can be used in CSS files for look customization. The way the Form
  prints itself also has changed. Help text is displayed in the same row as 
  label and input.
  """
  
  DEF_NORMAL_ROW = u'<tr title="%(help_text)s"><td class=' \
      '"%(field_class_type)s">%(label)s</td><td>' \
      '%(errors)s%(field)s%(required)s</td></tr>'
  DEF_ERROR_ROW = u'<tr><td>&nbsp;</td><td class="formfielderror">%s</td></tr>'
  DEF_ROW_ENDER = '</td></tr>'
  DEF_REQUIRED_HTML = u'<td class="formfieldrequired">(required)</td>'
  DEF_HELP_TEXT_HTML = u'%s'

  def __init__(self, *args, **kwargs):
    """Parent class initialization.

    Args:
      *args, **kwargs:  passed through to parent __init__() constructor
    """
    super(BaseForm, self).__init__(error_class=CustomErrorList, *args, **kwargs)
  
  def _html_output_with_required(self, normal_row, error_row, row_ender, 
          help_text_html, required_html, errors_on_separate_row):
    """Helper function for outputting HTML.
    
    Used by as_table(), as_ul(), as_p(). Displays information
    about required fields.
    """
    # Errors that should be displayed above all fields.
    top_errors = self.non_field_errors()
    output, hidden_fields = [], []
    for name, field in self.fields.items():
      bf = forms_in.BoundField(self, field, name)
      # Escape and cache in local variable.
      bf_errors = self.error_class([escape(error) for error in bf.errors])
      if bf.is_hidden:
        if bf_errors:
          top_errors.extend([u'(Hidden field %s) %s' % \
              (name, force_unicode(e)) for e in bf_errors])
        hidden_fields.append(unicode(bf))
      else:
        if errors_on_separate_row and bf_errors:
          output.append(error_row % force_unicode(bf_errors))

        if bf.label:
          label = escape(force_unicode(bf.label))
          # Only add the suffix if the label does not end in
          # punctuation.
          if self.label_suffix:
            if label[-1] not in ':?.!':
              label += self.label_suffix
          label = bf.label_tag(label) or ''
        else:
          label = ''
        if field.help_text:
          help_text = help_text_html % force_unicode(field.help_text)
        else:
          help_text = u''

        if bf_errors:
          field_class_type = u'formfielderrorlabel'
        else:
          field_class_type = u'formfieldlabel'

        if field.required:
          required = required_html
        else:
          required = u''
        
        if errors_on_separate_row and bf_errors:
          errors = u''
        else:
          errors = force_unicode(bf_errors)
        
        output.append(normal_row % {'field_class_type': field_class_type,
                                    'errors': errors, 
                                    'label': force_unicode(label), 
                                    'field': unicode(bf),
                                    'required': required,
                                    'help_text': help_text})
    if top_errors:
      output.insert(0, error_row % force_unicode(top_errors))
    if hidden_fields: # Insert any hidden fields in the last row.
      str_hidden = u''.join(hidden_fields)
      if output:
        last_row = output[-1]
        # Chop off the trailing row_ender (e.g. '</td></tr>') and
        # insert the hidden fields.
        if not last_row.endswith(row_ender):
          # This can happen in the as_p() case (and possibly others
          # that users write): if there are only top errors, we may
          # not be able to conscript the last row for our purposes,
          # so insert a new, empty row.
          last_row = normal_row % {'errors': '', 'label': '',
                                   'field': '', 'help_text': ''}
          output.append(last_row)
        output[-1] = last_row[:-len(row_ender)] + str_hidden + row_ender
      else:
        # If there aren't any rows in the output, just append the
        # hidden fields.
        output.append(str_hidden)
    return mark_safe(u'\n'.join(output))

  def as_table(self):
    """Returns form rendered as HTML <tr> rows -- with no <table></table>."""
    
    return self._html_output_with_required(self.DEF_NORMAL_ROW,
                                           self.DEF_ERROR_ROW,
                                           self.DEF_ROW_ENDER,
                                           self.DEF_HELP_TEXT_HTML,
                                           self.DEF_REQUIRED_HTML, True)


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
