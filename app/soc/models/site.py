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

"""This module contains the Site Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.ext import db

from django.utils.translation import ugettext

import soc.models.presence_with_tos


class Site(soc.models.presence_with_tos.PresenceWithToS):
  """Model of a Site, which stores per site configuration.

  The Site Model stores configuration information unique to the Melange
  web site as a whole (in addition to any configuration that is common to
  any "presence" on the site, such as a Group or Program).
  """

  #: The official name of the site
  site_name = db.StringProperty(default="Melange",
      verbose_name=ugettext('Site Name'))
  site_name.help_text = ugettext('The official name of the Site')

  #: Valid Google Analytics tracking number, if entered every page
  #: is going to have Google Analytics JS initialization code in 
  #: the footer with the given tracking number.
  ga_tracking_num = db.StringProperty(
      verbose_name=ugettext('Google Analytics'))
  ga_tracking_num.help_text = ugettext(
      'Valid Google Analytics tracking number. If the number is '
      'entered every page is going to have Google Analytics '
      'initialization code in footer.')

  #: Valid Google Maps API Key. Used to embed Google Maps.
  gmaps_api_key = db.StringProperty(verbose_name=ugettext('Google Maps'))
  gmaps_api_key.help_text = ugettext(
      'Valid Google Maps API Key. This key is used for '
      'embedding Google Maps into the website.')

  #: No Reply Email address used for sending notification emails to site users 
  noreply_email = db.EmailProperty(verbose_name=ugettext('No reply email'))
  noreply_email.help_text = ugettext(
      'No reply email address is used for sending emails to site users. '
      'Email address provided in this field needs to be added as Developer '
      'in GAE admin console.')
