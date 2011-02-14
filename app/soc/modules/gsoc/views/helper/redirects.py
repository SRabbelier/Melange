#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Redirect related methods.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


# Redirects for the hard-coded sidebar menu items
def getAboutPageRedirect():
  """Returns the redirect for the About page for the current GSoC program.
  """

  return 'gsoc/about'


def getAllProjectsRedirect():
  """Returns the redirect for list all GSoC projects.
  """

  return 'gsoc/list_projects'


def getConnectRedirect():
  """Returns the redirect for the Connect page for the current GSoC program.
  """

  return 'gsoc/connect'


def getEventsRedirect():
  """Returns the redirect for the Events & Timeline page for the current
  GSoC program.
  """

  return 'gsoc/events'


def getHelpRedirect():
  """Returns the redirect for the Help page for the current GSoC program.
  """

  return 'gsoc/help'
