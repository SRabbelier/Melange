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

from django import newforms as forms
from django.newforms import util
from django.newforms import widgets
from django.utils import html
from django.utils import simplejson
from django.utils import safestring


class ReadOnlyInput(forms.widgets.Input):
  """Read only input widget.
  """
  input_type = 'text'

  def render(self, name, value, attrs=None):
    """Render ReadOnlyInput widget as HTML.
    """
    attrs['readonly'] = 'readonly'
    return super(ReadOnlyInput, self).render(name, value, attrs)


class TinyMCE(forms.widgets.Textarea):
  """TinyMCE widget. 
  
  Requires to include tiny_mce_src.js in your template. Widget can be
  customized by overwriting or adding extra options to mce_settings
  dictionary

  You can set TinyMCE widget for particular form field using code below:
    class ExampleForm(forms_helpers.DbModelForm):
      content = forms.fields.CharField(widget=custom_widgets.TinyMCE())
  
  You can include tiny_mce_src.js in your template using:
    {% block scripts %}
  	  <script type="text/javascript" src="/tiny_mce/tiny_mce_src.js"></script>
    {% endblock %}
  """ 
  DEF_MCE_SETTINGS = { 'mode': "exact",
                       'theme': "simple",
                       'theme_advanced_toolbar_location': "top",
                       'theme_advanced_toolbar_align': "center"}

  mce_settings = DEF_MCE_SETTINGS.copy()

  TINY_MCE_HTML_FMT = u'''\
<textarea %(attrs)s>%(value)s</textarea>
<script type="text/javascript">
tinyMCE.init(%(settings_json)s)
</script>'''
  
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
