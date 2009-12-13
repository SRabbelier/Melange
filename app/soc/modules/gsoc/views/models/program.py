#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Views for GSoCProgram.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.utils.translation import ugettext

from soc.logic import dicts
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.models import program
from soc.views.sitemap import sidebar

from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import org_app as org_app_logic
from soc.logic.models.host import logic as host_logic
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.student import logic as student_logic
from soc.modules.gsoc.views.helper import access
from soc.views.helper import redirects


class View(program.View):
  """View methods for the Program model.
  """

  DEF_ACCEPTED_ORGS_MSG_FMT = ugettext("These organizations have"
      " been accepted into %(name)s, but they have not yet completed"
      " their organization profile. You can still learn more about"
      " each organization by visiting the links below.")

  DEF_CREATED_ORGS_MSG_FMT = ugettext("These organizations have been"
      " accepted into %(name)s and have completed their organization"
      " profiles. You can learn more about each organization by"
      " visiting the links below.")

  DEF_ACCEPTED_PROJECTS_MSG_FMT = ugettext("These projects have been"
      " accepted into %(name)s. You can learn more about each project"
      " by visiting the links below.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasActiveRoleForScope',
        host_logic])]
    rights['edit'] = [('checkIsHostForProgram', [program_logic])]
    rights['delete'] = ['checkIsDeveloper']
    rights['assign_slots'] = [('checkIsHostForProgram', [program_logic])]
    rights['slots'] = [('checkIsHostForProgram', [program_logic])]
    rights['show_duplicates'] = [('checkIsHostForProgram',
        [program_logic])]
    rights['assigned_proposals'] = [('checkIsHostForProgram',
        [program_logic])]
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['accepted_organization_announced_deadline',
         '__all__', program_logic])]
    rights['list_projects'] = [('checkIsAfterEvent',
        ['accepted_students_announced_deadline',
         '__all__', program_logic])]

    new_params = {}
    new_params['logic'] = program_logic
    new_params['rights'] = rights

    new_params['name'] = "GSoC Program"
    new_params['module_name'] = "program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'gsoc_program'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/program'

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)

  @decorators.merge_params
  def getExtraMenus(self, id, user, params=None):
    """Returns the extra menu's for this view.

    A menu item is generated for each program that is currently
    running. The public page for each program is added as menu item,
    as well as all public documents for that program.

    Args:
      params: a dict with params for this View.
    """

    logic = params['logic']
    rights = params['rights']

    # only get all invisible and visible programs
    fields = {'status': ['invisible', 'visible']}
    entities = logic.getForFields(fields)

    menus = []

    rights.setCurrentUser(id, user)

    for entity in entities:
      items = []

      if entity.status == 'visible':
        items += self._getVisibleProgramEntries(entity, id, user, params)
        items += self._getSurveyEntries(entity, params, id, user)
      try:
        # check if the current user is a host for this program
        rights.doCachedCheck('checkIsHostForProgram',
                             {'scope_path': entity.scope_path,
                              'link_id': entity.link_id}, [])

        if entity.status == 'invisible':
          # still add the document links so hosts can see how it looks like
          items += self._getVisibleProgramEntries(entity, id, user, params)
          items += self._getSurveyEntries(entity, params, id, user)

        items += self._getHostEntries(entity, params, 'gsoc')

        items += [(redirects.getReviewOverviewRedirect(
            entity, {'url_name': 'org_app'}),
            "Review Organization Applications", 'any_access')]

        # add link to Assign Slots
        items += [(redirects.getAssignSlotsRedirect(entity, params),
            'Assign Slots', 'any_access')]
        # add link to Show Duplicate project assignments
        items += [(redirects.getShowDuplicatesRedirect(entity, params),
            'Show Duplicate Project Assignments', 'any_access')]
        # add link to create a new Program Survey
        items += [(redirects.getCreateSurveyRedirect(entity, 'program',
            'survey'),
            "Create a New Survey", 'any_access')]
        # add link to list all Program Surveys
        items += [(redirects.getListSurveysRedirect(entity, 'program',
            'survey'),
            "List Surveys", 'any_access')]
        # add link to create a new Project Survey
        items += [(redirects.getCreateSurveyRedirect(entity, 'program',
            'gsoc/project_survey'),
            "Create a New Project Survey", 'any_access')]
        # add link to list all Project Surveys
        items += [(redirects.getListSurveysRedirect(entity, 'program',
            'gsoc/project_survey'),
            "List Project Surveys", 'any_access')]
        # add link to create a new Grading Survey
        items += [(redirects.getCreateSurveyRedirect(entity, 'program',
            'gsoc/grading_project_survey'),
            "Create a New Grading Survey", 'any_access')]
        # add link to list all Grading Surveys
        items += [(redirects.getListSurveysRedirect(entity, 'program',
            'gsoc/grading_project_survey'),
            "List Grading Surveys", 'any_access')]
        # add link to withdraw Student Projects
        items += [(redirects.getWithdrawRedirect(
            entity, {'url_name': 'student_project'}),
            "Withdraw Student Projects", 'any_access')]

      except out_of_band.Error:
        pass

      items = sidebar.getSidebarMenu(id, user, items, params=params)
      if not items:
        continue

      menu = {}
      menu['heading'] = entity.short_name
      menu['items'] = items
      menu['group'] = 'Programs'
      menus.append(menu)

    return menus

  def _getTimeDependentEntries(self, program_entity, params, id, user):
    """Returns a list with time dependent menu items.
    """
    items = []

    #TODO(ljvderijk) Add more timeline dependent entries
    timeline_entity = program_entity.timeline

    if timeline_helper.isActivePeriod(timeline_entity, 'org_signup'):
      # add the organization signup link
      items += [
          (redirects.getApplyRedirect(program_entity, {'url_name': 'org_app'}),
          "Apply to become an Organization", 'any_access')]

    if user and timeline_helper.isAfterEvent(timeline_entity,
        'org_signup_start'):
      filter = {
          'applicant': user,
          'scope': program_entity,
          }

      if org_app_logic.logic.getForFields(filter, unique=True):
        # add the 'List my Organization Applications' link
        items += [
            (redirects.getListSelfRedirect(program_entity,
                                           {'url_name' : 'org_app'}),
             "List My Organization Applications", 'any_access')]

    # get the student entity for this user and program
    filter = {'user': user,
              'scope': program_entity,
              'status': 'active'}
    student_entity = student_logic.getForFields(filter, unique=True)

    if student_entity:
      items += self._getStudentEntries(program_entity, student_entity,
                                       params, id, user, 'gsoc')

    # get mentor and org_admin entity for this user and program
    filter = {'user': user,
              'program': program_entity,
              'status': 'active'}
    mentor_entity = mentor_logic.getForFields(filter, unique=True)
    org_admin_entity = org_admin_logic.getForFields(filter,
                                                               unique=True)

    if mentor_entity or org_admin_entity:
      items += self._getOrganizationEntries(program_entity, org_admin_entity,
                                            mentor_entity, params, id, user)

    if user and not (student_entity or mentor_entity or org_admin_entity):
      if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
        # this user does not have a role yet for this program
        items += [
            ('/gsoc/student/apply/%s' % (program_entity.key().id_or_name()),
            "Register as a Student", 'any_access')]

    deadline = 'accepted_organization_announced_deadline'

    if timeline_helper.isAfterEvent(timeline_entity, deadline):
      url = redirects.getAcceptedOrgsRedirect(program_entity, params)
      # add a link to list all the organizations
      items += [(url, "List participating Organizations", 'any_access')]

      if not student_entity:
        # add apply to become a mentor link
        items += [
            ('/gsoc/org/apply_mentor/%s' % (program_entity.key().id_or_name()),
           "Apply to become a Mentor", 'any_access')]

    deadline = 'accepted_students_announced_deadline'

    if timeline_helper.isAfterEvent(timeline_entity, deadline):
      items += [(redirects.getListProjectsRedirect(program_entity,
          {'url_name':'gsoc/program'}),
          "List all Student Projects", 'any_access')]

    return items

  def _getSurveyEntries(self, entity, params, id, user):
    """Returns a list of entries specific for surveys which should be visible
    for users.
    """

    from soc.views.models import survey as survey_view
    from soc.modules.gsoc.views.models import project_survey \
        as project_survey_view
    from soc.modules.gsoc.views.models import grading_project_survey \
        as grading_survey_view

    items = []

    items += survey_view.view.getMenusForScope(entity, params, id, user)
    items += project_survey_view.view.getMenusForScope(entity, params, id, 
                                                       user)
    items += grading_survey_view.view.getMenusForScope(entity, params, id,
                                                       user)

    return items

  def _getStudentEntries(self, program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    timeline_entity = program_entity.timeline

    if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
      items += [('/student_proposal/list_orgs/%s' % (
          student_entity.key().id_or_name()),
          "Submit your Student Proposal", 'any_access')]

    if timeline_helper.isAfterEvent(timeline_entity, 'student_signup_start'):
      items += [(redirects.getListSelfRedirect(student_entity,
          {'url_name': prefix + '/student_proposal'}),
          "List my Student Proposals", 'any_access')]

    if timeline_helper.isAfterEvent(timeline_entity,
                                   'accepted_students_announced_deadline'):
      # add a link to show all projects
      items += [(redirects.getListProjectsRedirect(program_entity,
          {'url_name': prefix + '/student'}),
          "List my Student Projects", 'any_access')]

    items += super(View, self)._getStudentEntries(program_entity,
        student_entity, params, id, user, prefix)

    return items

  @decorators.merge_params
  @decorators.check_access
  def acceptedOrgs(self, request, access_type,
                   page_name=None, params=None, filter=None, **kwargs):
    """See base.View.list.
    """

    from soc.modules.gsoc.views.models.organization import view as org_view

    contents = []
    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    aa_list = self._getOrgsWithAcceptedApps(request, program_entity, params)
    if aa_list:
      contents.append(aa_list)

    fmt = {'name': program_entity.name}
    description = self.DEF_CREATED_ORGS_MSG_FMT % fmt

    use_cache = not aa_list # only cache if there are no aa's left

    ap_list = self._getOrgsWithProfilesList(program_entity, org_view,
        description, use_cache)
    contents.append(ap_list)

    params = params.copy()
    params['list_msg'] = program_entity.accepted_orgs_msg

    return self._list(request, params, contents, page_name)

  def _getOrgsWithAcceptedApps(self, request, program_entity, params):
    """
    """

    fmt = {'name': program_entity.name}
    description = self.DEF_ACCEPTED_ORGS_MSG_FMT % fmt

    filter = {
        'status': 'accepted',
        'scope': program_entity,
        }

    from soc.views.models import org_app as org_app_view
    aa_params = org_app_view.view.getParams().copy() # accepted applications

    # define the list redirect action to show the notification
    del aa_params['list_key_order']
    aa_params['list_action'] = (redirects.getHomeRedirect, aa_params)
    aa_params['list_description'] = description

    aa_list = lists.getListContent(request, aa_params, filter, idx=0,
                                   need_content=True)

    return aa_list

  @decorators.merge_params
  @decorators.check_access
  def acceptedProjects(self, request, access_type,
                       page_name=None, params=None, filter=None, **kwargs):
    """See base.View.list.
    """
    contents = []
    logic = params['logic']

    program_entity = logic.getFromKeyFieldsOr404(kwargs)

    filter = {
        'status': 'accepted',
        'program': program_entity}

    fmt = {'name': program_entity.name}
    description = self.DEF_ACCEPTED_PROJECTS_MSG_FMT % fmt

    from soc.modules.gsoc.views.models import student_project as sp_view

    ap_params = sp_view.view.getParams().copy() # accepted projects
    ap_params['list_action'] = (redirects.getPublicRedirect, ap_params)
    ap_params['list_description'] = description
    ap_params['list_heading'] = 'soc/student_project/list/heading_all.html'
    ap_params['list_row'] = 'soc/student_project/list/row_all.html'

    prefetch = ['mentor', 'student', 'scope']

    return self.list(request, access_type, page_name=page_name,
                     params=ap_params, filter=filter, prefetch=prefetch)

view = View()

accepted_orgs = decorators.view(view.acceptedOrgs)
list_projects = decorators.view(view.acceptedProjects)
admin = decorators.view(view.admin)
assign_slots = decorators.view(view.assignSlots)
assigned_proposals = decorators.view(view.assignedProposals)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
show_duplicates = decorators.view(view.showDuplicates)
slots = decorators.view(view.slots)
home = decorators.view(view.home)
pick = decorators.view(view.pick)
