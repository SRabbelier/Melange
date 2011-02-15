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


from django.template import loader

from soc.modules.gsoc.logic.models.timeline import logic as timeline_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class Homepage(RequestHandler):
  """Encapsulate all the methods required to generate GSoC Home page.
  """

  def __init__(self, template_path=None):
    """Construct the instance variables required for the GSoC Home page view.
    """
    if not template_path:
      template_path = 'v2/modules/gsoc/homepage/base.html'

    super(Homepage, self).__init__(template_path=template_path)

  def getDjangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    patterns = [
         (r'^gsoc/homepage/%(program_key)s$' % {
             'program_key': url_patterns.PROGRAM}, self)]
    return patterns

  def checkAccess(self):
    """Access checks for GSoC Home page.
    """
    return

  def get(self):
    """Handler to for GSoC Home page HTTP get request.
    """

    program = self.data.program

    context = {
        'page_name': 'Home page',
        'current_timeline': timeline_logic.getCurrentTimeline(program),
        }

    content = loader.render_to_string(self.template_path, dictionary=context)
    self.response.write(content)
