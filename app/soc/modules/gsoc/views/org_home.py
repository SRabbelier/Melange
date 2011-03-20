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

"""Module containing the views for GSoC Homepage Application.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from django.conf.urls.defaults import url

from soc.views.template import Template

from soc.modules.gsoc.logic.models.student_project import logic as sp_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import lists
from soc.modules.gsoc.views.helper import url_patterns


class Contact(Template):
  """Organization Contact template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    return {
      'organization': self.data.organization,
    }

  def templatePath(self):
    return "v2/modules/gsoc/org_home/_contact.html"


class ProjectList(Template):
  """Template for list of student projects accepted under the organization.
  """

  def __init__(self, request, data):
    self.request = request
    self.data = data

    list_config = lists.ListConfiguration()
    list_config.addColumn('student', 'Student',
                          lambda entity, *args: entity.student.user.name)
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('mentor', 'Mentor',
                          lambda entity, *args: entity.mentor.user.name)
    self._list_config = list_config

  def context(self):
    list = lists.ListConfigurationResponse(
        self._list_config, idx=0,
        description='List of projects accepted into %s' % (
            self.data.organization.name))

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
      fields = {'scope': self.data.organization,
                'status': 'accepted'}
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, sp_logic,
          fields)
      return response_builder.build()
    else:
      return None

  def templatePath(self):
    return "v2/modules/gsoc/org_home/_project_list.html"


class OrgHome(RequestHandler):
  """View methods for Organization Home page.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/org_home/base.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'^gsoc/org/%s$' % url_patterns.ORG, self,
            name='gsoc_org_home')
    ]

  def checkAccess(self):
    """Access checks for GSoC Organization Application.
    """
    pass

  def context(self):
    """Handler to for GSoC Organization Home page HTTP get request.
    """
    organization = self.data.organization

    return {
        'page_name': '%s - Homepage' % organization.short_name,
        'organization': organization,
        'contact': Contact(self.data),
        'tags': organization.tags_string(organization.org_tag),
        'project_list': ProjectList(self.request, self.data),
    }
