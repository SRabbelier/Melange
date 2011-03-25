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

"""Module containing the views for GSoC home page.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users

from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

from soc.logic import dicts
from soc.views.template import Template

from soc.modules.gsoc.logic.models.student_project import logic as sp_logic
from soc.modules.gsoc.logic.models.timeline import logic as timeline_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class Timeline(Template):
  """Timeline template.
  """

  def __init__(self, data, current_timeline):
    self.data = data
    self.current_timeline = current_timeline

  def context(self):
    if self.current_timeline == 'kickoff_period':
      img_url = "/soc/content/images/v2/gsoc/image-map-kickoff.png"
    elif self.current_timeline in ['org_signup_period', 'orgs_announced_period']:
      img_url = "/soc/content/images/v2/gsoc/image-map-org-apps.png"
    elif self.current_timeline == 'student_signup_period':
      img_url = "/soc/content/images/v2/gsoc/image-map-student-apps.png"
    elif self.current_timeline == 'coding_period':
      img_url = "/soc/content/images/v2/gsoc/image-map-on-season.png"
    else:
      img_url = "/soc/content/images/v2/gsoc/image-map-off-season.png"

    return {
        'img_url': img_url
    }

  def templatePath(self):
    return "v2/modules/gsoc/homepage/_timeline.html"


class Apply(Template):
  """Apply template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
    context = {}
    accepted_orgs = None

    if self.data.timeline.orgsAnnounced():
      accepted_orgs = reverse('gsoc_accepted_orgs', kwargs=kwargs)
      context['accepted_orgs_link'] = accepted_orgs

    context['org_signup'] = self.data.timeline.orgSignup()  
    context['student_signup'] = self.data.timeline.studentSignup()

    signup = self.data.timeline.orgSignup() or self.data.timeline.studentSignup()

    if signup and not self.data.gae_user:
      context['login_link'] = users.create_login_url(self.data.full_path)
    if signup and not self.data.profile:
      if self.data.timeline.orgSignup():
        kwargs['role'] = 'org_admin'
      else:
        kwargs['role'] = 'student'
      context['profile_link'] = reverse('create_gsoc_profile', kwargs=kwargs)

    if self.data.timeline.studentSignup() and self.data.profile:
      context['apply_link'] = accepted_orgs

    context['apply_block'] = signup or accepted_orgs

    return context

  def templatePath(self):
    return "v2/modules/gsoc/homepage/_apply.html"


class FeaturedProject(Template):
  """Featured project template
  """

  def __init__(self, data, featured_project):
    self.data = data
    self.featured_project = featured_project

  def context(self):
    redirect = self.data.redirect

    featured_project_url = redirect.projectDetails(self.featured_project).url()

    return {
      'featured_project': self.featured_project,
      'featured_project_url': featured_project_url,
    }

  def templatePath(self):
    return "v2/modules/gsoc/homepage/_featured_project.html"


class ConnectWithUs(Template):
  """Connect with us template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    return {
      'program': self.data.program,
    }

  def templatePath(self):
    return "v2/modules/gsoc/homepage/_connect_with_us.html"


class Homepage(RequestHandler):
  """Encapsulate all the methods required to generate GSoC Home page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/homepage/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'^gsoc/homepage/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_homepage')
    ]

  def checkAccess(self):
    """Access checks for GSoC Home page.
    """
    pass

  def context(self):
    """Handler to for GSoC Home page HTTP get request.
    """

    current_timeline = self.data.timeline.currentPeriod()

    featured_project = sp_logic.getFeaturedProject(
        current_timeline, self.data.program)

    context = {
        'timeline': Timeline(self.data, current_timeline),
        'apply': Apply(self.data),
        'connect_with_us': ConnectWithUs(self.data),
        'page_name': 'Home page',
        'program': self.data.program,
    }

    if featured_project:
      context['featured_project'] = FeaturedProject(
        self.data, featured_project)

    return context
