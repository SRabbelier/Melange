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

"""Views for Role profiles.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.logic.models.request import logic as request_logic
from soc.logic.models.role import logic as role_logic
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import base
from soc.views.models import request as request_view

import soc.models.request
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.helper.widgets


ROLE_VIEWS = {}


def addRole(view):
  """Adds the specified view to the known role views.
  """

  global ROLE_VIEWS
  params = view.getParams()
  role_logic = params['logic']
  name = role_logic.role_name
  ROLE_VIEWS[name] = view


class View(base.View):
  """Views for all entities that inherit from Role.

  All views that only Role entities have are defined in this subclass.
  """

  DEF_INVITE_INSTRUCTION_MSG_FMT = ugettext(
      'Please use this form to invite someone to become a %s for %s.')

  DEF_REQUEST_INSTRUCTION_MSG_FMT = ugettext(
      'Please use this form to request to become a %s for %s.')

  DEF_INVITE_ERROR_MSG_FMT = ugettext(
      'This user can not receive an invite to become a %(name)s. <br/>'
      'Please make sure there is no outstanding invite or request and '
      'be sure that this user is not a %(name)s.')

  DEF_REQUEST_ERROR_MSG_FMT = ugettext(
      'You can not request to become a %(name)s. <br/>'
      'Please make sure there is no outstanding invite or request and '
      'be sure that you are not a %(name)s already.')


  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Args:
      params: This dictionary should be filled with the parameters
    """

    new_params = {}

    patterns = params.get('extra_django_patterns')

    if not patterns:
      patterns = []

    if params.get('allow_requests_and_invites'):
      # add patterns concerning requests and invites
      patterns += [(r'^%(url_name)s/(?P<access_type>invite)/%(scope)s$',
          '%(module_package)s.%(module_name)s.invite',
          'Create invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>accept_invite)/(?P<id>[0-9]*)$',
          '%(module_package)s.%(module_name)s.accept_invite',
          'Accept invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>process_request)/(?P<id>[0-9]*)$',
          '%(module_package)s.%(module_name)s.process_request',
          'Process request'),
          (r'^%(url_name)s/(?P<access_type>request)/%(scope)s$',
          '%(module_package)s.%(module_name)s.role_request',
          'Create a Request to become %(name)s')]
    elif params.get('allow_invites'):
      # add patterns concerning only invites
      patterns += [(r'^%(url_name)s/(?P<access_type>invite)/%(scope)s$',
          '%(module_package)s.%(module_name)s.invite',
          'Create invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>accept_invite)/(?P<id>[0-9]*)$',
          '%(module_package)s.%(module_name)s.accept_invite',
          'Accept invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>process_request)/(?P<id>[0-9]*)$',
          '%(module_package)s.%(module_name)s.process_request',
          'Process request for %(name)s')]

    # add manage pattern
    patterns += [(r'^%(url_name)s/(?P<access_type>manage)/%(scope)s/%(lnp)s$',
        '%(module_package)s.%(module_name)s.manage',
        'Manage a %(name)s'),]

    new_params['extra_django_patterns'] = patterns
    new_params['scope_redirect'] = redirects.getInviteRedirect
    new_params['manage_redirect'] = redirects.getListRolesRedirect

    new_params['create_template'] = 'soc/role/edit.html'
    new_params['edit_template'] = 'soc/role/edit.html'

    new_params['create_extra_dynaproperties'] = {
       'latitude':forms.fields.FloatField(widget=forms.HiddenInput,
                                          required=False),
       'longitude': forms.fields.FloatField(widget=forms.HiddenInput,
                                            required=False),
       'email': forms.fields.EmailField(required=True),
       'clean_link_id': cleaning.clean_existing_user('link_id'),
       'clean_given_name': cleaning.clean_ascii_only('given_name'),
       'clean_surname': cleaning.clean_ascii_only('surname'),
       'clean_phone': cleaning.clean_phone_number('phone'),
       'clean_res_street': cleaning.clean_ascii_only('res_street'),
       'clean_res_city': cleaning.clean_ascii_only('res_city'),
       'clean_res_state': cleaning.clean_ascii_only('res_state'),
       'clean_res_postalcode': cleaning.clean_ascii_only('res_postalcode'),
       'clean_ship_street': cleaning.clean_ascii_only('ship_street'),
       'clean_ship_city': cleaning.clean_ascii_only('ship_city'),
       'clean_ship_state': cleaning.clean_ascii_only('ship_state'),
       'clean_ship_postalcode': cleaning.clean_ascii_only('ship_postalcode'),
       'clean_home_page': cleaning.clean_url('home_page'),
       'clean_blog': cleaning.clean_url('blog'),
       'clean_photo_url': cleaning.clean_url('photo_url'),
       'scope_path': forms.CharField(widget=forms.HiddenInput,
                                  required=True),
       }

    new_params['extra_dynaexclude'] = ['user', 'status', 'agreed_to_tos_on']

    new_params['show_in_roles_overview'] = True

    # define the fields for the admin list
    new_params['admin_field_keys'] = [
        'link_id', 'name', 'document_name', 'email', 'res_street',
        'res_city', 'res_state', 'res_country', 'res_postalcode', 'phone',
        'shipping_street', 'shipping_city', 'shipping_state',
        'shipping_country', 'shipping_postalcode', 'birth_date',
        'tshirt_style', 'tshirt_size', 'group_name', 'status', 'account_name'
        ]
    new_params['admin_field_names'] = [
        'Link ID', 'Name', 'Name on Documents', 'Email', 'Street', 'City',
        'State', 'Country', 'Postal Code', 'Phone Number', 'Shipping Street',
        'Shipping City', 'Shipping State', 'Shipping Country',
        'Shipping Postal Code', 'Birth Date', 'T-Shirt Style', 'T-Shirt Size',
        'Group Name', 'Status', 'Account Name'
    ]
    new_params['admin_field_prefetch'] = ['scope', 'user']
    new_params['admin_field_extra'] = lambda entity: {
        'group_name': entity.scope.name,
        'birth_date': entity.birth_date.isoformat(),
        'account_name': accounts.normalizeAccount(entity.user.account).email()
    }

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    # add manage template
    template = 'soc/%(module_name)s/manage.html' % self._params
    self._params['manage_template'] = template

    # register this View
    addRole(self)

  @decorators.merge_params
  @decorators.check_access
  def invite(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Creates the page on which an invite can be send out.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    group_entity = params['group_logic'].getFromKeyName(kwargs['scope_path'])

    context['instruction_message'] = (self.DEF_INVITE_INSTRUCTION_MSG_FMT %
        (params['name'], group_entity.name))

    if request.method == 'POST':
      return self.invitePost(request, context, params, group_entity, **kwargs)
    else:
      # request.method == 'GET'
      return self.inviteGet(request, context, params, **kwargs)

  def inviteGet(self, request, context, params, **kwargs):
    """Handles the GET request concerning the view that creates an invite
    for attaining a certain Role.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the request view parameters and initialize the invite form
    request_params = request_view.view.getParams()
    form = request_params['invite_form']()

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=request_params)

  def invitePost(self, request, context, params, group_entity, **kwargs):
    """Handles the POST request concerning the view that creates an invite
    for attaining a certain Role.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      group_entity: Group entity which this invite is from
      kwargs: the Key Fields for the specified entity
    """

    # get the request view parameters and populate the form using POST data
    request_params = request_view.view.getParams()
    form = request_params['invite_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=request_params)

    # collect the cleaned data from the valid form
    _, form_fields = soc.views.helper.forms.collectCleanedFields(form)

    # create the fields for the new request entity
    request_fields = {
        'user': form_fields['user_id'],
        'group': group_entity,
        'role': params['logic'].role_name,
        'status': 'group_accepted'}

    if not request_logic.isValidNewRequest(request_fields, params['logic']):
      # not a valid invite
      context['error_message'] = self.DEF_INVITE_ERROR_MSG_FMT % (
          params)
      return super(View, self)._constructResponse(request, entity=None,
          context=context, form=form, params=request_params)

    # create the request entity
    request_logic.updateOrCreateFromFields(request_fields)

    group_view = params.get('group_view')

    if not group_view:
      return http.HttpResponseRedirect('/')
    else:
      # redirect to the requests list
      return http.HttpResponseRedirect(
          redirects.getListRequestsRedirect(group_entity, 
                                            group_view.getParams()))

  @decorators.merge_params
  @decorators.check_access
  def acceptInvite(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """Creates the page process an invite into a Role.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: contains the ID for the Request entity
    """

    request_entity = request_logic.getFromIDOr404(int(kwargs['id']))

     # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.acceptInvitePost(request, context, params, request_entity,
                                   **kwargs)
    else:
      # request.method == 'GET'
      return self.acceptInviteGet(request, context, params, request_entity,
                                  **kwargs)

  def acceptInviteGet(self, request, context, params, request_entity,
                      **kwargs):
    """Handles the GET request concerning the creation of a Role via an
    invite.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      request_entity: Request that is being accepted
      kwargs: contains the ID for the Request entity
    """

    # create the form using the scope_path and link_id from kwargs 
    # as initial value
    fields = {'link_id': request_entity.user.link_id,
              'scope_path': request_entity.group.key().id_or_name()}

    fields.update(role_logic.getSuggestedInitialProperties(
        request_entity.user))

    form = params['invited_create_form'](initial=fields)
    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

  def acceptInvitePost(self, request, context, params, 
                       request_entity, **kwargs):
    """Handles the POST request concerning the creation of a Role via an
    invite.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      request_entity: Request that is being accepted
      kwargs: contains the ID for the Request entity
    """

    # populate the form using the POST data
    form = params['invited_create_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, fields = soc.views.helper.forms.collectCleanedFields(form)

    # set the user and link_id fields to the right property
    fields['user'] = request_entity.user
    fields['link_id'] = request_entity.user.link_id
    fields['scope'] = request_entity.group
    fields['scope_path'] = request_entity.group.key().id_or_name()
    # make sure that this role becomes active once more in case this user
    # has been reinvited
    fields ['status'] = 'active'

    # call the post process method
    self._acceptInvitePost(fields, request, context, params, **kwargs)

    # get the key_name for the new entity
    key_name = self._logic.getKeyNameFromFields(fields)

    # create new Role entity
    _ = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # mark the request as completed
    request_fields = {'status': 'completed'}
    request_logic.updateEntityProperties(request_entity, request_fields)

    # redirect to the roles overview page
    return http.HttpResponseRedirect('/user/roles')

  def _acceptInvitePost(self, fields, request, context, params, **kwargs):
    """Used to post-process data after the fields have been cleaned.

      Args:
      fields : the cleaned fields from the role form
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """
    pass

  @decorators.merge_params
  @decorators.check_access
  def manage(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Handles the request concerning the view that let's 
       you manage a role's status.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    logic = params['logic']

    # get the entity for the given fields in kwargs
    fields = {'scope_path': kwargs['scope_path'],
        'link_id': kwargs['link_id']}
    role_entity = logic.getForFields(kwargs, unique=True)

    # get the redirect for the cancel button or when the resignation is done
    redirect = params['manage_redirect'](role_entity.scope,
        params['group_view'].getParams())

    # check to see if resign is true
    get_dict = request.GET
    resign = get_dict.get('resign')

    if resign == 'true':

      resign_error = params['logic'].canResign(role_entity)

      if not resign_error:
        # change the status of this role_entity to invalid
        fields = {'status': 'invalid'}
        logic.updateEntityProperties(role_entity, fields)

        # redirect to the roles listing
        return http.HttpResponseRedirect(redirect)
      else:
        # show error to the user
        context['resign_error'] = ugettext(resign_error %params)

    # set the appropriate context
    context['entity'] = role_entity
    context['url_name'] = params['url_name']
    context['cancel_redirect'] = redirect

    # get the manage template
    template = params['manage_template']

    # return a proper response
    return responses.respond(request, template, context=context)

  @decorators.merge_params
  @decorators.check_access
  def request(self, request, access_type,
              page_name=None, params=None, **kwargs):
    """Handles the request concerning the view that creates a request
    for attaining a certain Role.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    group_entity = params['group_logic'].getFromKeyName(kwargs['scope_path'])

    context['instruction_message'] = (self.DEF_REQUEST_INSTRUCTION_MSG_FMT %
        (params['name'], group_entity.name))

    if request.method == 'POST':
      return self.requestPost(request, context, params, group_entity, **kwargs)
    else:
      # request.method == 'GET'
      return self.requestGet(request, context, params, **kwargs)

  def requestGet(self, request, context, params, **kwargs):
    """Handles the GET request concerning the creation of a request
    to attain a role.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the request view parameters and initialize the create form
    request_params = request_view.view.getParams()
    form = request_params['request_form']()

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=request_params)

  def requestPost(self, request, context, params, group_entity, **kwargs):
    """Handles the POST request concerning the creation of a request
    to attain a role.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      group_entity: the Group entity this request is for
      kwargs: the Key Fields for the specified entity
    """

    # get the request view parameters and populate the form using POST data
    request_params = request_view.view.getParams()
    form = request_params['request_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=request_params)

    _, fields = soc.views.helper.forms.collectCleanedFields(form)

    # set the fields for the new request
    user_entity = user_logic.logic.getForCurrentAccount()

    request_fields = {
        'user': user_entity,
        'group' : group_entity,
        'message': fields['message'],
        'role' : params['logic'].role_name,
        'status' : 'new'}

    if not request_logic.isValidNewRequest(request_fields, params['logic']):
      # not a valid request
      context['error_message'] = self.DEF_REQUEST_ERROR_MSG_FMT % (
          params)
      return super(View, self)._constructResponse(request, entity=None,
          context=context, form=form, params=request_params)

    # create the request entity
    request_logic.updateOrCreateFromFields(request_fields)

    # redirect to requests overview
    return http.HttpResponseRedirect('/user/requests')

  @decorators.merge_params
  @decorators.check_access
  def processRequest(self, request, access_type,
                     page_name=None, params=None, **kwargs):
    """Creates the page upon which a request can be processed.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the request entity using the information from kwargs
    request_entity = request_logic.getFromIDOr404(int(kwargs['id']))

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])

    context['page_name'] = '%s from %s to become a %s' % (
        page_name, request_entity.user.name, params['name'])

    get_dict = request.GET

    if 'status' in get_dict.keys():
      if get_dict['status'] in ['group_accepted', 'rejected', 'ignored']:
        # update the request_entity and redirect away from this page
        request_status = get_dict['status']

        # only update when the status is changing
        if request_status != request_entity.status:
          request_logic.updateEntityProperties(request_entity, {
              'status': get_dict['status']})

        group_view = params.get('group_view')
        if not group_view:
          return http.HttpResponseRedirect('/')
        else:
          # redirect to the requests list
          return http.HttpResponseRedirect(
              redirects.getListRequestsRedirect(request_entity.group,
                  group_view.getParams()))

    # put the entity in the context
    context['entity'] = request_entity
    context['request_status'] = request_entity.status 
    context['role_verbose'] = params['name']
    context['url_name'] = params['url_name']

    #display the request processing page using the appropriate template
    template = request_view.view.getParams()['request_processing_template']

    return responses.respond(request, template, context=context)
