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

"""Views for the User's own profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import datetime

from google.appengine.api import users

from django import forms
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import models as model_logic
from soc.logic.models.user import logic as user_logic
from soc.logic.models.site import logic as site_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import lists
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models import role as role_view


class View(base.View):
  """Views for User own profiles.
  """

  DEF_ROLE_LIST_MSG_FMT = ugettext("Your roles as %(name)s.")
  DEF_NO_ROLES_MSG_FMT = ugettext("You don't have any roles in %s.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['any_access'] = ['allow']
    rights['create_profile'] = ['checkIsUnusedAccount']
    rights['edit_profile'] = ['checkHasUserEntity']
    rights['roles'] = ['checkIsUser']
    rights['requests'] = ['checkIsUser']
    rights['signIn'] = ['checkNotLoggedIn']
    rights['notification'] = ['checkIsUser']

    new_params = {}
    new_params['rights'] = rights
    new_params['logic'] = user_logic

    new_params['name'] = 'User'
    new_params['module_name'] = 'user_self'
    new_params['url_name'] = 'user'

    new_params['create_template'] = 'soc/user/edit_profile.html'
    new_params['edit_template'] = 'soc/user/edit_profile.html'
    new_params['save_message'] = [ugettext('Profile saved.')]
    new_params['edit_redirect'] = '/%(url_name)s/edit_profile'

    # set the specific fields for the users profile page
    new_params['extra_dynaexclude'] = ['former_accounts',
        'account', 'is_developer', 'status', 'agreed_to_tos_on']

    new_params['create_extra_dynaproperties'] = {
        'clean_agreed_to_tos': cleaning.clean_agrees_to_tos('agreed_to_tos'),
        'clean_link_id': cleaning.clean_user_not_exist('link_id'),}

    new_params['edit_extra_dynaproperties'] = {
        'clean_link_id': cleaning.clean_user_is_current('link_id', False),
        'agreed_to_tos_on': forms.DateTimeField(
          widget=widgets.ReadOnlyInput(attrs={'disabled':'true'}),
          required=False),
        }

    new_params['sidebar_heading'] = 'User (self)'
    new_params['sidebar'] = [
        ('login', 'Sign In', 'signIn'),
        (redirects.getCreateProfileRedirect(new_params),
            'Create Profile', 'create_profile'),
        (redirects.getEditProfileRedirect(new_params),
            'Edit Profile', 'edit_profile'),
        (redirects.getRolesRedirect(new_params), 'Roles', 'roles'),
        (redirects.getRequestsRedirect(new_params), 'Requests', 'requests'),
        ]

    patterns = []

    page_name = ugettext('Create your profile')
    patterns += [(r'^%(url_name)s/(?P<access_type>create_profile)$',
                  'soc.views.models.%(module_name)s.create', page_name)]

    page_name = ugettext('Edit your profile')
    patterns += [(r'^%(url_name)s/(?P<access_type>edit_profile)$',
                  'soc.views.models.%(module_name)s.edit', page_name)]

    page_name = ugettext('List of your roles')
    patterns += [(r'^%(url_name)s/(?P<access_type>roles)$',
                   'soc.views.models.user_self.roles', page_name)]

    page_name = ugettext('List of your requests')
    patterns += [(r'^%(url_name)s/(?P<access_type>requests)$',
                   'soc.views.models.user_self.requests', page_name)]

    new_params['django_patterns_defaults'] = patterns

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def editProfile(self, request, access_type,
           page_name=None, params=None, **kwargs):
    """Displays User profile edit page for the current user.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity
    """

    # set the link_id to the current user's link_id
    user_entity = user_logic.getCurrentUser()
    # pylint: disable=E1103
    link_id = user_entity.link_id

    return self.edit(request, access_type, page_name=page_name,
        params=params, link_id=link_id, **kwargs)

  def editGet(self, request, entity, context, params=None):
    """Overwrite so we can add the contents of the ToS.
    For params see base.View.editGet().
    """

    site_tos = site_logic.getToS(site_logic.getSingleton())
    if site_tos:
      context['tos_contents'] = site_tos.content

    return super(View, self).editGet(request, entity, context, params=params)

  def _editGet(self, request, entity, form):
    """Sets the content of the agreed_to_tos_on field and replaces.

    Also replaces the agreed_to_tos field with a hidden field when the ToS has been signed.
    For params see base.View._editGet().
    """

    if entity.agreed_to_tos:
      form.fields['agreed_to_tos_on'].initial = entity.agreed_to_tos_on
      # replace the 'agreed_to_tos' field with a hidden field so
      # that the form checks still pass
      form.fields['agreed_to_tos'] = forms.fields.BooleanField(
          widget=forms.HiddenInput, initial=entity.agreed_to_tos, required=True)

  @decorators.mutation
  def editPost(self, request, entity, context, params=None):
    """Overwrite so we can add the contents of the ToS.
    For params see base.View.editPost().
    """

    site_tos = site_logic.getToS(site_logic.getSingleton())
    if site_tos:
      context['tos_contents'] = site_tos.content

    return super(View, self).editPost(request, entity, context, params=params)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      # fill in the account field with the current User
      account = users.User()
      fields['account'] = account
      fields['user_id'] = account.user_id()
    else:
      fields['account'] = entity.account
      fields['user_id'] = entity.user_id

    # special actions if there is no ToS present
    site_tos = site_logic.getToS(site_logic.getSingleton())
    if not site_tos:
      # there is no Terms of Service set
      if not entity:
        # we are a new user so set the agrees_to_tos field to None
        fields['agreed_to_tos'] = None
      else:
        # editing an existing user so no value changes allowed
        fields['agreed_to_tos'] = entity.agreed_to_tos
    else:
      if not entity or not entity.agreed_to_tos:
        # set the time of agreement
        fields['agreed_to_tos_on'] = datetime.datetime.now()

    super(View, self)._editPost(request, entity, fields)

  def getRolesListData(self, request, lists_params):
    """Returns the list data for roles.
    """

    user = user_logic.getCurrentUser()

    # only select the roles for the current user
    # pylint: disable=E1103
    fields = {
        'link_id': user.link_id,
        'status': ['active', 'inactive']
        }

    idx = lists.getListIndex(request)

    if not 0 <= idx < len(lists_params):
      return lists.getErrorResponse(request, 'idx not valid')

    list_params = lists_params[idx]

    if list_params is None:
      return lists.getErrorResponse(
          request, 'idx not valid (list not in roles overview)')

    contents = helper.lists.getListData(request, list_params, fields)

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def roles(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Displays the valid roles for this user.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used
    """

    lists_params = []

    for _, loop_view in sorted(role_view.ROLE_VIEWS.iteritems()):
      list_params = loop_view.getParams()

      if not list_params['show_in_roles_overview']:
        # filler for easy indexing
        lists_params.append(None)
        continue

      list_params = list_params.copy()
      list_params['public_field_keys'] = list_params['public_field_keys'] + ['status']
      list_params['public_field_names'] = list_params['public_field_names'] + ['Status']
      list_params['list_description'] = self.DEF_ROLE_LIST_MSG_FMT % list_params
      field_props = list_params.setdefault('public_field_props', {})
      field_props['status'] = {
          'searchoptions': {'defaultValue': 'Active'},
          'stype': 'select',
          'editoptions': {'value': ':All;^active$:Active;^inactive$:Inactive'},
      }

      lists_params.append(list_params)

    if lists.isDataRequest(request):
      return self.getRolesListData(request, lists_params)

    contents = []

    for i, list_params in enumerate(lists_params):
      if list_params is None:
        continue

      if not self.getRolesListData(lists.IsNonEmptyRequest(i), lists_params):
        continue

      list = lists.getListGenerator(request, list_params, idx=i)
      contents.append(list)

    params = params.copy()

    if not contents:
      site_name = site_logic.getSingleton().site_name
      params['list_msg'] = self.DEF_NO_ROLES_MSG_FMT % site_name

    return self._list(request, params, contents, page_name)

  def getRequestsListData(self, request, uh_params, ar_params):
    """Returns the list data for getRequestsList.
    """

    idx = lists.getListIndex(request)

    # get the current user
    user_entity = user_logic.getCurrentUser()

    # only select the Invites for this user that haven't been handled yet
    # pylint: disable=E1103
    filter = {'user': user_entity}

    if idx == 0:
      filter['status'] = 'group_accepted'
      params = uh_params
    elif idx == 1:
      filter['status'] = 'new'
      params = ar_params
    else:
      return lists.getErrorResponse(request, "idx not valid")

    contents = helper.lists.getListData(request, params, filter,
                                        visibility='public')

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def requests(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Displays the unhandled requests for this user.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used
    """

    from soc.views.models.request import view as request_view

    req_params = request_view.getParams()

    # construct the Unhandled Invites list
    uh_params = req_params.copy()
    uh_params['public_row_extra'] = lambda entity: {
        "link": redirects.getInviteProcessRedirect(entity, None),
    }
    uh_params['list_description'] = ugettext(
        "An overview of your unhandled invites.")

    # construct the Open Requests list

    ar_params = req_params.copy()
    ar_params['public_row_action'] = {}
    ar_params['public_row_extra'] = lambda x: {}
    ar_params['list_description'] = ugettext(
        "List of your pending requests.")

    if lists.isDataRequest(request):
      return self.getRequestsListData(request, uh_params, ar_params)

    uh_list = helper.lists.getListGenerator(request, uh_params,
                                            visibility='public', idx=0)
    ar_list = helper.lists.getListGenerator(request, ar_params,
                                            visibility='public', idx=1)

    # fill contents with all the needed lists
    contents = [uh_list, ar_list]

    # call the _list method from base to display the list
    return self._list(request, req_params, contents, page_name)

  def getSidebarMenus(self, id, user, params=None):
    """See base.View.getSidebarMenus().
    """

    link_title = ugettext('Notifications')

    filter = {
        'scope': user,
        'unread': True,
        }

    notifications = model_logic.notification.logic.getForFields(filter)
    count = len(list(notifications))

    if count > 0:
      link_title = '<span class="unread">%s (%d)</span>' % (
          force_unicode(link_title), count)
      link_title = mark_safe(link_title)

    items = [('/' + 'notification/list', link_title, 'notification')]
    if user:
      items += [(redirects.getCreateDocumentRedirect(user, 'user'),
          "Create a New Document", 'any_access')]

      items += [(redirects.getListDocumentsRedirect(user, 'user'),
          "List Documents", 'any_access')]

    new_params = {}
    new_params['sidebar_additional'] = items

    params = dicts.merge(params, new_params)

    return super(View, self).getSidebarMenus(id, user, params=params)


view = View()

create = decorators.view(view.create)
edit = decorators.view(view.editProfile)
export = decorators.view(view.export)
requests = decorators.view(view.requests)
roles = decorators.view(view.roles)
