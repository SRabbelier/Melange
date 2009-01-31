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

"""Views for Clubs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import http
from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.logic.models import club_app as club_app_logic
from soc.logic.models import club as club_logic
from soc.logic.models import request as request_logic
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import group

import soc.logic.models.club
import soc.views.helper


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
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsClubAdminForClub', ('checkIsGroupActive', club_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['home'] = ['allow']
    rights['list'] = ['checkIsDeveloper']
    rights['apply_member'] = ['checkIsUser', ('checkIsGroupActive', club_logic)]
    rights['list_requests'] = ['checkIsClubAdminForClub']
    rights['list_roles'] = ['checkIsClubAdminForClub']
    rights['applicant'] = [('checkIsApplicationAccepted', club_app_logic)]

    new_params = {}
    new_params['logic'] = soc.logic.models.club.logic
    new_params['rights'] = rights
    new_params['name'] = "Club"
    new_params['url_name'] = "club"
    new_params['sidebar_grouping'] = 'Clubs'

    patterns = []

    patterns += [(r'^%(url_name)s/(?P<access_type>applicant)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.applicant', 
        "%(name)s Creation via Accepted Application"),
        (r'^%(url_name)s/(?P<access_type>apply_member)$',
        'soc.views.models.%(module_name)s.apply_member', 
        "List of all %(name_plural)s you can apply to"),]

    new_params['extra_django_patterns'] = patterns

    new_params['sidebar_additional'] = [
        ('/' + new_params['url_name'] + '/apply_member', 'Join a Club', 'apply_member'),]

    new_params['create_extra_dynafields'] = {
        'clean_link_id': cleaning.clean_new_club_link_id('link_id', 
            club_logic, club_app_logic)
        }
    new_params['edit_extra_dynafields'] = {
        'founded_by': forms.CharField(widget=widgets.ReadOnlyInput(),
                                   required=False),
        'clean_link_id': cleaning.clean_link_id('link_id')
        }

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special form for applicants
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False),
        'clean_link_id': cleaning.clean_link_id('link_id')}

    applicant_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynafields = updated_fields)

    params['applicant_create_form'] = applicant_create_form

  @decorators.merge_params
  @decorators.check_access
  def applicant(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Handles the creation of a club via an approved club application.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.applicantPost(request, context, params, **kwargs)
    else:
      # request.method == 'GET'
      return self.applicantGet(request, context, params, **kwargs)

  def applicantGet(self, request, context, params, **kwargs):
    """Handles the GET request concerning the creation of a club via an
    approved club application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # find the application
    key_fields = club_app_logic.logic.getKeyFieldsFromFields(kwargs)
    application = club_app_logic.logic.getFromKeyFields(key_fields)

    # extract the application fields
    field_names = application.properties().keys()
    fields = dict( [(i, getattr(application, i)) for i in field_names] )

    # create the form using the fields from the application as the initial value
    form = params['applicant_create_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

  def applicantPost(self, request, context, params, **kwargs):
    """Handles the POST request concerning the creation of a club via an
    approved club application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # populate the form using the POST data
    form = params['applicant_create_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, fields = soc.views.helper.forms.collectCleanedFields(form)

    # fill in the founder of the club
    user = user_logic.logic.getForCurrentAccount()
    fields['founder'] = user

    if not key_name:
      key_fields =  self._logic.getKeyFieldsFromFields(fields)
      key_name = self._logic.getKeyNameFromFields(key_fields)

    # create the club entity
    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # redirect to notifications list to see the admin invite
    return http.HttpResponseRedirect('/notification/list')


  @decorators.merge_params
  @decorators.check_access
  def applyMember(self, request, access_type,
                  page_name=None, params=None, **kwargs):
    """Shows a list of all clubs and you can choose one to apply to become a member.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    list_params = params.copy()
    list_params['list_action'] = (redirects.getRequestRedirectForRole, 'club_member')
    list_params['list_description'] = 'Choose a club to apply to become a Club Member'

    return self.list(request, access_type, 
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
      submenu = (redirects.getInviteRedirectForRole(group_entity, 'club_member'),
          "Invite a Member", 'any_access')
      submenus.append(submenu)

      # add a link to the request page
      submenu = (redirects.getListRequestsRedirect(group_entity, params), 
          "List Requests and Invites", 'any_access')
      submenus.append(submenu)

      # add a link to the edit page
      submenu = (redirects.getEditRedirect(group_entity, params), 
          "Edit Club Profile", 'any_access')
      submenus.append(submenu)

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

    if roles.get('club_member') or roles.get('club_admin'):
      submenu = (redirects.getCreateDocumentRedirect(group_entity, 'club'),
          "Create new document", 'any_access')
      submenus.append(submenu)

    return submenus


view = View()

applicant = view.applicant
apply_member = view.applyMember
create = view.create
delete = view.delete
edit = view.edit
home = view.home
list = view.list
list_requests = view.listRequests
list_roles = view.listRoles
public = view.public
export = view.export
pick = view.pick
