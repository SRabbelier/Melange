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

"""Views for Groups.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views.helper import decorators
from soc.views.helper import lists as list_helper
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import presence
from soc.views.models import document as document_view
from soc.views.models.request import view as request_view
from soc.views.sitemap import sidebar

import soc.views.helper

class View(presence.View):
  """View methods for the Group model.
  """


  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}

    new_params['extra_dynaexclude'] = ['founder', 'home', 'tos',
                                       'member_template', 'status']
    new_params['edit_extra_dynaproperties'] = {
        'founded_by': forms.CharField(widget=widgets.ReadOnlyInput(),
                                   required=False),
        }

    #set the extra_django_patterns and include the one from params
    patterns = params.get('extra_django_patterns', [])

    patterns += [
        (r'^%(url_name)s/(?P<access_type>list_requests)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.list_requests',
        'List of requests for %(name)s'),
        (r'^%(url_name)s/(?P<access_type>list_roles)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.list_roles',
        'List of roles for %(name)s')]

    if params.get('group_applicant_url'):
      # add the applicant pattern
      patterns += [
          (r'^%(url_name)s/(?P<access_type>applicant)/%(key_fields)s$',
          'soc.views.models.%(module_name)s.applicant', 
          "%(name)s Creation via Accepted Application"),]

    new_params['extra_django_patterns'] = patterns

    # TODO(tlarsen): Add support for Django style template lookup
    new_params['public_template'] = 'soc/group/public.html'

    new_params['list_row'] = 'soc/group/list/row.html'
    new_params['list_heading'] = 'soc/group/list/heading.html'

    new_params['create_extra_dynaproperties'] = {
       'clean_phone': cleaning.clean_phone_number('phone'),
       'clean_contact_street': cleaning.clean_ascii_only('contact_street'),
       'clean_contact_city': cleaning.clean_ascii_only('contact_city'),
       'clean_contact_state': cleaning.clean_ascii_only('contact_state'),
       'clean_contact_postalcode': cleaning.clean_ascii_only(
          'contact_postalcode'),
       'clean_shipping_street': cleaning.clean_ascii_only('shipping_street'),
       'clean_shipping_city': cleaning.clean_ascii_only('shipping_city'),
       'clean_shipping_state': cleaning.clean_ascii_only('shipping_state'),
       'clean_shipping_postalcode': cleaning.clean_ascii_only(
          'shipping_postalcode'),
       }


    new_params['role_views'] = {}

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the founded_by with data from the entity
    form.fields['founded_by'].initial = entity.founder.name
    super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      # only if we are creating a new entity we should fill in founder
      user = user_logic.logic.getForCurrentAccount()
      fields['founder'] = user

    super(View, self)._editPost(request, entity, fields)


  @decorators.merge_params
  @decorators.check_access
  def applicant(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Handles the creation of a group via an approved group application.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.applicantPost(request, context, params, **kwargs)
    else:
      # request.method == 'GET'
      return self.applicantGet(request, context, params, **kwargs)

  def applicantGet(self, request, context, params, **kwargs):
    """Handles the GET request concerning the creation of a group via an
    approved group application.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # find the application
    application_logic = params['application_logic']
    application = application_logic.logic.getFromKeyFields(kwargs)

    # extract the application fields
    field_names = application.properties().keys()
    fields = dict( [(i, getattr(application, i)) for i in field_names] )

    # create the form using the fields from the application as the initial value
    form = params['applicant_create_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

  def applicantPost(self, request, context, params, **kwargs):
    """Handles the POST request concerning the creation of a group via an
    approved group application.

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

    # do post processing
    self._applicantPost(request, context, fields)

    if not key_name:
      key_name = self._logic.getKeyNameFromFields(fields)

    # create the group entity
    self._logic.updateOrCreateFromKeyName(fields, key_name)

    # redirect to notifications list to see the admin invite
    return http.HttpResponseRedirect('/notification/list')

  def _applicantPost(self, request, context, fields):
    """Performs any required processing on the entity to post its edit page.

    Args:
      request: the django request object
      context: the context for the webpage
      fields: the new field values
    """

     # fill in the founder of the group
    user = user_logic.logic.getForCurrentAccount()
    fields['founder'] = user

    # If scope_logic is not defined, this entity has no scope
    if not self._params['scope_logic']:
      return

    # If this entity is unscoped, do not try to retrieve a scope
    if 'scope_path' not in fields:
      return

    scope = self._params['scope_logic'].logic.getFromKeyName(
        fields['scope_path'])
    fields['scope'] = scope


  @decorators.merge_params
  @decorators.check_access
  def listRequests(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """Gives an overview of all the requests for a specific group.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # set the pagename to include the link_id
    page_name = '%s %s' % (page_name, kwargs['link_id'])

    # get the group from the request
    group_logic = params['logic']

    group_entity = group_logic.getFromKeyFields(kwargs)

    role_names = params['role_views'].keys()
    
    # list all incoming requests
    filter = {
        'scope': group_entity,
        'role': role_names,
        'status': 'new'
        }

    # create the list parameters
    inc_req_params = request_view.getParams()

    # define the list redirect action to the request processing page
    inc_req_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    inc_req_params['list_description'] = ugettext(
        "An overview of the %(name)s's incoming requests." % params)
    
    inc_req_content = list_helper.getListContent(
        request, inc_req_params, filter, idx=0)

    # list all outstanding invites
    filter = {
        'scope': group_entity,
        'role': role_names,
        'status': 'group_accepted'
        }

    # create the list parameters
    out_inv_params = request_view.getParams()

    # define the list redirect action to the request processing page
    out_inv_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    out_inv_params['list_description'] = ugettext(
        "An overview of the %(name)s's outstanding invites." % params)

    out_inv_content = list_helper.getListContent(
        request, out_inv_params, filter, idx=1)

    # list all ignored requests
    filter = {
        'scope': group_entity,
        'role': role_names,
        'status': 'ignored'
        }

    # create the list parameters
    ignored_params = request_view.getParams()

    # define the list redirect action to the request processing page
    ignored_params['list_action'] = (redirects.getProcessRequestRedirect, None)
    ignored_params['list_description'] = ugettext(
        "An overview of the %(name)s's ignored requests." % params)
    
    ignored_content = list_helper.getListContent(
        request, ignored_params, filter, idx=2)

    contents = [inc_req_content, out_inv_content, ignored_content]

    return self._list(request, params, contents, page_name)


  @decorators.merge_params
  @decorators.check_access
  def listRoles(self, request, access_type,
                page_name=None, params=None, **kwargs):
    """Gives an overview of all the roles in a specific group.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # set the pagename to include the link_id
    page_name = '%s %s' % (page_name, kwargs['link_id'])

    # get the group from the request
    group_logic = params['logic']

    group_entity = group_logic.getFromKeyFields(kwargs)

    # create the filter
    filter = {
        'scope' : group_entity,
        'status': 'active'
        }

    role_views = params['role_views']
    contents = []
    index = 0

    # for each role we create a separate list
    for role_name in role_views.keys():
      # create the list parameters
      list_params = role_views[role_name].getParams().copy()

      list_params['list_action'] = (redirects.getManageRedirect, list_params)
      list_params['list_description'] = ugettext(
          "An overview of the %s for this %s." % (
          list_params['name_plural'], params['name']))
    
      new_list_content = list_helper.getListContent(
          request, list_params, filter, idx=index)

      contents += [new_list_content]

      index += 1

    # call the _list method from base.View to show the list
    return self._list(request, params, contents, page_name)

  def registerRole(self, role_name, role_view):
    """Adds a role to the role_views param.
    
    Args:
      role_name: The name of the role that needs to be added
      role_view: The view that needs to be added to role_views.
    """

    role_views = self._params['role_views']
    role_views[role_name] = role_view

  def getExtraMenus(self, id, user, params=None):
    """Returns the extra menu's for this view.

    A menu item is generated for each group that the user has an active
    role for. The public page for each group is added as menu item,
    as well as all public documents for that group.

    Args:
      params: a dict with params for this View.
    """

    params = dicts.merge(params, self._params)

    # set fields to match every active role this user has
    fields = {'user': user,
              'status': 'active'}

    # get the role views and start filling group_entities
    role_views = self._params['role_views']
    role_descriptions = {}

    for role_name in role_views.keys():
      role_view = role_views[role_name]
      role_view_params = role_view.getParams()
      role_logic = role_view_params['logic']

      roles = role_logic.getForFields(fields)

      for role in roles:
        group_key_name = role.scope.key().name()
        existing_role_descriptions = role_descriptions.get(group_key_name)

        if existing_role_descriptions:
          # add this description to existing roles
          existing_roles = existing_role_descriptions['roles']
          existing_roles[role_name] = role
        else:
          # create a description of this role
          role_description = {'roles': {role_name: role},
              'group': role.scope}

          # add the new entry to our dictionary
          role_descriptions[group_key_name] = role_description

    # get the document view params to add the group's documents to the menu
    doc_params = document_view.view.getParams()

    menus = []

    # for each role description in our collection
    for role_description in role_descriptions.itervalues():
      #start with an empty menu
      menu = {}

      # get the group for this role description
      group_entity = role_description['group']

      # set the menu header name
      menu['heading'] = group_entity.short_name

      # get the documents for this group entity
      doc_items = document_view.view.getMenusForScope(group_entity, params)
      doc_items = sidebar.getSidebarMenu(id, user, doc_items,
                                         params=doc_params)

      # get the group specific items
      group_items = self._getExtraMenuItems(role_description, params)
      group_items = sidebar.getSidebarMenu(id, user, group_items,
                                           params=self._params)

      # add the items together
      menu['items'] = doc_items + group_items
      menu['group'] = params['name_plural']

      # append this as a new menu
      menus.append(menu)

    return menus

  def _getExtraMenuItems(self, role_description, params=None):
    """Used to implement group instance specific needs for the side menu.

    Args:
      role_description : dict containing all the roles which is a dict of 
                         name and the role entity to which it belongs. Also
                         group contains the group entity to which these roles
                         belong.
      params: a dict with params for this View.
    """
    return []
