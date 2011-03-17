#!/usr/bin/env python2.5
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
    'Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.logic import cleaning
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models.user import logic as user_logic

from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import organization

from soc.modules.gsoc.logic import cleaning as gsoc_cleaning
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic
from soc.modules.gsoc.logic.models.student_proposal import logic \
    as sp_logic

from soc.modules.gsoc.models import student_proposal
from soc.modules.gsoc.models.organization import OrgTag

from soc.modules.gsoc.views.models import program as program_view
from soc.modules.gsoc.views.models import student_proposal \
    as student_proposal_view
from soc.modules.gsoc.views.helper import access

import soc.cache.logic


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
    rights['applicant'] = [('checkIsOrgAppAccepted', org_app_logic)]
    rights['apply_mentor'] = ['checkIsUser']
    rights['list_requests'] = [('checkHasRoleForKeyFieldsAsScope',
                                org_admin_logic)]
    rights['list_roles'] = [('checkHasRoleForKeyFieldsAsScope',
                             org_admin_logic)]
    rights['list_proposals'] = [('checkHasAny', [
        [('checkHasRoleForKeyFieldsAsScope', 
          [org_admin_logic, ['active', 'inactive']]),
         ('checkHasRoleForKeyFieldsAsScope', 
          [mentor_logic, ['active', 'inactive']])]
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
    new_params['mentor_url_name'] = 'gsoc/mentor'
    new_params['org_admin_role_name'] = 'gsoc_org_admin'

    patterns = []

    patterns += [
        (r'^org_tags/(?P<access_type>pick)$',
        '%(module_package)s.%(module_name)s.pick_suggested_tags', 
        "Pick a list of suggested tags."),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['slots', 'slots_calculated',
                                       'nr_applications', 'nr_mentors']

    new_params['create_extra_dynaproperties']  = {
        'tags': widgets.ReferenceField(
              required=False,
              reference_url='org_tags',
              label=ugettext('Tags'),
              help_text=ugettext("A list of comma seperated tags"),
              example_text="e.g. python, django, appengine",
              filter=['scope_path'],
              group="1. Public Info"),
        'clean_tags': gsoc_cleaning.cleanTagsList(
            'tags', gsoc_cleaning.COMMA_SEPARATOR),
        'contrib_template': forms.fields.CharField(
            widget=helper.widgets.FullTinyMCE(
                attrs={'rows': 25, 'cols': 100})),
        'clean_contrib_template': cleaning.clean_html_content(
            'contrib_template'),
        'clean_facebook': cleaning.clean_url('facebook'),
        'clean_twitter': cleaning.clean_url('twitter'),
        'clean_blog': cleaning.clean_url('blog'),
        }

    new_params['org_app_logic'] = org_app_logic

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)

    self._params['public_field_keys'].append('tags')
    self._params['public_field_names'].append("Tags")
    self._params['public_field_extra'] = lambda entity: {
        'ideas': lists.urlize(entity.ideas, 'Click Here'),
        'tags': entity.tags_string(entity.org_tag),
    }
    self._params['select_field_extra'] = self._params['public_field_extra']

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    if entity.org_tag:
      form.fields['tags'].initial = entity.tags_string(entity.org_tag)

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    super(View, self)._editPost(request, entity, fields)

    fields['org_tag'] = {
        'tags': fields['tags'],
        'scope': entity.scope if entity else fields['scope']
        }

  @decorators.check_access
  def pickSuggestedTags(self, request, access_type,
                        page_name=None, params=None, **kwargs):
    """Returns a JSON representation of a list of organization tags
     that are suggested for a given GSoCProgram in scope.
    """

    if 'scope_path' not in request.GET:
      data = []
    else:
      program = program_logic.getFromKeyName(request.GET.get('scope_path'))
      if not program:
        data = []
      else:
        fun = soc.cache.logic.cache(OrgTag.get_for_custom_query)
        suggested_tags = fun(OrgTag, filter={'scope': program}, order=None)
        # TODO: this should be refactored after the issue with autocompletion
        #       is resolved
        data = simplejson.dumps({
            'data': [{'link_id': item['tag']} for item in [dicts.toDict(tag, ['tag']) for tag in suggested_tags]],
            'autocomplete_options': {
               'multiple': True,
               'selectFirst': False
            }
        })

    return self.json(request, data, False)

  # TODO (dhans): merge common items with the GCI module in a single function
  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific Organization menu entries.

    For args see group.View._getExtraMenuItems().
    """
    submenus = []

    group_entity = role_description['group']
    program_entity = group_entity.scope
    roles = role_description['roles']

    mentor_entity = roles.get('gsoc_mentor')
    admin_entity = roles.get('gsoc_org_admin')

    is_active_mentor = mentor_entity and mentor_entity.status == 'active'
    is_active_admin = admin_entity and admin_entity.status == 'active'

    if admin_entity or mentor_entity:
      # add a link to view all the student proposals
      submenu = (redirects.getListProposalsRedirect(group_entity, params),
          "Manage Student Proposals", 'any_access')
      submenus.append(submenu)

      # add a link to manage student projects after they have been announced
      if timeline_helper.isAfterEvent(program_entity.timeline,
                                      'accepted_students_announced_deadline'):
        submenu = (redirects.getManageOverviewRedirect(group_entity,
            {'url_name': 'gsoc/student_project'}),
            "Manage Student Projects", 'any_access')
        submenus.append(submenu)


    if is_active_admin:
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
      submenu = (redirects.getManageRedirect(roles['gsoc_org_admin'],
          {'url_name': 'gsoc/org_admin'}),
          "Resign as Admin", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['gsoc_org_admin'],
          {'url_name': 'gsoc/org_admin'}),
          "Edit My Admin Profile", 'any_access')
      submenus.append(submenu)


    if is_active_mentor:
      # add a link to the resign page
      submenu = (redirects.getManageRedirect(roles['gsoc_mentor'],
          {'url_name' : 'gsoc/mentor'}),
          "Resign as Mentor", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(roles['gsoc_mentor'],
          {'url_name': 'gsoc/mentor'}),
          "Edit My Mentor Profile", 'any_access')
      submenus.append(submenu)

    return submenus


  def getListProposalsData(self, request, params_collection, org_entity):
    """Returns the list data for listProposals.

    Args:
      request: HTTPRequest object
      params_collection: List of list Params indexed with the idx of the list
      org_entity: GSoCOrganization entity for which the lists are generated
    """

    from soc.modules.gsoc.logic.models.proposal_duplicates import logic \
        as pd_logic
    from soc.modules.gsoc.logic.models.ranker_root import logic \
        as ranker_root_logic

    idx = lists.getListIndex(request)

    # default list settings
    args = []
    visibility = None

    if idx == 0:
      filter = {'org': org_entity,
                'status': 'new'}
    elif idx == 1:
      # retrieve the ranker
      fields = {'link_id': student_proposal.DEF_RANKER_NAME,
                'scope': org_entity}

      ranker_root = ranker_root_logic.getForFields(fields, unique=True)
      ranker = ranker_root_logic.getRootFromEntity(ranker_root)

      status = {}

      program_entity = org_entity.scope

      # only when the program allows allocations
      # we show that proposals are likely to be
      # accepted or rejected
      if program_entity.allocations_visible:
        proposals = sp_logic.getProposalsToBeAcceptedForOrg(org_entity)

        duplicate_proposals = []

        # get all the duplicate entities if duplicates can be shown
        # to the organizations and make a list of all such proposals.
        if program_entity.duplicates_visible:
          duplicate_properties = {
              'orgs': org_entity,
              'is_duplicate': True
              }
          duplicates = pd_logic.getForFields(duplicate_properties)

          for duplicate in duplicates:
            duplicate_proposals.extend(duplicate.duplicates)

        for proposal in proposals:
          proposal_key =  proposal.key()
          if proposal.status == 'pending' and proposal_key in duplicate_proposals:
            status[proposal_key] = """<strong><font color="red">
                Duplicate</font></strong>"""
          else:
            status[proposal_key] = """<strong><font color="green">
                Pending acceptance</font><strong>"""

      filter = {'org': org_entity,
                'status': ['accepted','pending','rejected']}

      # some extras for the list
      args = [ranker, status]
      visibility = 'review'
    elif idx == 2:
      # check if the current user is a mentor
      user_entity = user_logic.getCurrentUser()

      fields = {'user': user_entity,
                'scope': org_entity,
                'status': ['active', 'inactive']}
      mentor_entity = mentor_logic.getForFields(fields, unique=True)

      filter = {'org': org_entity,
                'mentor': mentor_entity,
                'status': ['pending', 'accepted', 'rejected']}
    elif idx == 3:
      filter = {'org': org_entity,
                'status': 'invalid'}
    else:
      return lists.getErrorResponse(request, "idx not valid")

    params = params_collection[idx]
    contents = helper.lists.getListData(request, params, filter,
                                        visibility=visibility, args=args)

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def listProposals(self, request, access_type,
                    page_name=None, params=None, **kwargs):
    """Lists all proposals for the organization given in kwargs.

    For params see base.View.public().
    """

    from soc.modules.gsoc.logic.models.proposal_duplicates_status import \
        logic as ds_logic

    try:
      org_entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    program_entity = org_entity.scope
    is_after_deadline = timeline_helper.isAfterEvent(program_entity.timeline,
        'accepted_students_announced_deadline')
    if is_after_deadline:
      redirect_fun = redirects.getProposalCommentRedirect
    else:
      redirect_fun = redirects.getReviewRedirect

    context = {}
    context['entity'] = org_entity
    # whether or not the amount of slots assigned should be shown
    context['slots_visible'] = org_entity.scope.allocations_visible

    # used to check the status of the duplicate process
    context['duplicate_status'] = ds_logic.getOrCreateForProgram(
        org_entity.scope)

    program_entity = org_entity.scope
    page_name = '%s %s (%s)' %(page_name, org_entity.name,
                               program_entity.short_name)

    list_params = student_proposal_view.view.getParams().copy()
    list_params['list_template'] = 'soc/student_proposal/list_for_org.html'

    np_params = list_params.copy() # new proposals
    description = ugettext('List of new %s sent to %s') % (
        np_params['name_plural'], org_entity.name)
    np_params['list_description'] = description
    np_params['public_row_extra'] = lambda entity: {
        'link': redirect_fun(entity, np_params),
    }

    rp_params = list_params.copy()# ranked proposals
    rp_params['review_field_keys'] = ['rank', 'title', 'student', 'mentor',
                                      'score', 'status', 'last_modified_on',
                                      'abstract', 'content', 'additional_info',
                                      'created_on']
    rp_params['review_field_hidden'] = ['abstract', 'content', 'additional_info',
                                        'created_on']
    rp_params['review_field_names'] = ['Rank', 'Title', 'Student', 'Mentor',
                                       'Score', 'Status', 'Last Modified On',
                                       'Abstract', 'Content', 'Additional Info',
                                       'Created On']
    rp_params['review_field_no_filter'] = ['status']
    rp_params['review_field_prefetch'] = ['scope', 'mentor', 'program']
    rp_params['review_field_extra'] = lambda entity, ranker, status: {
          'rank': ranker.FindRanks([[entity.score]])[0] + 1,
          'student': entity.scope.name(),
          'mentor': entity.mentor.name() if entity.mentor else
              '%s Proposed' % len(entity.possible_mentors),
          'status': status.get(entity.key(),
              '<font color="red">Pending rejection</font>') if (
              entity.program.allocations_visible \
              and entity.status == 'pending') else entity.status,
    }
    rp_params['review_row_action'] = {
        "type": "redirect_custom",
        "parameters": dict(new_window=True),
    }
    rp_params['review_row_extra'] = lambda entity, *args: {
        'link': redirect_fun(entity, rp_params)
    }
    rp_params['review_field_props'] = {
        "score": {
            "sorttype": "integer",
        },
        "rank": {
            "sorttype": "integer",
        },
    }
    rp_params['review_conf_min_num'] = 50

    description = ugettext('%s already under review sent to %s') %(
        rp_params['name_plural'], org_entity.name)
    rp_params['list_description'] = description

    mp_params = list_params.copy() # proposals mentored by current user
    description = ugettext('List of %s sent to %s you are mentoring') % (
        mp_params['name_plural'], org_entity.name)
    mp_params['list_description'] = description
    mp_params['public_row_extra'] = lambda entity: {
        'link': redirect_fun(entity, mp_params)
    }

    ip_params = list_params.copy() # invalid proposals
    ip_params['list_description'] = ugettext('List of invalid %s sent to %s ') % (
        ip_params['name_plural'], org_entity.name)
    ip_params['public_row_extra'] = lambda entity: {
        'link': redirect_fun(entity, ip_params)
    }

    if lists.isDataRequest(request):
      # retrieving data for a list
      return self.getListProposalsData(
          request, [np_params, rp_params, mp_params, ip_params], org_entity)

    # fill contents for all the needed lists
    contents = []

    # check if there are new proposals if so show them in a separate list
    fields = {'org': org_entity,
              'status': 'new'}
    new_proposal = sp_logic.getForFields(fields, unique=True)

    if new_proposal:
      # we should add this list because there is a new proposal
      np_list = helper.lists.getListGenerator(request, np_params, idx=0)
      contents.append(np_list)

    order = ['-score']
    # the list of proposals that have been reviewed should always be shown
    rp_list = helper.lists.getListGenerator(request, rp_params, order=order,
                                            visibility='review', idx=1)
    contents.append(rp_list)

    # check whether the current user is a mentor for the organization
    user_entity = user_logic.getCurrentUser()

    fields = {'user': user_entity,
              'scope': org_entity,
              'status': ['active','inactive']}
    mentor_entity = mentor_logic.getForFields(fields, unique=True)

    if mentor_entity:
      # show the list of all proposals that this user is mentoring
      mp_list = helper.lists.getListGenerator(request, mp_params, idx=2)
      contents.append(mp_list)

    # check if there are invalid proposals if so show them in a separate list
    fields = {'org': org_entity,
              'status': 'invalid'}
    invalid_proposal = sp_logic.getForFields(fields, unique=True)
    if invalid_proposal:
      ip_list = helper.lists.getListGenerator(request, ip_params, idx=3)
      contents.append(ip_list)

    return self._list(request, list_params, contents, page_name, context)

  def _getMapData(self, filter=None):
    """Constructs the JSON object required to generate 
       Google Maps on organization home page.

    Args:
      filter: a dict for the properties that the entities should have

    Returns: 
      A JSON object containing map data.
    """

    from soc.modules.gsoc.logic.models.student_project import logic as \
        student_project_logic
    from soc.modules.gsoc.views.models import student_project as \
        student_project_view

    sp_params = student_project_view.view.getParams().copy()

    people = {}
    projects = {}

    # get all the student_project entities for the given filter
    student_project_entities = student_project_logic.getForFields(
        filter=filter)

    # Construct a dictionary of mentors and students. For each mentor construct
    # a list of 3-tuples containing student name, project title and url.
    # And for each student a list of 3 tuples containing mentor name, project
    # title and url. Only students and mentors who have agreed to publish their
    # locations will be in the dictionary.
    for entity in student_project_entities:

      project_key_name = entity.key().id_or_name()
      project_redirect = redirects.getPublicRedirect(entity, sp_params)

      student_entity = entity.student
      student_key_name = student_entity.key().id_or_name()

      mentor_entity = entity.mentor
      mentor_key_name = mentor_entity.key().id_or_name()

      # store the project data in the projects dictionary
      projects[project_key_name] = {'title': entity.title,
                                    'redirect': project_redirect,
                                    'student_key': student_key_name,
                                    'student_name': student_entity.name(),
                                    'mentor_key': mentor_key_name,
                                    'mentor_name': mentor_entity.name()}

      if mentor_entity.publish_location:
        if mentor_key_name not in people:
          # we have not stored the information of this mentor yet
          people[mentor_key_name] = {
              'type': 'mentor',
              'name': mentor_entity.name(),
              'lat': mentor_entity.latitude,
              'lon': mentor_entity.longitude,
              'projects': []
              }

        # add this project to the mentor's list
        people[mentor_key_name]['projects'].append(project_key_name)

      if student_entity.publish_location:
        if student_key_name not in people:
          # new student, store the name and location
          people[student_key_name] = {
              'type': 'student',
              'name': student_entity.name(),
              'lat': student_entity.latitude,
              'lon': student_entity.longitude,
              'projects': [],
              }

        # append the current project to the known student's list of projects
        people[student_key_name]['projects'].append(project_key_name)

    # combine the people and projects data into one JSON object
    data = {'people': people,
            'projects': projects}

    return simplejson.dumps(data)

  def getHomeData(self, request, ap_params, entity):
    """Returns the home data.
    """

    idx = lists.getListIndex(request)

    if idx == 0:
      params = ap_params
      # only show projects that have not failed
      fields= {'scope': entity,
               'status': ['accepted', 'completed']}
    else:
      return lists.getErrorResponse(request, "idx not valid")

    contents = lists.getListData(request, params, fields, 'org_home')

    return lists.getResponse(request, contents)

  @decorators.check_access
  def home(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """See base.View._public().
    """

    from soc.modules.gsoc.views.models import student_project as \
        student_project_view

    entity = self._logic.getFromKeyFieldsOr404(kwargs)
    program_entity = entity.scope

    params = params.copy() if params else {}

    if timeline_helper.isAfterEvent(program_entity.timeline,
                                    'accepted_students_announced_deadline'):
      # accepted projects
      ap_params = student_project_view.view.getParams().copy()

      ap_params['list_description'] = self.DEF_ACCEPTED_PROJECTS_MSG_FMT % (
          entity.name)

      if lists.isDataRequest(request):
        return self.getHomeData(request, ap_params, entity)

      ap_list = lists.getListGenerator(request, ap_params, idx=0,
                                       visibility='org_home', order=['name'])

      contents = [ap_list]

      extra_context = {}
      # construct the list and put it into the context
      extra_context['list'] = soc.logic.lists.Lists(contents)

      fields= {'scope': entity,
               'status': ['accepted', 'completed']}

      # obtain data to construct the organization map as json object
      extra_context['org_map_data'] = self._getMapData(fields)
      params['context'] = extra_context

    return super(View, self).home(request, 'any_access', page_name=page_name,
                                  params=params, **kwargs)


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
pick_suggested_tags = decorators.view(view.pickSuggestedTags)
