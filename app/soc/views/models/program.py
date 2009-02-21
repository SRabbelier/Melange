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

from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.logic.models import program as program_logic
from soc.logic.models.document import logic as document_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import presence_with_tos
from soc.views.models import document as document_view
from soc.views.models import sponsor as sponsor_view
from soc.views.sitemap import sidebar

import soc.logic.models.program
import soc.models.work


class View(presence_with_tos.View):
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
    rights['create'] = [('checkSeeded', ['checkHasActiveRoleForScope', host_logic.logic])]
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
        ('tos_link_id', soc.models.work.Work.link_id.help_text,
         ugettext('Terms of Service Document link ID'))
        ]

    result = {}

    for key, help_text, label in reference_fields:
      result[key] = widgets.ReferenceField(
          reference_url='document', filter=['__scoped__'],
          filter_fields={'prefix': new_params['document_prefix']},
          required=False, label=label, help_text=help_text)

    result['workflow'] = forms.CharField(widget=widgets.ReadOnlyInput(),
                                         required=True)

    new_params['edit_extra_dynaproperties'] = result


    references = [
        ('org_admin_agreement_link_id', 'org_admin_agreement', document_logic,
         lambda x: x.org_admin_agreement),
        ('mentor_agreement_link_id', 'mentor_agreement', document_logic,
         lambda x: x.mentor_agreement),
        ('student_agreement_link_id', 'student_agreement', document_logic,
         lambda x: x.student_agreement),
        ]

    new_params['references'] = references

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """

    if not entity:
      # there is no existing entity so create a new timeline
      fields['timeline'] = self._createTimelineForType(fields)
    else:
      # use the timeline from the entity
      fields['timeline'] = entity.timeline

    super(View, self)._editPost(request, entity, fields)

  def _createTimelineForType(self, fields):
    """Creates and stores a timeline model for the given type of program.
    """

    workflow = fields['workflow']

    timeline_logic = program_logic.logic.TIMELINE_LOGIC[workflow]

    key_name = self._logic.getKeyNameFromFields(fields)

    properties = {'scope_path': key_name}

    timeline = timeline_logic.updateOrCreateFromFields(properties, properties)
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
    fields = {'status':['invisible', 'visible']}
    entities = logic.getForFields(fields)

    menus = []

    rights.setCurrentUser(id, user)
    filter_args = {}

    for entity in entities:
      items = []

      if entity.status == 'visible':
        # show the documents for this program, even for not logged in users
        items += document_view.view.getMenusForScope(entity, params)
        items += self._getTimeDependentEntries(entity, params, id, user)

        url = redirects.getPublicListRedirect(entity, {'url_name': 'org'})
        items += [(url, "List Organizations", 'any_access')]

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

    return items


view = View()

admin = view.admin
create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export
home = view.home
pick = view.pick
