#!/usr/bin/env python2.5
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

"""Views for Programs.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.logic.models import program as program_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import presence
from soc.views.models import document as document_view
from soc.views.models import sponsor as sponsor_view

import soc.cache.logic
import soc.logic.models.program
import soc.models.work


class View(presence.View):
  """View methods for the Program model.
  """

  DEF_SLOTS_ALLOCATION_MSG = ugettext("Use this view to assign slots.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasRoleForScope',
        host_logic.logic])]
    rights['edit'] = ['checkIsHostForProgram']
    rights['delete'] = ['checkIsDeveloper']
    rights['accepted_orgs'] = [('checkIsAfterEvent',
        ['accepted_organization_announced_deadline',
         '__all__', program_logic.logic])]

    new_params = {}
    new_params['logic'] = soc.logic.models.program.logic
    new_params['rights'] = rights

    new_params['scope_view'] = sponsor_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = 'program'

    new_params['extra_dynaexclude'] = ['timeline', 'org_admin_agreement',
        'mentor_agreement', 'student_agreement']

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>assign_slots)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.assign_slots',
          'Assign slots'),
        (r'^%(url_name)s/(?P<access_type>slots)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.slots',
          'Assign slots (JSON)'),
        (r'^%(url_name)s/(?P<access_type>show_duplicates)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.show_duplicates',
          'Show duplicate slot assignments'),
        (r'^%(url_name)s/(?P<access_type>assigned_proposals)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.assigned_proposals',
          "Assigned proposals for multiple organizations"),
        (r'^%(url_name)s/(?P<access_type>accepted_orgs)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.accepted_orgs',
          "List all accepted organizations"),
        (r'^%(url_name)s/(?P<access_type>list_projects)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.list_projects',
          "List all Student Projects"),
        (r'^%(url_name)s/(?P<access_type>list_participants)/%(key_fields)s$',
          '%(module_package)s.%(module_name)s.list_participants',
          "List all Participants for"),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['create_dynafields'] = [
        {'name': 'link_id',
         'base': forms.fields.CharField,
         'label': 'Program Link ID',
         },
        ]

    # TODO: add clean field to check for uniqueness in link_id and scope_path
    new_params['create_extra_dynaproperties'] = {
        'description': forms.fields.CharField(widget=helper.widgets.TinyMCE(
            attrs={'rows':10, 'cols':40})),
        'accepted_orgs_msg': forms.fields.CharField(required=False,
            widget=helper.widgets.TinyMCE(attrs={'rows':10, 'cols':40})),
        'scope_path': forms.CharField(widget=forms.HiddenInput, required=True),
        }

    params = dicts.merge(params, new_params, sub_merge=True)

    new_params = {}

    reference_fields = [
        ('org_admin_agreement_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Organization Admin Agreement Document link ID')),
        ('mentor_agreement_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Mentor Agreement Document link ID')),
        ('student_agreement_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Student Agreement Document link ID')),
        ('home_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Home page Document link ID')),
        ]

    result = {}

    for key, help_text, label in reference_fields:
      result[key] = widgets.ReferenceField(
          reference_url='document', filter=['__scoped__'],
          filter_fields={'prefix': params['document_prefix']},
          required=False, label=label, help_text=help_text)

    result['clean'] = cleaning.clean_refs(params,
                                          [i for i,_,_ in reference_fields])

    new_params['edit_extra_dynaproperties'] = result

    document_references = [
        ('org_admin_agreement_link_id', 'org_admin_agreement',
         lambda x: x.org_admin_agreement),
        ('mentor_agreement_link_id', 'mentor_agreement',
         lambda x: x.mentor_agreement),
        ('student_agreement_link_id', 'student_agreement',
         lambda x: x.student_agreement),
        ]

    new_params['references'] = document_references

    new_params['public_field_keys'] = ["name", "scope_path"]
    new_params['public_field_names'] = ["Program Name", "Program Owner"]

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    super(View, self)._editPost(request, entity, fields)

    if not entity:
      # there is no existing entity so create a new timeline
      fields['timeline'] = self._params['logic'].createTimelineForType(fields)
    else:
      # use the timeline from the entity
      fields['timeline'] = entity.timeline

  @decorators.merge_params
  @decorators.check_access
  def listParticipants(self, request, access_type, page_name=None,
                       params=None, **kwargs):
    """View that lists the roles of all the participants for a single Program.

    For args see base.list().
    """

    from django.utils import simplejson

    from soc.views.models.role import ROLE_VIEWS

    program_logic = params['logic']
    program_entity = program_logic.getFromKeyFieldsOr404(kwargs)

    if request.GET.get('fmt') == 'json':
      # get index
      idx = request.GET.get('idx', '')
      idx = int(idx) if idx.isdigit() else -1

      participants_logic = params['participants_logic']

      if idx == -1 or idx > len(participants_logic):
        return responses.jsonErrorResponse(request, "idx not valid")

      # get role params that belong to the given index
      (role_logic, query_field) = participants_logic[idx]
      role_view = ROLE_VIEWS[role_logic.role_name]
      role_params = role_view.getParams().copy()

      # construct the query for the specific list
      fields = {query_field: program_entity,
                'status': ['active','inactive']}

      # return getListData
      contents = lists.getListData(request, role_params, fields,
                                   visibility='admin')

      json = simplejson.dumps(contents)
      return responses.jsonResponse(request, json)

    # we need to generate the lists to be shown on this page
    participants = []

    idx = 0
    for (role_logic, _) in params['participants_logic']:
      # retrieve the role view belonging to the logic
      role_view = ROLE_VIEWS[role_logic.role_name]
      role_params = role_view.getParams().copy()
      role_params['list_description'] = 'List of All %s' %(
          role_params['name_plural'])

      role_list = lists.getListGenerator(request, role_params, idx=idx)
      participants.append(role_list)

      idx = idx + 1

    page_name = '%s %s' %(page_name, program_entity.name)
    return self._list(request, params, contents=participants,
                      page_name=page_name)

  def _getStandardProgramEntries(self, entity, id, user, params):
    """Returns those entries for a program which are available to regular users,
    not only to hosts or developers. 
    """

    items = []

    # show the documents for this program, even for not logged in users
    items += document_view.view.getMenusForScope(entity, params)

    # also show time-dependent entities for a given user
    items += self._getTimeDependentEntries(entity, params, id, user)

    return items

  def _getTimeDependentEntries(self, program_entity, params, id, user):
    """Returns a list with time dependent menu items. Should be redefined
    in a module specific view.
    """

    return []

  def _getHostEntries(self, entity, params, prefix):
    """Returns a list with menu items for program host.

    Args:
      entity: program entity to get the entries for
      params: view specific params
      prefix: module prefix for the program entity
    """

    items = []

    # add link to edit Program Profile
    items += [(redirects.getEditRedirect(entity, params),
            'Edit Program Profile', 'any_access')]
    # add link to edit Program Timeline
    items += [(redirects.getEditRedirect(entity, 
            {'url_name': prefix + '/timeline'}),
            "Edit Program Timeline", 'any_access')]
    # add link to create a new Program Document
    items += [(redirects.getCreateDocumentRedirect(
            entity, params['document_prefix']),
            "Create a New Document", 'any_access')]
    # add link to list all Program Document
    items += [(redirects.getListDocumentsRedirect(
            entity, params['document_prefix']),
            "List Documents", 'any_access')]
    # add link to list all participants
    items += [(redirects.getListParticipantsRedirect(entity, params),
               "List Participants", 'any_access')]

    timeline_entity = entity.timeline

    org_app_logic = params['org_app_logic']
    org_app_survey = org_app_logic.getForProgram(entity)

    if not timeline_helper.isAfterEvent(timeline_entity, 'org_signup'):
      # add link to create/edit OrgAppSurvey
      items += [(redirects.getCreateSurveyRedirect(
                    entity, params['document_prefix'], prefix + '/org_app'),
                'Edit Org Application Survey','any_access')]

    if org_app_survey:
      # add link to Review Org Applications
        items += [(redirects.getReviewOverviewRedirect(
            org_app_survey, params),
            "Review Organization Applications", 'any_access')]

    return items

  def _getStudentEntries(self, program_entity, student_entity,
                         params, id, user, prefix):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    if timeline_helper.isBeforeEvent(program_entity.timeline, 'program_end') \
        and student_entity.status == 'active':
      items += [(redirects.getEditRedirect(student_entity,
          {'url_name': prefix + '/student'}),
          "Edit my Student Profile", 'any_access')]

      items += [(redirects.getManageRedirect(student_entity,
          {'url_name': prefix + '/student'}),
          "Resign as a Student", 'any_access')]

    return items

  def _getOrganizationEntries(self, program_entity, org_admin_entity,
                              mentor_entity, params, id, user):
    """Returns a list with menu items for org admins and mentors in a
       specific program.
    """

    # TODO(ljvderijk): think about adding specific org items like submit review

    items = []

    return items


view = View()

accepted_orgs = responses.redirectLegacyRequest
list_projects = responses.redirectLegacyRequest
admin = responses.redirectLegacyRequest
assign_slots = responses.redirectLegacyRequest
assigned_proposals = responses.redirectLegacyRequest
create = responses.redirectLegacyRequest
delete = responses.redirectLegacyRequest
edit = responses.redirectLegacyRequest
list = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
export = responses.redirectLegacyRequest
show_duplicates = responses.redirectLegacyRequest
slots = responses.redirectLegacyRequest
home = responses.redirectLegacyRequest
pick = responses.redirectLegacyRequest
