#!/usr/bin/env python2.5
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

"""Basic system information functions.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


import os
import settings

from soc.logic.models import site


def getRawHostname():
  """Returns the actual hostname.
  """

  return os.environ.get('HTTP_HOST', '')


def getHostname():
  """Returns the hostname, taking in account site hostname settings.
  """

  site_settings = site.logic.getSingleton()

  if site_settings.hostname:
    return site_settings.hostname

  return getRawHostname()

def isSecondaryHostname(request):
  """Returns if the current request is from the secondary hostname.
  """

  site_settings = site.logic.getSingleton()

  if not site_settings.hostname:
    return False

  return getRawHostname().find(site_settings.hostname) >= 0

def getAppVersion():
  """Returns the Google App Engine "version" of the running instance.
  """

  return os.environ.get('CURRENT_VERSION_ID')


def getMelangeVersion():
  """Returns the Melange part of the GAE version.
  """

  return getAppVersion().split('.', 1)[0]


def isLocal():
  """Returns True if Melange application is running locally.
  
  "Local mode" is currently determined from settings.DEBUG but may become
  more sophisticated in the future.
  """

  return settings.DEBUG


def isDebug():
  """Returns True if Melange application is running in "debug mode".

  "Debug mode" is currently enabled if running locally or if the
  current Melange version is 'devvin'.
  """

  return isLocal() or getMelangeVersion() == 'devvin'
