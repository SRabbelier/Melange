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

"""Module for the GSoC participant dashboard.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic.lists import Lists
from soc.views import out_of_band
from soc.views.helper import lists
from soc.views.template import Template

from soc.modules.gsoc.logic.models.student_project import logic as \
    project_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns
from soc.modules.gsoc.views.models.student_proposal import view as \
    proposal_view
from soc.modules.gsoc.views.models.student_project import view as \
    project_view

class Dashboard(RequestHandler):
  """View for the participant dashboard.
  """

  def djangoURLPatterns(self):
    """The URL pattern for the dashboard.
    """
    return [(r'^gsoc/dashboard/%s$' %url_patterns.PROGRAM, self)]

  def checkAccess(self):
    """Denies access if you don't have a role in the current program.
    """
    # TODO: Should raise exception when you are not a participant in the program
    return

  def templatePath(self):
    """Returns the path to the template.
    """
    return 'v2/modules/gsoc/dashboard/base.html'

  def context(self):
    """Handler for default HTTP GET request.
    """
    components = self._getActiveComponents()

    context = {}
    context['page_name'] = self.data.program.name
    context['user'] = self.data.user
    context['alert_msg'] = 'Default <strong>alert</strong> goes here'
    context['components'] = components

    return context

  def _getActiveComponents(self):
    """Returns the components that are active on the page.
    """
    if self.data.student:
      return self._getStudentComponents()
    elif self.data.mentors or self.data.org_admins:
      return self._getOrgMemberComponents()
    else:
      return []

  def get(self):
    """Handler for the GET request.
    """
    if lists.isDataRequest(self.request):
      components = self._getActiveComponents()

      list_data = None
      for component in components:
        list_data = component.getListData()
        if list_data:
          break

      if not list_data:
        raise out_of_band.AccessViolation("You do not have access to this data")
      self.response = lists.getResponse(self.request, list_data)
    else:
      super(Dashboard, self).get()

  def _getStudentComponents(self):
    """Get the dashboard components for a student.
    """
    # Add all the proposals of this current user
    components = [MyProposalsComponent(self.request, self.data)]

    fields = {'student': self.data.student}
    project = project_logic.getForFields(fields, unique=True)
    if project:
      # Add a component to show all the projects
      components.append(MyProjectsComponent(self.request, self.data))
      # Add a component to show the evaluations
      #MyEvaluationsComponent()

    return components

  def _getOrgMemberComponents(self):
    """Get the dashboard components for Organization members.
    """
    # Figure out which orgs are involved
    #org_roles = self.data.mentors + self.data.org_admins
    pass


class Component(Template):
  """Base component for the dashboard.
  """

  def __init__(self, request, data):
    """Initializes the component.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
    """
    self.request = request
    self.data = data

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    # by default no list is present
    return None


class MyProposalsComponent(Component):
  """Component for listing all the proposals of the current Student.
  """

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list_config = lists.getListGenerator(self.request,
                                         proposal_view.getParams(), idx=0)
    return {
        'name': 'proposals',
        'title': 'PROPOSALS',
        'lists': Lists([list_config]),
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      list_data = lists.getListData(self.request, proposal_view.getParams(),
                                   {'program': self.data.program,
                                    'scope': self.data.student})
      return list_data
    else:
      return None


class MyProjectsComponent(Component):
  """Component for listing all the projects of the current Student.
  """

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/list_component.html'

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 1:
      list_data = lists.getListData(self.request, project_view.getParams(),
                                   {'program': self.data.program,
                                    'student': self.data.student})
      return list_data
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list_config = lists.getListGenerator(self.request,
                                         project_view.getParams(), idx=1)
    return {
        'name': 'projects',
        'title': 'PROJECTS',
        'lists': Lists([list_config]),
    }