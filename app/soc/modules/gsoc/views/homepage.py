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
    return {
        'current_timeline': self.current_timeline,
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

    return {
        'timeline': Timeline(self.data, current_timeline).render(),
        'apply': Apply(self.data, current_timeline).render(),
        'page_name': 'Home page',
        'program': self.data.program,
    }
