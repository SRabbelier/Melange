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

"""Views for Programs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.logic.models import mentor as mentor_logic
from soc.logic.models import org_admin as org_admin_logic
from soc.logic.models import program as program_logic
from soc.logic.models import student as student_logic
from soc.logic.models.document import logic as document_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import presence
from soc.views.models import document as document_view
from soc.views.models import sponsor as sponsor_view
from soc.views.sitemap import sidebar

import soc.logic.models.program
import soc.models.work


class View(presence.View):
  """View methods for the Program model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['allow']
    rights['create'] = [('checkSeeded', ['checkHasActiveRoleForScope', 
        host_logic.logic])]
    rights['edit'] = ['checkIsHostForProgram']
    rights['delete'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = soc.logic.models.program.logic
    new_params['rights'] = rights

    new_params['scope_view'] = sponsor_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Program"
    new_params['sidebar_grouping'] = 'Programs'
    new_params['document_prefix'] = "program"

    new_params['extra_dynaexclude'] = ['timeline', 'org_admin_agreement',
        'mentor_agreement', 'student_agreement']

    # TODO add clean field to check for uniqueness in link_id and scope_path
    new_params['create_extra_dynaproperties'] = {
        'description': forms.fields.CharField(widget=helper.widgets.TinyMCE(
            attrs={'rows':10, 'cols':40})),
        'scope_path': forms.CharField(widget=forms.HiddenInput, required=True),
        'workflow': forms.ChoiceField(choices=[('gsoc','Project-based'),
            ('ghop','Task-based')], required=True),
        }

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
          filter_fields={'prefix': new_params['document_prefix']},
          required=False, label=label, help_text=help_text)

    result['workflow'] = forms.CharField(widget=widgets.ReadOnlyInput(),
                                         required=True)
    result['clean'] = cleaning.clean_refs(new_params,
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

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    super(View, self)._editPost(request, entity, fields)

    if not entity:
      # there is no existing entity so create a new timeline
      fields['timeline'] = self._createTimelineForType(fields)
    else:
      # use the timeline from the entity
      fields['timeline'] = entity.timeline

  def _createTimelineForType(self, fields):
    """Creates and stores a timeline model for the given type of program.
    """

    workflow = fields['workflow']

    timeline_logic = program_logic.logic.TIMELINE_LOGIC[workflow]

    properties = timeline_logic.getKeyFieldsFromFields(fields)
    key_name = timeline_logic.getKeyNameFromFields(properties)

    properties['scope'] = fields['scope']

    timeline = timeline_logic.updateOrCreateFromKeyName(properties, key_name)
    return timeline

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
        # show the documents for this program, even for not logged in users
        items += document_view.view.getMenusForScope(entity, params)
        items += self._getTimeDependentEntries(entity, params, id, user)

      try:
        # check if the current user is a host for this program
        rights.doCachedCheck('checkIsHostForProgram',
                             {'scope_path': entity.scope_path,
                              'link_id': entity.link_id}, [])

        if entity.status == 'invisible':
          # still add the document links so hosts can see how it looks like
          items += document_view.view.getMenusForScope(entity, params)
          items += self._getTimeDependentEntries(entity, params, id, user)

        items += [(redirects.getReviewOverviewRedirect(
            entity, {'url_name': 'org_app'}),
            "Review Organization Applications", 'any_access')]
        # add link to edit Program Profile
        items += [(redirects.getEditRedirect(entity, params),
            'Edit Program Profile','any_access')]
        # add link to edit Program Timeline
        items += [(redirects.getEditRedirect(entity, {'url_name': 'timeline'}),
            "Edit Program Timeline", 'any_access')]
        # add link to create a new Program Document
        items += [(redirects.getCreateDocumentRedirect(entity, 'program'),
            "Create a New Document", 'any_access')]
        # add link to list all Program Document
        items += [(redirects.getListDocumentsRedirect(entity, 'program'),
            "List Documents", 'any_access')]

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

      if user:
        # add the 'List my Organization Applications' link
        items += [
            (redirects.getListSelfRedirect(program_entity,
                                           {'url_name' : 'org_app'}),
             "List My Organization Applications", 'any_access')]

    # get the student entity for this user and program
    filter = {'user': user,
              'scope': program_entity,
              'status': 'active'}
    student_entity = student_logic.logic.getForFields(filter, unique=True)

    if student_entity:
      items += self._getStudentEntries(program_entity, student_entity,
                                       params, id, user)

    # get mentor and org_admin entity for this user and program
    filter = {'user': user,
              'program': program_entity,
              'status': 'active'}
    mentor_entity = mentor_logic.logic.getForFields(filter, unique=True)
    org_admin_entity = org_admin_logic.logic.getForFields(filter, unique=True)

    if mentor_entity or org_admin_entity:
      items += self._getOrganizationEntries(program_entity, org_admin_entity,
                                            mentor_entity, params, id, user)

    if not (student_entity or mentor_entity or org_admin_entity):
      if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
        # this user does not have a role yet for this program
        items += [('/student/apply/%s' % (program_entity.key().name()),
            "Register as a Student", 'any_access')]

    if timeline_helper.isAfterEvent(timeline_entity,
        'accepted_organization_announced_deadline'):
      # add a link to list all the organizations
      items += [(redirects.getPublicListRedirect(program_entity, 
          {'url_name': 'org'}),
          "List participating Organizations", 'any_access')]

      if not student_entity:
        # add apply to become a mentor link
        items += [('/org/apply_mentor/%s' % (program_entity.key().name()),
         "Apply to become a Mentor", 'any_access')]

    return items

  def _getStudentEntries(self, program_entity, student_entity, 
                         params, id, user):
    """Returns a list with menu items for students in a specific program.
    """

    items = []

    timeline_entity = program_entity.timeline

    if timeline_helper.isActivePeriod(timeline_entity, 'student_signup'):
      items += [('/student_proposal/list_orgs/%s' % (
          student_entity.key().name()),
          "Submit your Student Proposal", 'any_access')]
      items += [(redirects.getListSelfRedirect(student_entity,
          {'url_name':'student_proposal'}),
         "List my Student Proposals", 'any_access')]

    return items

  def _getOrganizationEntries(self, program_entity, org_admin_entity,
                              mentor_entity, params, id, user):
    """Returns a list with menu items for org admins and mentors in a
       specific program.
    """

    # TODO(ljvderijk) think about adding specific org items like submit review

    items = []

    return items


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
home = decorators.view(view.home)
pick = decorators.view(view.pick)
