#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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

"""Views for Organizations.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Augie Fackler" <durin42@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import itertools

from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import accounts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import mentor as mentor_logic
from soc.logic.models import organization as org_logic
from soc.logic.models import org_admin as org_admin_logic
from soc.logic.models import org_app as org_app_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import group

import soc.models.organization
import soc.logic.models.organization

class View(group.View):
  """View methods for the Organization model.
  """

  DEF_ACCEPTED_PROJECTS_MSG_FMT = ugettext("These projects have"
      " been accepted into %s. You can learn more about"
      " each project by visiting the links below.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
    """

    from soc.views.models import program as program_view

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasActiveRoleForKeyFieldsAsScope',
                           org_admin_logic.logic,),
                      ('checkGroupIsActiveForLinkId', org_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['public_list'] = ['allow']
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasActiveRoleForKeyFieldsAsScope',
                                org_admin_logic.logic)]
    rights['list_roles'] = [('checkHasActiveRoleForKeyFieldsAsScope',
                             org_admin_logic.logic)]
    rights['applicant'] = [('checkIsApplicationAccepted',
                            org_app_logic.logic)]
    rights['list_proposals'] = [('checkHasAny', [
        [('checkHasActiveRoleForKeyFieldsAsScope', [org_admin_logic.logic]),
         ('checkHasActiveRoleForKeyFieldsAsScope', [mentor_logic.logic])]
        ])]

    new_params = {}
    new_params['logic'] = soc.logic.models.organization.logic
    new_params['rights'] = rights

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Organization"
    new_params['url_name'] = "org"
    new_params['document_prefix'] = "org"
    new_params['sidebar_grouping'] = 'Organizations'

    new_params['public_template'] = 'soc/organization/public.html'
    new_params['list_row'] = 'soc/organization/list/row.html'
    new_params['list_heading'] = 'soc/organization/list/heading.html'
    new_params['home_template'] = 'soc/organization/home.html'

    new_params['application_logic'] = org_app_logic
    new_params['group_applicant_url'] = True
    new_params['sans_link_id_public_list'] = True

    new_params['extra_dynaexclude'] = ['slots', 'slots_calculated',
                                       'nr_applications', 'nr_mentors']

    patterns = []

    patterns += [
        (r'^%(url_name)s/(?P<access_type>apply_mentor)/%(scope)s$',
        'soc.views.models.%(module_name)s.apply_mentor',
        "List of all %(name_plural)s you can apply to"),
        (r'^%(url_name)s/(?P<access_type>list_proposals)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.list_proposals',
        "List of all Student Proposals for this %(name)s"),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['create_dynafields'] = [
        {'name': 'link_id',
         'base': forms.fields.CharField,
         'label': 'Organization Link ID',
         },
        ]

    new_params['create_extra_dynaproperties'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
                                   required=True),
        'description': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(
                attrs={'rows': 25, 'cols': 100})),
        'contrib_template': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(
                attrs={'rows': 25, 'cols': 100})),
        'clean_description': cleaning.clean_html_content('description'),
        'clean_contrib_template': cleaning.clean_html_content(
            'contrib_template'),
        'clean_ideas': cleaning.clean_url('ideas'),
        'clean': cleaning.validate_new_group('link_id', 'scope_path',
            soc.logic.models.organization, org_app_logic)
        }

    new_params['edit_extra_dynaproperties'] = {
        'clean': cleaning.clean_refs(new_params, ['home_link_id'])
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special form for applicants
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False),
        'clean_link_id': cleaning.clean_link_id('link_id')
        }

    applicant_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynaproperties = updated_fields)

    self._params['applicant_create_form'] = applicant_create_form

  @decorators.merge_params
  @decorators.check_access
  def applyMentor(self, request, access_type,
                  page_name=None, params=None, **kwargs):
    """Shows a list of all organizations and you can choose one to
       apply to become a mentor.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    list_params = params.copy()
    list_params['list_action'] = (redirects.getRequestRedirectForRole, 'mentor')
    list_params['list_description'] = ugettext('Choose an Organization which '
        'you want to become a Mentor for.')

    filter = {'scope_path': kwargs['scope_path'],
              'status' : 'active'}

    return self.list(request, access_type,
        page_name, params=list_params, filter=filter)

  @decorators.merge_params
  @decorators.check_access
  def listProposals(self, request, access_type,
                    page_name=None, params=None, **kwargs):
    """Lists all proposals for the organization given in kwargs.

    For params see base.View.public().
    """

    from soc.logic.models.ranker_root import logic as ranker_root_logic
    from soc.logic.models.student_proposal import logic as sp_logic
    from soc.models import student_proposal
    from soc.views.helper import list_info as list_info_helper
    from soc.views.models import student_proposal as student_proposal_view

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
    ranked_params['list_description'] = '%s already under review sent to %s' % (
        ranked_params['name_plural'], org_entity.name)
    ranked_params['list_action'] = (redirects.getReviewRedirect, ranked_params)

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
    user_entity = user_logic.logic.getForCurrentAccount()

    fields = {'user': user_entity,
        'scope': org_entity,}
    mentor_entity = mentor_logic.logic.getForFields(fields, unique=True)

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
    ap_params['list_action'] = (redirects.getPublicRedirect, ap_params)

    filter = {'org': org_entity,
              'status': 'accepted'}

    ap_list = lists.getListContent(
        request, ap_params, filter, idx=3, need_content=True)

    rp_params = list_params.copy() # rejected proposals

    description = ugettext('List of rejected %s sent to %s ') % (
        rp_params['name_plural'], org_entity.name)

    rp_params['list_description'] = description
    rp_params['list_action'] = (redirects.getPublicRedirect, rp_params)

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

  @decorators.merge_params
  @decorators.check_access
  def listPublic(self, request, access_type, page_name=None,
                 params=None, filter=None, **kwargs):
    """See base.View.list.
    """

    account = accounts.getCurrentAccount()
    user = user_logic.logic.getForAccount(account) if account else None

    try:
      rights = self._params['rights']
      rights.setCurrentUser(account, user)
      rights.checkIsHost()
      is_host = True
    except out_of_band.Error:
      is_host = False

    params = params.copy()

    if is_host:
      params['list_action'] = (redirects.getAdminRedirect, params)
    else:
      params['list_action'] = (redirects.getPublicRedirect, params)

    new_filter = {}

    new_filter['scope_path'] = kwargs['scope_path']
    new_filter['status'] = 'active'
    filter = dicts.merge(filter, new_filter)

    content = lists.getListContent(request, params, filter)
    contents = [content]

    return self._list(request, params, contents, page_name)

  def _getMapData(self, student_project_params, filter=None):
    """Constructs the JSON object required to generate a 
      google map on organization home page.

    Args:
      student_project_logic: logic for student_project to obtain entities
      filter: a dict for the properties that the entities should have

    Returns: 
      A json object containing map data with the following structure.
      [
        {
          'type': 'mentor',
          'name': MentorName,
          'city': CityName,
          'ccTLD': ccTLD,
          'students': [{'name': Name, 'city': CityName, 'ccTLD': ccTLD,
                      'summary': Summary, 'url': URL}, 
                   {'name': Name, 'city': CityName, 'ccTLD': ccTLD,
                      'summary': Summary, 'url': URL}, ]
        },
        {
          'type': 'none',
          'name': MentorName,
          'student': {'name': Name, 'city': CityName, 'ccTLD': ccTLD, 
                      'summary': Summary, 'url': URL}
        }
      ]
    """
    student_project_logic = student_project_params['logic']

    map_data = []
    mentors = {}
    student_only = []

    # get all the student_project entities for this organization
    student_project_entities = student_project_logic.getForFields(filter)

    # construct a dictionary of mentors. For each mentor construct a
    # list of 3-tuple containing student, project title and url. This is
    # mainly done to track and pair all students and mentors who
    # have allowed to publish their locations.
    for entity in student_project_entities:

      if entity.mentor.publish_location and entity.mentor not in mentors:
        # if mentor has allowed to publish his location add it to the 
        # mentors dictionary
        mentors[entity.mentor] = []

      if entity.student.publish_location:
        # if student has allowed to publish his location, add it to the
        # corresponding mentor list, otherwise add it to the 'none' list
        if entity.mentor in mentors:
          mentors[entity.mentor].append(
              (entity.student, entity.title,
              redirects.getPublicRedirect(entity, student_project_params)))
        else:
          student_only.append(
              (entity.student, entity.title,
               redirects.getPublicRedirect(entity, student_project_params),
               entity.mentor))

    # from the index built in the form of mentors dictionary we now build
    # the map_data for all the mentors who have allowed to publish their
    # location
    for mentor in mentors:
      mentor_map = {
          'type': 'mentor',
          'name': mentor.name(),
          'city': mentor.res_city,
          'ccTLD': mentor.ccTld(),
          'students': []
          }

      for student, summary, url in mentors[mentor]:
        student_map = {
           'name': student.name(),
           'city': student.res_city,
           'ccTLD': student.ccTld(),
           'summary': summary,
           'url': url
           }

        mentor_map['students'].append(student_map)

      map_data.append(mentor_map)

    # construct the 'type': 'none' dictionary for those students, whose
    # mentors haven't allowed to publish location
    for student, summary, url, mentor in student_only:
      nomentor_map = {
          'type': 'none',
          'name': mentor.name(), 
          'student': {
              'name': student.name(),
              'city': student.res_city,
              'ccTLD': student.ccTld(),
              'summary': summary,
              'url': url
              }
          }

      map_data.append(nomentor_map)

    return simplejson.dumps(map_data)

  def _public(self, request, entity, context):
    """See base.View._public().
    """

    from soc.views.models import student_project as student_project_view

    program_entity = entity.scope

    if timeline_helper.isAfterEvent(program_entity.timeline,
                                    'accepted_students_announced_deadline'):
      ap_params = student_project_view.view.getParams().copy() # accepted projects

      # define the list redirect action to show the notification
      ap_params['list_action'] = (redirects.getPublicRedirect, ap_params)
      ap_params['list_description'] = self.DEF_ACCEPTED_PROJECTS_MSG_FMT % (
          entity.name)
      ap_params['list_heading'] = 'soc/student_project/list/heading.html'
      ap_params['list_row'] = 'soc/student_project/list/row.html'

      # only show projects that have not failed
      filter = {'scope': entity,
                'status': ['accepted', 'mid_term_passed', 'passed']}

      ap_list = lists.getListContent(request, ap_params, filter, idx=0,
                                     need_content=True)

      contents = []

      if ap_list:
        contents.append(ap_list)

      # construct the list and put it into the context
      context['list'] = soc.logic.lists.Lists(contents)

      # obtain data to construct the organization map as json object
      context['org_map_data'] = self._getMapData(ap_params, filter)

    return super(View, self)._public(request=request, entity=entity,
                                     context=context)

  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific Organization menu entries.

    For args see group.View._getExtraMenuItems().
    """
    submenus = []

    group_entity = role_description['group']
    program_entity = group_entity.scope
    roles = role_description['roles']

    if roles.get('org_admin') or roles.get('mentor'):
      # add a link to view all the student proposals
      submenu = (redirects.getListProposalsRedirect(group_entity, params),
          "View all Student Proposals", 'any_access')
      submenus.append(submenu)


    if roles.get('org_admin'):
      # add a link to manage student projects after they have been announced
      if timeline_helper.isAfterEvent(program_entity.timeline,
                                     'accepted_students_announced_deadline'):
        submenu = (redirects.getManageOverviewRedirect(group_entity,
            {'url_name': 'student_project'}),
            "Manage Student Projects", 'any_access')
        submenus.append(submenu)

      # add a link to the management page
      submenu = (redirects.getListRolesRedirect(group_entity, params),
          "Manage Admins and Mentors", 'any_access')
      submenus.append(submenu)

      # add a link to invite an org admin
      submenu = (redirects.getInviteRedirectForRole(group_entity, 'org_admin'),
          "Invite an Admin", 'any_access')
      submenus.append(submenu)

      # add a link to invite a member
      submenu = (redirects.getInviteRedirectForRole(group_entity, 'mentor'),
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

    if roles.get('org_admin') or roles.get('mentor'):
      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'org'),
          "Create a New Document", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getListDocumentsRedirect(group_entity, 'org'),
          "List Documents", 'any_access')
      submenus.append(submenu)


    if roles.get('org_admin'):
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['org_admin'],
          {'url_name': 'org_admin'}),
          "Resign as Admin", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['org_admin'],
          {'url_name': 'org_admin'}),
          "Edit My Admin Profile", 'any_access')
      submenus.append(submenu)


    if roles.get('mentor'):
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['mentor'],
          {'url_name' : 'mentor'}),
          "Resign as Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['mentor'],
          {'url_name': 'mentor'}),
          "Edit My Mentor Profile", 'any_access')
      submenus.append(submenu)

    return submenus


view = View()

admin = decorators.view(view.admin)
applicant = decorators.view(view.applicant)
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
