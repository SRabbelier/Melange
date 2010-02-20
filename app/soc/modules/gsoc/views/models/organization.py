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
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import itertools

from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
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
from soc.views.models import group

from soc.modules.gsoc.logic import cleaning
from soc.modules.gsoc.logic.models.mentor import logic as mentor_logic
from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic
from soc.modules.gsoc.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.gsoc.logic.models.organization import logic as org_logic
from soc.modules.gsoc.logic.models.program import logic as program_logic

from soc.modules.gsoc.models.organization import OrgTag

from soc.modules.gsoc.views.models import program as program_view
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
              filter=['scope_path']),
        'clean_tags': cleaning.cleanTagsList('tags', cleaning.COMMA_SEPARATOR)
        }

    new_params['org_app_logic'] = org_app_logic

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params)

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
               'multiple': True
            }            
        })

    return self.json(request, data, False)

  # TODO (dhans): merge common items with the GHOP module in a single function
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
          "View all Student Proposals", 'any_access')
      submenus.append(submenu)


    if admin_entity:
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


  def getListProposalsData(self, request, rp_params, mp_params,
                           p_params, org_entity):
    """Returns the list data for listProposals.
    """

    from soc.modules.gsoc.logic.models.ranker_root import logic \
        as ranker_root_logic
    from soc.modules.gsoc.logic.models.student_proposal import logic \
        as sp_logic
    from soc.modules.gsoc.models import student_proposal
    from soc.modules.gsoc.views.helper import list_info as list_info_helper
    from soc.modules.gsoc.views.models import student_proposal \
        as student_proposal_view

    idx = request.GET.get('idx', '')
    idx = int(idx) if idx.isdigit() else -1

    args = order = []

    if idx == 0:
      # retrieve the ranker
      fields = {'link_id': student_proposal.DEF_RANKER_NAME,
                'scope': org_entity}

      ranker_root = ranker_root_logic.getForFields(fields, unique=True)
      ranker = ranker_root_logic.getRootFromEntity(ranker_root)

      keys = []

      # only when the program allows allocations
      # to be seen we should color the list
      if org_entity.scope.allocations_visible:
        proposals = sp_logic.getProposalsToBeAcceptedForOrg(org_entity)
        keys = [i.key() for i in proposals]

        # show the amount of slots assigned on the webpage
        context['slots_visible'] = True

      # TODO(ljvderijk) once sorting with IN operator is fixed,
      # make this list show more
      filter = {'org': org_entity,
                'status': 'pending'}
      params = rp_params
      # order by descending score
      order = ['-score']
      args = [ranker, keys]
    elif idx == 1:
      # check if the current user is a mentor
      user_entity = user_logic.getForCurrentAccount()

      fields = {'user': user_entity,
          'scope': org_entity,}
      mentor_entity = mentor_logic.getForFields(fields, unique=True)

      filter = {'org': org_entity,
                'mentor': mentor_entity,
                'status': 'pending'}
      params = mp_params
    elif idx == 2:
      filter = {'org': org_entity}
      params = p_params
    else:
      return responses.jsonErrorResponse(request, "idx not valid")

    contents = helper.lists.getListData(request, params, filter, 'public',
                                        order=order, args=args)
    json = simplejson.dumps(contents)

    return responses.jsonResponse(request, json)

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

    rp_params = list_params.copy()# ranked proposals
    rp_params['list_row'] = ('soc/%(module_name)s/list/'
        'detailed_row.html' % list_params)
    rp_params['list_heading'] = ('soc/%(module_name)s/list/'
        'detailed_heading.html' % list_params)
    rp_params['public_row_extra'] = lambda entity, *args: {
        'link': redirects.getReviewRedirect(entity, rp_params)
    }
    rp_params['public_field_extra'] = lambda entity, ranker, keys: {
          'rank': ranker.FindRanks([[entity.score]])[0] + 1,
          'item_class': entity.key() in keys,
    }

    description = ugettext('%s already under review sent to %s') %(
        rp_params['name_plural'], org_entity.name)
    rp_params['list_description'] = description

    mp_params = list_params.copy() # proposals mentored by current user
    description = ugettext('List of %s sent to %s you are mentoring') % (
        mp_params['name_plural'], org_entity.name)
    mp_params['list_description'] = description
    mp_params['public_row_extra'] = lambda entity: {
        'link': redirects.getReviewRedirect(entity, mp_params),
    }

    p_params = list_params.copy() # proposals
    p_params['list_description'] = ugettext('List of %s sent to %s ') % (
        p_params['name_plural'], org_entity.name)
    p_params['public_row_extra'] = lambda entity: {
        'link': redirects.getReviewRedirect(entity, p_params),
    }

    # fill contents with all the needed lists
    if request.GET.get('fmt') == 'json':
      return self.getListProposalsData(request, rp_params, mp_params,
                                       p_params, org_entity)

    rp_list = helper.lists.getListGenerator(request, rp_params, idx=0)
    mp_list = helper.lists.getListGenerator(request, mp_params, idx=1)
    p_list = helper.lists.getListGenerator(request, p_params, idx=2)

    contents = [rp_list, mp_list, p_list]

    return self._list(request, list_params, contents, page_name, context)


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
                                      