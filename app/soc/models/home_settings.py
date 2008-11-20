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

"""This module contains the HomeSettings Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
]


import polymodel

from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.document


class HomeSettings(polymodel.PolyModel):
  """Model that stores settings for various Home pages.

  This Model is the basis for more specific "/home" view settings, such as
  SiteSettings, ProgramSettings, etc.
  """

  #: Reference to Document containing the contents of the "/home" page
  home = db.ReferenceProperty(
    reference_class=soc.models.document.Document,
    collection_name='home')
  home.help_text = ugettext_lazy(
      'Document to be used as the "/home" page static contents.')

  #: Valid ATOM or RSS feed url or None if unused. Feed entries are shown 
  #: on the site page using Google's JavaScript blog widget  
  feed_url = db.LinkProperty(verbose_name=ugettext_lazy('Feed URL'))
  feed_url.help_text = ugettext_lazy(
      'The URL should be a valid ATOM or RSS feed. '
      'Feed entries are shown on the home page.')

  #: Required path, prepended to a "link ID" to form the Setting URL.
  partial_path = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Settings partial path'))
  partial_path.help_text = ugettext_lazy(
    'path portion of URLs for Settings, prepended to link ID')

  #: Required link ID, appended to a "path" to form the Setting URL.
  link_id = db.StringProperty(required=True,
      verbose_name=ugettext_lazy('Setttings link ID'))
  link_id.help_text = ugettext_lazy('link ID for Settings used in URLs')
