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
def getAboutPageRedirect(data):
  """Returns the redirect for the About page for the current GSoC program.
  """

  if data.program.about_page:
    return '/gsoc/document/%s' % data.program.about_page.key().name()


def getAllProjectsRedirect(data):
  """Returns the redirect for list all GSoC projects.
  """

  return '/gsoc/list_projects/%s' % data.program.key().name()


def getConnectRedirect(data):
  """Returns the redirect for the Connect page for the current GSoC program.
  """

  if data.program.connect_with_us_page:
    return '/gsoc/document/%s' % data.program.connect_with_us_page.key().name()


def getEventsRedirect(data):
  """Returns the redirect for the Events & Timeline page for the current
  GSoC program.
  """

  if data.program.events_page:
    return '/gsoc/document/%s' % data.program.events_page.key().name()


def getHelpRedirect(data):
  """Returns the redirect for the Help page for the current GSoC program.
  """

  if data.program.events_page:
    return '/gsoc/document/%s' % data.program.events_page.key().name()


def getHomepageRedirect(data):
  """Returns the redirect for the homepage for the current GSOC program.
  """
  return '/gsoc/homepage/%s' % data.program.key().name()


def getDashboardRedirect(data):
  """Returns the redirect for the dashboard page for the current GSOC program.
  """

  return '/gsoc/dashboard/%s' % data.program.key().name()


def getProjectDetailsRedirect(student_project):
  """Returns the URL to the Student Project.

  Args:
    student_project: entity which represents the Student Project
  """
  return '/gsoc/student_project/show/%s' % student_project.key().id_or_name()
