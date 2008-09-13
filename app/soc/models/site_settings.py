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

"""This module contains the SiteSettings Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]

from google.appengine.ext import db
from django.utils.translation import ugettext_lazy

class SiteSettings(db.Model):
  """Model of a SiteSettings, which stores per site configuration."""
  
  #: Valid ATOM or RSS feed url or None if unused. Feed entries are shown 
  #: on the site page using Google's JavaScript blog widget  
  feed_url = db.LinkProperty(
      verbose_name=ugettext_lazy('Feed URL'))
  feed_url.help_text = ugettext_lazy(
      'The URL should be a valid ATOM or RSS feed. '
      'Feed entries are shown on the site page.')
  

