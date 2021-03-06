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

"""Views for Clubs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import club  as club_logic
from soc.logic.models import club_admin as club_admin_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import group

import soc.logic.models.club


class View(group.View):
  """View methods for the Club model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkHasRoleForLinkId', club_admin_logic.logic),
                      ('checkGroupIsActiveForLinkId', club_logic.logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['list'] = ['checkIsDeveloper']
    rights['apply_member'] = ['checkIsUser',
                              ('checkGroupIsActiveForScopeAndLinkId', 
                               club_logic.logic)]
    rights['list_requests'] = [('checkHasRoleForLinkId', 
                                club_admin_logic.logic)]
    rights['list_roles'] = [('checkHasRoleForLinkId', 
                             club_admin_logic.logic)]

    new_params = {}
    new_params['logic'] = soc.logic.models.club.logic
    new_params['rights'] = rights
    new_params['name'] = "Club"
    new_params['url_name'] = "club"
    new_params['document_prefix'] = "club"
    new_params['sidebar_grouping'] = 'Clubs'

    new_params['public_template'] = 'soc/group/public.html'

    patterns = []

    patterns += [(r'^%(url_name)s/(?P<access_type>apply_member)$',
        'soc.views.models.%(module_name)s.apply_member', 
        "List of all %(name_plural)s you can apply to"),]

    new_params['extra_django_patterns'] = patterns

    new_params['sidebar_additional'] = [
        ('/' + new_params['url_name'] + '/apply_member', 
         'Join a Club', 'apply_member'),]

    new_params['create_dynafields'] = [
        {'name': 'link_id',
         'base': forms.fields.CharField,
         'label': 'Club Link ID',
         },
        ]

    new_params['create_extra_dynaproperties'] = {
        'clean' : cleaning.validate_new_group('link_id', 'scope_path',
            club_logic)}

    # get rid of the clean method
    new_params['edit_extra_dynaproperties'] = {
        'clean' : (lambda x: x.cleaned_data)}

    new_params['public_field_keys'] = ["name", "link_id", "short_name"]
    new_params['public_field_names'] = ["Name", "Link ID", "Short name"]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special form for applicants
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False),
        'clean_link_id': cleaning.clean_link_id('link_id')}

    applicant_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynaproperties = updated_fields)

    self._params['applicant_create_form'] = applicant_create_form

  @decorators.merge_params
  @decorators.check_access
  def applyMember(self, request, access_type,
                  page_name=None, params=None, **kwargs):
    """Shows a list of all clubs and you can choose one to 
       apply to become a member.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    list_params = params.copy()
    list_params['public_row_extra'] = lambda entity: {
        'link': redirects.getRequestRedirectForRole(entity, 'club_member')
    }
    list_params['list_description'] = ugettext('Choose a club to ' 
                                               'apply to become a Club Member.')

    return self.list(request, 'allow', 
        page_name, params=list_params, filter=None)


  def _getExtraMenuItems(self, role_description, params=None):
    """Used to create the specific club menu entries.

    For args see group.View._getExtraMenuItems().
    """

    submenus = []

    group_entity = role_description['group']
    roles = role_description['roles']
  
    if roles.get('club_admin'):
      # add a link to the management page
      submenu = (redirects.getListRolesRedirect(group_entity, params),
          "Manage Admins and Members", 'any_access')
      submenus.append(submenu)

      # add a link to invite an admin
      submenu = (redirects.getInviteRedirectForRole(group_entity, 'club_admin'),
          "Invite an Admin", 'any_access')
      submenus.append(submenu)

      # add a link to invite a member
      submenu = (redirects.getInviteRedirectForRole(group_entity, 
          'club_member'), "Invite a Member", 'any_access')
      submenus.append(submenu)

      # add a link to the request page
      submenu = (redirects.getListRequestsRedirect(group_entity, params), 
          "List Requests and Invites", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(group_entity, params), 
          "Edit Club Profile", 'any_access')
      submenus.append(submenu)

    if roles.get('club_member') or roles.get('club_admin'):
      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'club'),
          "Create a New Document", 'any_access')
      submenus.append(submenu)

      submenu = (redirects.getListDocumentsRedirect(group_entity, 'club'),
          "List Documents", 'any_access')
      submenus.append(submenu)

    if roles.get('club_admin'):
      # add a link to resign as club admin
      submenu = (redirects.getManageRedirect(roles['club_admin'], 
          {'url_name': 'club_admin'}), 
          "Resign as Club Admin", 'any_access')
      submenus.append(submenu)

    if roles.get('club_member'):
      # add a link to resign as club member
      submenu = (redirects.getManageRedirect(roles['club_member'], 
          {'url_name' : 'club_member'}), 
          "Resign as Club Member", 'any_access')
      submenus.append(submenu)

    return submenus


view = View()

admin = decorators.view(view.admin)
apply_member = decorators.view(view.applyMember)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
home = decorators.view(view.home)
list = decorators.view(view.list)
list_requests = decorators.view(view.listRequests)
list_roles = decorators.view(view.listRoles)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
