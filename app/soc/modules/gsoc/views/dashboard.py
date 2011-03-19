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


from google.appengine.api import users

from django.conf.urls.defaults import url

from soc.logic.exceptions import AccessViolation
from soc.logic.helper import timeline as timeline_helper
from soc.views.template import Template

from soc.modules.gsoc.logic.models.org_app_survey import logic as \
    org_app_logic
from soc.modules.gsoc.logic.models.student_project import logic as \
    project_logic
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import lists
from soc.modules.gsoc.views.helper import url_patterns


class Dashboard(RequestHandler):
  """View for the participant dashboard.
  """

  def djangoURLPatterns(self):
    """The URL pattern for the dashboard.
    """
    return [
        url(r'^gsoc/dashboard/%s$' %url_patterns.PROGRAM, self,
            name='gsoc_dashboard')]

  def checkAccess(self):
    """Denies access if you don't have a role in the current program.
    """
    self.check.isLoggedIn()

  def templatePath(self):
    """Returns the path to the template.
    """
    return 'v2/modules/gsoc/dashboard/base.html'

  def jsonContext(self):
    """Handler for JSON requests.
    """
    components = self._getActiveComponents()

    list_content = None
    for component in components:
      list_content = component.getListData()
      if list_content:
        break

    if not list_content:
      raise AccessViolation(
          'You do not have access to this data')
    return list_content.content()

  def context(self):
    """Handler for default HTTP GET request.
    """
    components = self._getActiveComponents()

    context = {}
    context['page_name'] = self.data.program.name
    context['user'] = self.data.user
    context['logout_link'] = users.create_logout_url(self.data.full_path)
    # TODO(ljvderijk): Implement code for setting dashboard messages.
    #context['alert_msg'] = 'Default <strong>alert</strong> goes here'
    context['components'] = components

    return context

  def _getActiveComponents(self):
    """Returns the components that are active on the page.
    """
    if self.data.student:
      return self._getStudentComponents()
    elif self.data.mentor or self.data.org_admin:
      return self._getOrgMemberComponents()
    else:
      return self._getLoneUserComponents()

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
      # TODO(ljvderijk): Enable after the right information can be displayed
      #components.append(MyEvaluationsComponent(self.request, self.data))

    return components

  def _getOrgMemberComponents(self):
    """Get the dashboard components for Organization members.
    """
    components = []

    if self.data.mentor:
      if timeline_helper.isAfterEvent(
          self.data.program_timeline, 'accepted_students_announced_deadline'):
        # add a component to show all projects a user is mentoring
        components.append(
            ProjectsIMentorComponent(self.request, self.data))

    if self.data.org_admin:
      # add a component for all organization that this user administers
      components.append(OrganizationsIAdminComponent(self.request, self.data))

    if timeline_helper.isBeforeEvent(
      self.data.program_timeline, 'student_signup_start'):
      # Add the submitted proposals component
      #components.append(
      #    SubmittedProposalsComponent(self.request, self.data))
      pass

    return components

  def _getLoneUserComponents(self):
    """Get the dashboard components for users without any role.
    """
    components = []

    org_app_survey = org_app_logic.getForProgram(self.data.program)

    fields = {'survey': org_app_survey}
    org_app_record = org_app_logic.getRecordLogic().getForFields(fields, unique=True)

    if org_app_record:
      # add a component showing the organization application of the user
      components.append(MyOrgApplicationsComponent(self.request, self.data,
                                                   org_app_survey))

    return components

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


class MyOrgApplicationsComponent(Component):
  """Component for listing the Organization Applications of the current user.
  """

  def __init__(self, request, data, org_app_survey):
    """Initializes the component.

    Args:
      request: The HTTPRequest object
      data: The RequestData object
      org_app_survey: the OrgApplicationSurvey entity
    """
    # passed in so we don't have to do double queries
    self.org_app_survey = org_app_survey
    super(MyOrgApplicationsComponent, self).__init__(request, data)

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    # TODO(ljvderijk): List redirects
    list_params = org_app_view.getParams()['record_list_params']
    list_params['list_description'] = 'List of your Organization Applications'
    list_config = lists.getListGenerator(self.request, list_params,
                                         visibility='self', idx=0)
    return {
        'name': 'org_applications',
        'title': 'MY ORGANIZATION APPLICATIONS',
        'lists': Lists([list_config]),
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      list_data = lists.getListData(
          self.request, org_app_view.getParams()['record_list_params'],
          {'survey': self.org_app_survey, 'main_admin': self.data.user},
          visibility='self')
      return list_data
    else:
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
                                         proposal_view.getParams(), idx=1)
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
    if idx == 1:
      list_data = lists.getListData(self.request, proposal_view.getParams(),
                                   {'program': self.data.program,
                                    'scope': self.data.student})
      return list_data
    else:
      return None


class MyProjectsComponent(Component):
  """Component for listing all the projects of the current Student.
  """

  def __init__(self, request, data):
    """Initializes this component.
    """
    list_config = lists.ListConfiguration()
    list_config.addColumn('title', 'Title', lambda ent, *args: ent.title)
    list_config.addColumn('org_name', 'Organization Name',
                          lambda ent, *args: ent.scope.name)
    self._list_config = list_config

    super(MyProjectsComponent, self).__init__(request, data)

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
    if idx == 2:
      fields = {'program': self.data.program,
                'student': self.data.student}
      prefetch = ['scope']
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, project_logic, fields, prefetch)
      return response_builder.build()
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=2, description='List of my student projects')
    return {
        'name': 'projects',
        'title': 'PROJECTS',
        'lists': [list],
    }


class MyEvaluationsComponent(Component):
  """Component for listing all the Evaluations of the current Student.
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
    if idx == 3:
      list_data = lists.getListData(self.request, project_survey_view.getParams(),
                                    {'scope': self.data.program})
      return list_data
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list_config = lists.getListGenerator(
        self.request, project_survey_view.getParams(), idx=3)

    return {
        'name': 'evaluations',
        'title': 'EVALUATIONS',
        'lists': Lists([list_config]),
    }


class SubmittedProposalsComponent(Component):
  """Component for listing all the Evaluations of the current Student.
  """
  # TODO(ljvderijk): Implement
  pass


class ProjectsIMentorComponent(Component):
  """Component for listing all the Projects mentored by the current user.
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
    if idx == 4:
      list_data = lists.getListData(self.request, project_view.getParams(),
                                    {'program': self.data.program,
                                     'mentor': self.data.mentor})
      return list_data
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list_config = lists.getListGenerator(
        self.request, project_view.getParams(), idx=4)

    return {
        'name': 'mentoring_projects',
        'title': 'PROJECTS I AM A MENTOR FOR',
        'lists': Lists([list_config]),
    }


class OrganizationsIAdminComponent(Component):
  """Component for listing all the Organizations controlled by the current
  user.
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
    if idx == 5:
      # TODO(ljvderijk): Feels weird that if you have access to all the keys
      # already that you need to use the list code in this way. The rewrite
      # should probably allow the caller to control the entities to put in?
      list_data = lists.getListData(
          self.request, org_view.getParams(),
          {'scope': self.data.program,
           'link_id': [org_admin.scope.link_id
                       for org_admin in self.data.org_admin]})
      return list_data
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list_config = lists.getListGenerator(
        self.request, org_view.getParams(), idx=5)

    return {
        'name': 'adminning_organizations',
        'title': 'ORGANIZATIONS THAT I AM AN ADMIN FOR',
        'lists': Lists([list_config]),
    }
