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
  ]


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
    if self.current_timeline == 'org_signup_period':
      img_url = "/soc/content/images/v2/gsoc/image-map-org-apps.png"
    elif self.current_timeline == 'student_signup_period':
      img_url = "/soc/content/images/v2/gsoc/image-map-student-apps.png"
    elif self.current_timeline == 'program_period':
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

  def __init__(self, data, current_timeline):
    self.data = data
    self.current_timeline = current_timeline

  def context(self):
    return {
        'current_timeline': self.current_timeline,
    }

  def templatePath(self):
    return "v2/modules/gsoc/homepage/_apply.html"


class Homepage(RequestHandler):
  """Encapsulate all the methods required to generate GSoC Home page.
  """

  def getProjectDetailsRedirect(self, student_project):
    """Returns the URL to the Student Project.

    Args:
      student_project: entity which represents the Student Project
    """
    return '/gsoc/student_project/show/%s' % student_project.key().id_or_name()

  def templatePath(self):
    return 'v2/modules/gsoc/homepage/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        (r'^gsoc/homepage/%s$' % url_patterns.PROGRAM, self)
    ]

  def checkAccess(self):
    """Access checks for GSoC Home page.
    """
    pass

  def context(self):
    """Handler to for GSoC Home page HTTP get request.
    """

    current_timeline = timeline_logic.getCurrentTimeline(
        self.data.program_timeline, self.data.org_app)

    program = self.data.program

    featured_project = sp_logic.getFeaturedProject(current_timeline, program)

    return {
        'timeline': Timeline(self.data, current_timeline).render(),
        'apply': Apply(self.data, current_timeline).render(),
        'featured_project':featured_project,
        'featured_project_url': self.getProjectDetailsRedirect(
            featured_project),
        'page_name': 'Home page',
        'program': program,
    }
