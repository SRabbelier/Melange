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
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.core.urlresolvers import reverse

from soc.logic import dicts


# Redirects for the hard-coded sidebar menu items
def showDocument(doc):
  """Returns the show redirect for the specified document.

  Returns None if doc is not set.
  """
  if not doc:
    return None

  args = [doc.prefix, doc.scope_path + '/', doc.link_id]
  try:
    reversed = reverse('show_gsoc_document', args=args)
    return reversed
  except Exception ,e:
    print e
    return None


def acceptedOrgs(data):
  """Returns the redirect for list all GSoC projects.
  """

  kwargs = dicts.filter(data.kwargs, ['sponsor', 'program'])
  return reverse('gsoc_accepted_orgs', kwargs=kwargs)


def allProjects(data):
  """Returns the redirect for list all GSoC projects.
  """

  kwargs = dicts.filter(data.kwargs, ['sponsor', 'program'])
  return reverse('gsoc_accepted_projects', kwargs=kwargs)


def homepage(data):
  """Returns the redirect for the homepage for the current GSOC program.
  """
  kwargs = dicts.filter(data.kwargs, ['sponsor', 'program'])
  return reverse('gsoc_homepage', kwargs=kwargs)


def dashboard(data):
  """Returns the redirect for the dashboard page for the current GSOC program.
  """
  kwargs = dicts.filter(data.kwargs, ['sponsor', 'program'])
  return reverse('gsoc_dashboard', kwargs=kwargs)


def projectDetails(student_project):
  """Returns the URL to the Student Project.

  Args:
    student_project: entity which represents the Student Project
  """
  # TODO: Use django reverse function from urlresolver once student_project
  # view is converted to the new infrastructure
  return '/gsoc/student_project/show/%s' % student_project.key().id_or_name()
