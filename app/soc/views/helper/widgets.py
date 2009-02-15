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

"""Custom widgets used for form fields.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import copy

from django import forms
from django.forms import util
from django.forms import widgets
from django.utils import html
from django.utils import simplejson
from django.utils import safestring

from soc.logic import dicts


class ReadOnlyInput(forms.widgets.Input):
  """Read only input widget.
  """

  input_type = 'text'

  def render(self, name, value, attrs=None):
    """Render ReadOnlyInput widget as HTML.
    """

    attrs['readonly'] = 'readonly'
    attrs['class'] = 'plaintext'

    return super(ReadOnlyInput, self).render(name, value, attrs)


class PlainTextWidget(forms.widgets.Widget):
  """Read only input widget.
  """

  def render(self, name, value, attrs=None):
    """Render ReadOnlyInput widget as HTML.
    """

    return str(value) if value else ""


class FullTinyMCE(forms.widgets.Textarea):
  """TinyMCE widget. 
  
  Requires to include tiny_mce_src.js in your template. Widget can be
  customized by overwriting or adding extra options to mce_settings
  dictionary

  You can set TinyMCE widget for particular form field using code below:
    class ExampleForm(helper.forms.BaseForm):
      content = forms.fields.CharField(widget=helper.widgets.TinyMCE())
  
  You can include tiny_mce_src.js in your template using:
    {% block scripts %}
  	  <script type="text/javascript" src="/tiny_mce/tiny_mce_src.js"></script>
    {% endblock %}
  """ 

  features1 = ("bold,italic,underline,strikethrough,|,"
               "forecolor,backcolor,blockquote,|"
              ",justifyleft,justifycenter,justifyright,justifyfull,|,"
              "fontselect, fontsizeselect,formatselect")

  features2 = ("newdocument,|,bullist,numlist,|,outdent,indent,|,undo,redo,|"
      ",link,unlink,anchor,image,cleanup,help,code,hr,removeformat,visualaid,|,"
      "sub,sup,|,charmap,"
      "")

  DEF_MCE_SETTINGS = {'mode': "exact",
                      'theme': "advanced",
                      'theme_advanced_buttons1': features1,
                      'theme_advanced_buttons2': features2,
                      'theme_advanced_buttons3': '',
                      'theme_advanced_toolbar_location': "top",
                      'theme_advanced_toolbar_align': "left"}


  TINY_MCE_HTML_FMT = u'''\
<textarea %(attrs)s>%(value)s</textarea>
<script type="text/javascript">
tinyMCE.init(%(settings_json)s)
</script>'''

  def __init__(self, mce_settings=None, *args, **kwargs):
    """Initialize TinyMCE widget with default or customized settings.
    
    Args:
      mce_settings: dict with TinyMCE widget settings
      *args, **kwargs:  passed through to parent __init__() constructor
    """

    super(forms.widgets.Textarea, self).__init__(*args, **kwargs)
    self.mce_settings = self.DEF_MCE_SETTINGS
  
  def render(self, name, value, attrs=None):
    """Render TinyMCE widget as HTML.
    """
    if value is None:
      value = ''
    value = util.smart_unicode(value)
    final_attrs = self.build_attrs(attrs, name=name)
    
    self.mce_settings['elements'] = "id_%s" % name
      
    # convert mce_settings from dict to JSON
    mce_json = simplejson.JSONEncoder().encode(self.mce_settings)

    return safestring.mark_safe(self.TINY_MCE_HTML_FMT % 
        {'attrs': widgets.flatatt(final_attrs),
         'value': html.escape(value), 
         'settings_json':  mce_json})


class TinyMCE(FullTinyMCE):
  """Regular version of TinyMce
  """

  def __init__(self, *args, **kwargs):
    """
    """

    super(TinyMCE, self).__init__(*args, **kwargs)
    keys = ['mode', 'theme', 'theme_advanced_toolbar_location',
            'theme_advanced_toolbar_align']
    self.mce_settings = dicts.filter(self.mce_settings, keys)

class ReferenceField(forms.CharField):
  """Widget for selecting a reference to an Entity.
  """

  def __init__(self, reference_url, filter=None, filter_fields=None,
               *args, **kwargs):
    """Initializes the widget with the specified url and filter.
    """

    self.rf = {}
    self.rf['reference_url'] = reference_url
    self.rf['filter'] = filter if filter else []
    self.rf['filter_fields'] = filter_fields if filter_fields else {}
    super(ReferenceField, self).__init__(*args, **kwargs)


class AgreementField(widgets.Widget):
  """Widget for selecting a reference to an Entity.
  """

  HTML_CODE = """
  <span style="width:450px" colspan="4">
    <div id="ToS" style="overflow:auto;height:200px">
      %s
    </div>
  </span>
  """

  def __init__(self, *args, **kwargs):
    self.text = "No Agreement Text Specified"
    super(AgreementField, self).__init__(*args, **kwargs)

  def render(self, name, value, attrs=None):
    """
    """

    value = self.text.replace('\n', '<BR />')
    result = self.HTML_CODE % value
    return result
