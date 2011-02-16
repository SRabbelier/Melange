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
from soc.views.helper import lists
from soc.views.template import Template

from soc.modules.gsoc.logic.models.student_project import logic as \
    project_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class Dashboard(RequestHandler):
  """View for the participant dashboard.
  """

  def djangoURLPatterns(self):
    """The URL pattern for the dashboard.
    """
    return [(r'^gsoc/dashboard/%s$' % url_patterns.PROGRAM, self)]

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
    components = []
    if self.data.student:
      components = self._getStudentComponents()
    elif self.data.mentors or self.data.org_admins:
      components = self._getOrgMemberComponents()

    context = {}
    context['page_name'] = self.data.program.name
    context['user'] = self.data.user
    context['alert_msg'] = 'Default Messsage goes here'
    context['components'] = components

    return context

  def _getStudentComponents(self):
    """Get the dashboard components for a student.
    """
    # Add all the proposals of this current user
    components = [MyProposalsComponent(self)]

    fields = {'student': self.data.student}
    project = project_logic.getForFields(fields, unique=True)
    if project:
      # Add a component to show all the projects
      #MyProjectsComponent()
      # Add a component to show the evaluations
      #MyEvaluationsComponent()
      pass

    return components

  def _getOrgMemberComponents(self):
    """Get the dashboard components for Organization members.
    """
    # Figure out which orgs are involved
    #org_roles = self.data.mentors + self.data.org_admins
    pass


class MyProposalsComponent(Template):
  """Component for listing all the proposals of the current Student.
  """

  def __init__(self, handler):
    """Initializes the template location, name and title of this component.
    """
    self._handler = handler

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/proposals_component.html'

  def context(self):
    """Returns the context of this component.
    """
    from soc.modules.gsoc.views.models.student_proposal import view

    list_config = lists.getListGenerator(self._handler.request,
                                         view.getParams())
    return {
        'name': "proposals",
        'title': "PROPOSALS",
        'lists': Lists([list_config]),
    }
