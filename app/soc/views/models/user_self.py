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
from django import http
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
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models import user as user_view
from soc.views.models import role as role_view

import soc.models.user


class View(base.View):
  """Views for User own profiles.
  """

  DEF_ROLE_LIST_MSG_FMT = ugettext("Your roles as %(name)s.")
  DEF_NO_ROLES_MSG_FMT = ugettext("You don't have any Roles in %s.")

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['unspecified'] = ['deny']
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

    new_params['name'] = "User"
    new_params['module_name'] = "user_self"
    new_params['url_name'] = "user"

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
        'clean_link_id': cleaning.clean_link_id('link_id'),
        'agreed_to_tos_on': forms.DateTimeField(
          widget=widgets.ReadOnlyInput(attrs={'disabled':'true'}),
          required=False),
        }

    new_params['sidebar_heading'] = 'User (self)'
    new_params['sidebar'] = [
        (users.create_login_url("/"), 'Sign In', 'signIn'),
        ('/' + new_params['url_name'] + '/create_profile', 'Create Profile', 'create_profile'),
        ('/' + new_params['url_name'] + '/edit_profile', 'Edit Profile', 'edit_profile'),
        ('/' + new_params['url_name'] + '/roles', 'Roles', 'roles'),
        ('/' + new_params['url_name'] + '/requests', 'Requests', 'requests'),
        ]

    patterns = []

    page_name = ugettext("Create your profile")
    patterns += [(r'^%(url_name)s/(?P<access_type>create_profile)$',
                  'soc.views.models.%(module_name)s.create', page_name)]

    page_name = ugettext("Edit your profile")
    patterns += [(r'^%(url_name)s/(?P<access_type>edit_profile)$',
                  'soc.views.models.%(module_name)s.edit', page_name)]

    page_name = ugettext("List of your roles")
    patterns += [(r'^%(url_name)s/(?P<access_type>roles)$',
                   'soc.views.models.user_self.roles', page_name)]

    page_name = ugettext("List of your requests")
    patterns += [(r'^%(url_name)s/(?P<access_type>requests)$',
                   'soc.views.models.request.list_self', page_name)]

    new_params['django_patterns_defaults'] = patterns

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def editProfile(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """Displays User profile edit page for the current user.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity
    """

    # set the link_id to the current user's link_id
    user_entity = user_logic.getForCurrentAccount()
    link_id = user_entity.link_id

    return self.edit(request, access_type,
         page_name=page_name, params=params, seed=seed, link_id=link_id, **kwargs)

  def editGet(self, request, entity, context, seed, params=None):
    """Overwrite so we can add the contents of the ToS.
    For params see base.View.editGet().
    """

    s_logic = model_logic.site.logic
    site_tos = s_logic.getToS(s_logic.getSingleton())
    if site_tos:
      context['tos_contents'] = site_tos.content

    return super(View, self).editGet(request, entity, context, seed, params=params)

  def _editGet(self, request, entity, form):
    """Sets the content of the agreed_to_tos_on field and replaces.

    Also replaces the agreed_to_tos field with a hidden field when the ToS has been signed.
    For params see base.View._editGet().
    """

    if entity.agreed_to_tos:
      form.fields['agreed_to_tos_on'].initial = entity.agreed_to_tos_on
      # replace the 'agreed_to_tos' field with a hidden field so 
      # that the form checks still pass
      form.fields['agreed_to_tos'] = forms.fields.BooleanField(widget=forms.HiddenInput,
      initial=entity.agreed_to_tos, required=True)

  def editPost(self, request, entity, context, params=None):
    """Overwrite so we can add the contents of the ToS.
    For params see base.View.editPost().
    """

    s_logic = model_logic.site.logic
    site_tos = s_logic.getToS(s_logic.getSingleton())
    if site_tos:
      context['tos_contents'] = site_tos.content

    return super(View, self).editPost(request, entity, context, params=params)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    # fill in the account field with the current User
    fields['account'] = users.User()

    # special actions if there is no ToS present
    s_logic = model_logic.site.logic
    site_tos = s_logic.getToS(s_logic.getSingleton())
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

  @decorators.merge_params
  @decorators.check_access
  def roles(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Displays the unhandled requests for this user.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used
    """

    user = user_logic.getForCurrentAccount()

    # only select the roles for the current user
    filter = {
        'link_id': user.link_id,
        }

    contents = []

    i = 0

    for name, view in sorted(role_view.ROLE_VIEWS.iteritems()):
      list_params = view.getParams().copy()
      list_params['list_action'] = (redirects.getEditRedirect, list_params)
      list_params['list_description'] = self.DEF_ROLE_LIST_MSG_FMT % list_params

      list = helper.lists.getListContent(request, list_params, filter, i, True)

      if list:
        contents.append(list)
        i += 1

    site = site_logic.getSingleton()
    site_name = site.site_name

    params = params.copy()
    params['no_lists_msg'] = self.DEF_NO_ROLES_MSG_FMT % site_name

    return self._list(request, params, contents, page_name)

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
      link_title = '<span class="unread">%s (%d)</span>' % (force_unicode(link_title), count)
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
roles = decorators.view(view.roles)
