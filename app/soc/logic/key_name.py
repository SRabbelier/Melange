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

"""Functions for composing Model entity key names.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


import soc.models.site_settings
import soc.models.user


def nameSiteSettings(path):
  """Returns a SiteSettings key name constructed from a supplied path."""
  return '%s:%s' % (soc.models.site_settings.SiteSettings.__name__, path)


def nameUser(email):
  """Returns a User key name constructed from a supplied email address."""
  return '%s:%s' % (soc.models.user.User.__name__, email)
