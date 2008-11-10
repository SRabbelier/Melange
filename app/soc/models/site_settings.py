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
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext_lazy

import soc.models.home_settings


class SiteSettings(soc.models.home_settings.HomeSettings):
  """Model of a SiteSettings, which stores per site configuration."""

  #: Valid Google Analytics tracking number, if entered every page
  #: is going to have Google Analytics JS initialization code in 
  #: the footer with the given tracking number.
  ga_tracking_num = db.StringProperty(verbose_name=ugettext_lazy('Google Analytics'))
  ga_tracking_num.help_text = ugettext_lazy(
      'Valid Google Analytics tracking number. If the number is '
      'entered every page is going to have Google Analytics '
      'initialization code in footer.')

  #: Valid Google Maps API Key. Used to embed Google Maps.
  gmaps_api_key = db.StringProperty(verbose_name=ugettext_lazy('Google Maps'))
  gmaps_api_key.help_text = ugettext_lazy(
      'Valid Google Maps API Key. This key is used for '
      'embedding Google Maps into the website.')
