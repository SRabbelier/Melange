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

"""Views for GSoCOrganization.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import itertools

from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.user import logic as user_logic
from soc.logic.models.org_app import logic as org_app_logic

from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.models import organization
from soc.views.models import group

from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.views.models import program as program_view
from soc.modules.gsoc.views.helper import access


class View(organization.View):
  """View methods for the Organization model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasRoleForKeyFieldsAsScope',
                           org_admin_logic),
                      ('checkGroupIsActiveForLinkId', org_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['public_list'] = ['allow']
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasRoleForKeyFieldsAsScope',
                                org_admin_logic)]
    rights['list_roles'] = [('checkHasRoleForKeyFieldsAsScope',
                             org_admin_logic)]
    rights['applicant'] = [('checkIsApplicationAccepted',
                            org_app_logic)]
    rights['list_proposals'] = [('checkHasAny', [
        [('checkHasRoleForKeyFieldsAsScope', [org_admin_logic]),
         ('checkHasRoleForKeyFieldsAsScope', [mentor_logic])]
        ])]

    new_params = {}
    new_params['logic'] = org_logic
    new_params['rights'] = rights

    new_params['scope_view'] = program_view

    new_params['name'] = "GSoC Organization"
    new_params['module_name'] = "organization"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['url_name'] = 'gsoc/org'
    new_params['document_prefix'] = 'gsoc_org'

    new_params['mentor_role_name'] = 'gsoc_mentor'

    new_params['extra_dynaexclude'] = ['slots', 'slots_calculated',
                                       'nr_applications', 'nr_mentors']

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)

  # TODO (dhans): merge common items with the GHOP module in a single function
  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific Organization menu entries.

    For args see group.View._getExtraMenuItems().
    """
    submenus = []

    group_entity = role_description['group']
    program_entity = group_entity.scope
    roles = role_description['roles']

    mentor_entity = roles.get('mentor')
    admin_entity = roles.get('org_admin')

    is_active_mentor = mentor_entity and mentor_entity.status == 'active'
    is_active_admin = admin_entity and admin_entity.status == 'active'

    if admin_entity or mentor_entity:
      # add a link to view all the student proposals
      submenu = (redirects.getListProposalsRedirect(group_entity, params),
          "View all Student Proposals", 'any_access')
      submenus.append(submenu)


    if is_active_admin:
      # add a link to manage student projects after they have been announced
      if timeline_helper.isAfterEvent(program_entity.timeline,
                                      'accepted_students_announced_deadline'):
        submenu = (redirects.getManageOverviewRedirect(group_entity,
            {'url_name': 'gsoc/student_project'}),
            "Manage Student Projects", 'any_access')
        submenus.append(submenu)

      # add a link to the management page
      submenu = (redirects.getListRolesRedirect(group_entity, params),
          "Manage Admins and Mentors", 'any_access')
      submenus.append(submenu)

      # add a link to invite an org admin
      submenu = (
          redirects.getInviteRedirectForRole(group_entity, 'gsoc/org_admin'),
          "Invite an Admin", 'any_access')
      submenus.append(submenu)

      # add a link to invite a member
      submenu = (
          redirects.getInviteRedirectForRole(group_entity, 'gsoc/mentor'),
          "Invite a Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the request page
      submenu = (redirects.getListRequestsRedirect(group_entity, params),
          "List Requests and Invites", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(group_entity, params),
          "Edit Organization Profile", 'any_access')
      submenus.append(submenu)

    if is_active_admin or is_active_mentor:
      submenu = (redirects.getCreateDocumentRedirect(
          group_entity, 
          params['document_prefix']),
          "Create a New Document", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getListDocumentsRedirect(
          group_entity,
          params['document_prefix']),
          "List Documents", 'any_access')
      submenus.append(submenu)


    if is_active_admin:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['org_admin'],
          {'url_name': 'gsoc/org_admin'}),
          "Resign as Admin", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['org_admin'],
          {'url_name': 'gsoc/org_admin'}),
          "Edit My Admin Profile", 'any_access')
      submenus.append(submenu)


    if is_active_mentor:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['mentor'],
          {'url_name' : 'gsoc/mentor'}),
          "Resign as Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['mentor'],
          {'url_name': 'gsoc/mentor'}),
          "Edit My Mentor Profile", 'any_access')
      submenus.append(submenu)

    return submenus

  @decorators.merge_params
  @decorators.check_access
  def listProposals(self, request, access_type,
                    page_name=None, params=None, **kwargs):
    """Lists all proposals for the organization given in kwargs.

    For params see base.View.public().
    """


    from soc.modules.gsoc.logic.models.ranker_root import logic \
        as ranker_root_logic
    from soc.modules.gsoc.logic.models.student_proposal import logic \
        as sp_logic
    from soc.modules.gsoc.models import student_proposal
    from soc.modules.gsoc.views.helper import list_info as list_info_helper
    from soc.modules.gsoc.views.models import student_proposal \
        as student_proposal_view

    try:
      org_entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    context = {}
    context['entity'] = org_entity

    list_params = student_proposal_view.view.getParams().copy()
    list_params['list_template'] = 'soc/student_proposal/list_for_org.html'
    list_params['list_key_order'] = [
         'title', 'abstract', 'content', 'additional_info', 'mentor',
         'possible_mentors', 'score', 'status', 'created_on',
         'last_modified_on']

    ranked_params = list_params.copy()# ranked proposals
    ranked_params['list_row'] = ('soc/%(module_name)s/list/'
        'detailed_row.html' % list_params)
    ranked_params['list_heading'] = ('soc/%(module_name)s/list/'
        'detailed_heading.html' % list_params)
    ranked_params['list_action'] = (redirects.getReviewRedirect, ranked_params)

    description = ugettext('%s already under review sent to %s') %(
        ranked_params['name_plural'], org_entity.name)
    ranked_params['list_description'] = description

    # TODO(ljvderijk) once sorting with IN operator is fixed, 
    # make this list show more
    filter = {'org': org_entity,
              'status': 'pending'}

    # order by descending score
    order = ['-score']

    prop_list = lists.getListContent(
        request, ranked_params, filter, order=order, idx=0)

    proposals = prop_list['data']

    # get a list of scores
    scores = [[proposal.score] for proposal in proposals]

    # retrieve the ranker
    fields = {'link_id': student_proposal.DEF_RANKER_NAME,
              'scope': org_entity}

    ranker_root = ranker_root_logic.getForFields(fields, unique=True)
    ranker = ranker_root_logic.getRootFromEntity(ranker_root)

    # retrieve the ranks for these scores
    ranks = [rank+1 for rank in ranker.FindRanks(scores)]

    # link the proposals to the rank
    ranking = dict([i for i in itertools.izip(proposals, ranks)])

    assigned_proposals = []

    # only when the program allows allocations 
    # to be seen we should color the list
    if org_entity.scope.allocations_visible:
      assigned_proposals = sp_logic.getProposalsToBeAcceptedForOrg(org_entity)

      # show the amount of slots assigned on the webpage
      context['slots_visible'] = True

    ranking_keys = dict([(k.key(), v) for k, v in ranking.iteritems()])
    proposal_keys = [i.key() for i in assigned_proposals]

    # update the prop_list with the ranking and coloring information
    prop_list['info'] = (list_info_helper.getStudentProposalInfo(ranking_keys,
        proposal_keys), None)

    # check if the current user is a mentor
    user_entity = user_logic.getForCurrentAccount()

    fields = {'user': user_entity,
        'scope': org_entity,}
    mentor_entity = mentor_logic.getForFields(fields, unique=True)

    if mentor_entity:
      mp_params = list_params.copy() # proposals mentored by current user

      description = ugettext('List of %s sent to %s you are mentoring') % (
          mp_params['name_plural'], org_entity.name)
      mp_params['list_description'] = description
      mp_params['list_action'] = (redirects.getReviewRedirect, mp_params)

      filter = {'org': org_entity,
                'mentor': mentor_entity,
                'status': 'pending'}

      mp_list = lists.getListContent(
          request, mp_params, filter, idx=1, need_content=True)

    new_params = list_params.copy() # new proposals
    new_params['list_description'] = 'List of new %s sent to %s ' % (
        new_params['name_plural'], org_entity.name)
    new_params['list_action'] = (redirects.getReviewRedirect, new_params)

    filter = {'org': org_entity,
              'status': 'new'}

    contents = []
    new_list = lists.getListContent(
        request, new_params, filter, idx=2, need_content=True)

    ap_params = list_params.copy() # accepted proposals

    description = ugettext('List of accepted %s sent to %s ') % (
        ap_params['name_plural'], org_entity.name)

    ap_params['list_description'] = description
    ap_params['list_action'] = (redirects.getReviewRedirect, ap_params)

    filter = {'org': org_entity,
              'status': 'accepted'}

    ap_list = lists.getListContent(
        request, ap_params, filter, idx=3, need_content=True)

    rp_params = list_params.copy() # rejected proposals

    description = ugettext('List of rejected %s sent to %s ') % (
        rp_params['name_plural'], org_entity.name)

    rp_params['list_description'] = description
    rp_params['list_action'] = (redirects.getReviewRedirect, rp_params)

    filter = {'org': org_entity,
              'status': 'rejected'}

    rp_list = lists.getListContent(
        request, rp_params, filter, idx=4, need_content=True)

    ip_params = list_params.copy() # ineligible proposals

    description = ugettext('List of ineligible %s sent to %s ') % (
        ip_params['name_plural'], org_entity.name)

    ip_params['list_description'] = description
    ip_params['list_action'] = (redirects.getReviewRedirect, ip_params)

    filter = {'org': org_entity,
              'status': 'invalid'}

    ip_list = lists.getListContent(
        request, ip_params, filter, idx=5, need_content=True)

    # fill contents with all the needed lists
    if new_list != None:
      contents.append(new_list)

    contents.append(prop_list)

    if mentor_entity and mp_list != None:
      contents.append(mp_list)

    if ap_list != None:
      contents.append(ap_list)

    if rp_list != None:
      contents.append(rp_list)

    if ip_list != None:
      contents.append(ip_list)

    # call the _list method from base to display the list
    return self._list(request, list_params, contents, page_name, context)


view = View()

admin = decorators.view(view.admin)
#applicant = decorators.view(view.applicant) # TODO
apply_mentor = decorators.view(view.applyMentor)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
home = decorators.view(view.home)
list = decorators.view(view.list)
list_proposals = decorators.view(view.listProposals)
list_public = decorators.view(view.listPublic)
list_requests = decorators.view(view.listRequests)
list_roles = decorators.view(view.listRoles)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
