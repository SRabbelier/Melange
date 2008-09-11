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

import django.newforms as forms
from django.newforms.widgets import flatatt
from django.newforms.util import smart_unicode
from django.utils.html import escape
from django.utils import simplejson
from django.utils.safestring import mark_safe

class TinyMCE(forms.Textarea):
    """
    TinyMCE widget. requires you include tiny_mce_src.js in your template
    you can customize the mce_settings by overwriting instance mce_settings,
    or add extra options using update_settings
    """ 

    mce_settings = dict(
        mode = "exact",
        theme = "simple",
        theme_advanced_toolbar_location = "top",
        theme_advanced_toolbar_align = "center",
    )    

    def update_settings(self, custom):
        return_dict = self.mce_settings.copy()
        return_dict.update(custom)
        return return_dict

    def render(self, name, value, attrs=None):
        if value is None:
          value = ''
        value = smart_unicode(value)
        final_attrs = self.build_attrs(attrs, name=name)

        self.mce_settings['elements'] = "id_%s" % name
        mce_json = simplejson.JSONEncoder().encode(self.mce_settings)

        return mark_safe(u'<textarea%s>%s</textarea> \
                <script type="text/javascript">\
                tinyMCE.init(%s)</script>' % (flatatt(final_attrs), 
                                              escape(value), 
                                              mce_json))
