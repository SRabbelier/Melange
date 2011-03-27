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

"""Module containing the views for listing all the projects accepted
into a GSoC program.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from django.conf.urls.defaults import url

from soc.logic.exceptions import AccessViolation
from soc.views.template import Template

from soc.modules.gsoc.logic.models.student_project import logic as sp_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import lists
from soc.modules.gsoc.views.helper import url_patterns


class ProjectList(Template):
  """Template for listing the student projects accepted in the program.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration()
    list_config.addColumn('student', 'Student',
                          lambda entity, *args: entity.student.user.name)
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org', 'Organization',
                          lambda entity, *args: entity.scope.name)
    list_config.addColumn('mentor', 'Mentor',
                          lambda entity, *args: entity.mentor.user.name)
    list_config.setDefaultSort('student')
    self._list_config = list_config

  def context(self):
    list = lists.ListConfigurationResponse(
        self._list_config, idx=0,
        description='List of projects accepted into %s' % (
            self.data.program.name))

    return {
        'lists': [list],
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      fields = {'program': self.data.program,
                'status': 'accepted'}
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, sp_logic,
          fields, prefetch=['student', 'scope', 'mentor'])
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gsoc/projects_list/_project_list.html"


class ListProjects(RequestHandler):
  """View methods for listing all the projects accepted into a program.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/projects_list/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'^gsoc/list_projects/%s$' % url_patterns.PROGRAM, self,
            name='gsoc_accepted_projects')
    ]

  def checkAccess(self):
    """Access checks for the view.
    """
    self.check.acceptedStudentsAnnounced()

  def jsonContext(self):
    """Handler for JSON requests.
    """
    list_content = ProjectList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    """Handler for GSoC Accepted Projects List page HTTP get request.
    """
    program = self.data.program

    return {
        'page_name': '%s - Accepted Projects' % program.short_name,
        'program_name': program.name,
        'project_list': ProjectList(self.request, self.data),
    }
