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
from django.utils.translation import ugettext

from soc.logic.exceptions import AccessViolation
from soc.logic.helper import timeline as timeline_helper
from soc.views.template import Template

from soc.modules.gsoc.logic.models.org_app_survey import logic as \
    org_app_logic
from soc.modules.gsoc.logic.models.student_project import logic as \
    project_logic
from soc.modules.gsoc.logic.models.survey import project_logic as \
    ps_logic
from soc.modules.gsoc.models.proposal import GSoCProposal
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
    context['logged_in_msg'] = LoggedInMsg(self.data)
    # TODO(ljvderijk): Implement code for setting dashboard messages.
    #context['alert_msg'] = 'Default <strong>alert</strong> goes here'
    context['components'] = components

    return context

  def _getActiveComponents(self):
    """Returns the components that are active on the page.
    """
    if self.data.student_info:
      return self._getStudentComponents()
    elif self.data.mentor_for or self.data.org_admin_for:
      return self._getOrgMemberComponents()
    else:
      return self._getLoneUserComponents()

  def _getStudentComponents(self):
    """Get the dashboard components for a student.
    """
    # Add all the proposals of this current user
    components = [MyProposalsComponent(self.request, self.data)]

    project = project_logic.getOneForFields({}, ancestors=[self.data.profile])
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

    if self.data.mentor_for:
      if timeline_helper.isAfterEvent(
          self.data.program_timeline, 'accepted_students_announced_deadline'):
        # add a component to show all projects a user is mentoring
        components.append(
            ProjectsIMentorComponent(self.request, self.data))

    if timeline_helper.isAfterEvent(
      self.data.program_timeline, 'student_signup_start'):
      # Add the submitted proposals component
      components.append(
          SubmittedProposalsComponent(self.request, self.data))

    if self.data.org_admin_for:
      # add a component for all organization that this user administers
      components.append(OrganizationsIAdminComponent(self.request, self.data))

    return components

  def _getLoneUserComponents(self):
    """Get the dashboard components for users without any role.
    """
    components = []

    org_app_survey = org_app_logic.getForProgram(self.data.program)

    fields = {'survey': org_app_survey}
    org_app_record = org_app_logic.getRecordLogic().getForFields(fields,
                                                                 unique=True)

    if org_app_record:
      # add a component showing the organization application of the user
      components.append(MyOrgApplicationsComponent(self.request, self.data,
                                                   org_app_survey))

    return components


class LoggedInMsg(Template):
  """Template to render user login message at the top of the profile form.
  """
  def __init__(self, data):
    self.data = data

  def context(self):
    context = {
        'logout_link': self.data.redirect.logout().url(),
        'user_email': self.data.gae_user.email(),
        'has_profile': bool(self.data.profile),
    }

    if self.data.user:
      context['user_email'] = "%s [link_id: %s]" % (
          context['user_email'], self.data.user.link_id)

    if self.data.timeline.orgsAnnounced() and self.data.student_info:
      context['apply_link'] = self.data.redirect.acceptedOrgs().url()

    return context

  def templatePath(self):
    return "v2/modules/gsoc/_loggedin_msg.html"



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

    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('name', 'Organization Name')
    self._list_config = list_config

    super(MyOrgApplicationsComponent, self).__init__(request, data)

  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=0, description='List of your Organization Applications')

    return {
        'name': 'org_applications',
        'title': 'MY ORGANIZATION APPLICATIONS',
        'lists': [list],
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 0:
      fields = {'survey': self.org_app_survey,
                'main_admin': self.data.user}
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, org_app_logic.getRecordLogic(),
          fields)
      return response_builder.build()
    else:
      return None


class MyProposalsComponent(Component):
  """Component for listing all the proposals of the current Student.
  """

  DESCRIPTION = ugettext(
      'Click on a proposal in this list to see the comments or update your proposal.')

  def __init__(self, request, data):
    """Initializes this component.
    """
    r = data.redirect
    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org', 'Organization',
                          lambda ent, *args: ent.org.name)
    list_config.setRowAction(lambda e, *args, **kwargs: 
        r.review(e.key().id_or_name(), e.parent().link_id).
        urlOf('review_gsoc_proposal'))
    self._list_config = list_config

    super(MyProposalsComponent, self).__init__(request, data)


  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=1, description=MyProposalsComponent.DESCRIPTION)
    return {
        'name': 'proposals',
        'title': 'PROPOSALS',
        'lists': [list],
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 1:
      q = GSoCProposal.all()
      q.filter('program', self.data.program)
      q.ancestor(self.data.profile)

      starter = lambda start: GSoCProposal.get_by_key_name(start)

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, q, starter, prefetch=['org'])
      return response_builder.build()
    else:
      return None


class MyProjectsComponent(Component):
  """Component for listing all the projects of the current Student.
  """

  def __init__(self, request, data):
    """Initializes this component.
    """
    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
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
                'student': self.data.profile}
      prefetch = ['scope']
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, project_logic, fields,
          prefetch=prefetch)
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

  def __init__(self, request, data):
    """Initializes this component.
    """
    # TODO: This list should allow one to view or edit a record for each project
    # available to the student.
    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
    list_config.addSimpleColumn('survey_start', 'Survey Starts')
    list_config.addSimpleColumn('survey_end', 'Survey Ends')
    self._list_config = list_config

    super(MyEvaluationsComponent, self).__init__(request, data)

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
      fields = {'program': self.data.program}
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, ps_logic, fields)
      return response_builder.build()
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=3, description='List of my evaluations')

    return {
        'name': 'evaluations',
        'title': 'EVALUATIONS',
        'lists': [list],
    }


class SubmittedProposalsComponent(Component):
  """Component for listing all the proposals send to orgs this user is a member
  of.
  """

  DESCRIPTION = ugettext(
      'Click on a proposal to leave comments and give a score')

  def __init__(self, request, data):
    """Initializes this component.
    """
    r = data.redirect
    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org', 'Organization',
                          lambda ent, *args: ent.org.name)
    list_config.setRowAction(lambda e, *args, **kwargs: 
        r.review(e.key().id_or_name(), e.parent().link_id).
        urlOf('review_gsoc_proposal'))
    self._list_config = list_config

    super(SubmittedProposalsComponent, self).__init__(request, data)


  def templatePath(self):
    """Returns the path to the template that should be used in render().
    """
    return'v2/modules/gsoc/dashboard/list_component.html'

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=4,
        description=SubmittedProposalsComponent.DESCRIPTION)
    return {
        'name': 'proposals_submitted',
        'title': 'PROPOSALS SUBMITTED',
        'lists': [list],
        }

  def getListData(self):
    """Returns the list data as requested by the current request.

    If the lists as requested is not supported by this component None is
    returned.
    """
    idx = lists.getListIndex(self.request)
    if idx == 4:
      q = GSoCProposal.all()
      q.filter('org IN', self.data.profile.mentor_for)

      starter = lambda start: GSoCProposal.get_by_key_name(start)

      response_builder = lists.RawQueryContentResponseBuilder(
          self.request, self._list_config, q, starter, prefetch=['org'])
      return response_builder.build()
    else:
      return None

class ProjectsIMentorComponent(Component):
  """Component for listing all the Projects mentored by the current user.
  """

  def __init__(self, request, data):
    """Initializes this component.
    """
    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('title', 'Title')
    list_config.addColumn('org_name', 'Organization',
                          lambda ent, *args: ent.scope.name)
    self._list_config = list_config

    super(ProjectsIMentorComponent, self).__init__(request, data)

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
      fields =  {'program': self.data.program,
                 'mentor': self.data.profile}
      response_builder = lists.QueryContentResponseBuilder(
          self.request, self._list_config, project_logic, fields, prefetch=['scope'])
      return response_builder.build()
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=5, description='List of projects I mentor')

    return {
        'name': 'mentoring_projects',
        'title': 'PROJECTS I AM A MENTOR FOR',
        'lists': [list],
    }


class OrganizationsIAdminComponent(Component):
  """Component for listing all the Organizations controlled by the current
  user.
  """

  def __init__(self, request, data):
    """Initializes this component.
    """
    r = data.redirect
    list_config = lists.ListConfiguration()
    list_config.addSimpleColumn('name', 'name')
    list_config.setRowAction(
        lambda e, *args, **kwargs: r.organization(e).urlOf('gsoc_org_home'))
    self._list_config = list_config

    super(OrganizationsIAdminComponent, self).__init__(request, data)

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
    if idx == 6:
      response = lists.ListContentResponse(self.request, self._list_config)

      if response.start != 'done':
        # Add all organizations in one go since we already queried for it.
        for org in self.data.org_admin_for:
          response.addRow(org)
        response.next = 'done'

      return response
    else:
      return None

  def context(self):
    """Returns the context of this component.
    """
    list = lists.ListConfigurationResponse(
        self._list_config, idx=6, description='Organizations I am an admin for')

    return {
        'name': 'adminning_organizations',
        'title': 'ORGANIZATIONS THAT I AM AN ADMIN FOR',
        'lists': [list],
    }
