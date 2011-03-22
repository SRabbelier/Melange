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


from google.appengine.api import users

from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse

from soc.logic import dicts
from soc.logic.exceptions import AccessViolation
from soc.logic.helper import timeline as timeline_helper
from soc.views.template import Template

from soc.modules.gsoc.logic.models.timeline import logic as timeline_logic
from soc.modules.gsoc.logic.models.student_project import logic as sp_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import lists
from soc.modules.gsoc.views.helper import url_patterns


class Apply(Template):
  """Apply template.
  """

  def __init__(self, data, current_timeline):
    self.data = data
    self.current_timeline = current_timeline

  def context(self):
    context = {
        'request_data': self.data,
        'current_timeline': self.current_timeline,
        'organization': self.data.organization,
    }
    if not self.data.profile:
      kwargs = dicts.filter(self.data.kwargs, ['sponsor', 'program'])
      kwargs['role'] = 'student'
      context['student_profile_link'] = reverse('create_gsoc_profile', kwargs=kwargs)
      kwargs['role'] = 'mentor'
      context['mentor_profile_link'] = reverse('create_gsoc_profile', kwargs=kwargs)
      kwargs['role'] = 'org_admin'
      context['org_admin_profile_link'] = reverse('create_gsoc_profile', kwargs=kwargs)
    if self.data.student_info:
      kwargs_org = dicts.filter(self.data.kwargs, ['sponsor', 'program', 'organization'])
      context['submit_proposal_link'] = reverse('submit_gsoc_proposal', kwargs=kwargs_org)
    return context

  def templatePath(self):
    return "v2/modules/gsoc/org_home/_apply.html"


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

  def jsonContext(self):
    """Handler for JSON requests.
    """
    list_content = ProjectList(self.request, self.data).getListData()

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    """Handler to for GSoC Organization Home page HTTP get request.
    """
    current_timeline = timeline_logic.getCurrentTimeline(
        self.data.program_timeline, self.data.org_app)

    organization = self.data.organization

    context = {
        'page_name': '%s - Homepage' % organization.short_name,
        'organization': organization,
        'apply': Apply(self.data, current_timeline),
        'contact': Contact(self.data),
        'tags': organization.tags_string(organization.org_tag),
    }

    if timeline_helper.isAfterEvent(
        self.data.program_timeline, 'accepted_students_announced_deadline'):
      context['project_list'] = ProjectList(self.request, self.data)

    return context
