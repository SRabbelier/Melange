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

"""Views for Role profiles.
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
from soc.logic.models import request as request_logic
from soc.logic.models import user as user_logic
from soc.logic.helper import notifications as notifications_helper
from soc.logic.helper import request as request_helper
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import base
from soc.views.models import request as request_view

import soc.models.request
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.helper.widgets


class View(base.View):
  """Views for all entities that inherit from Role.

  All views that only Role entities have are defined in this subclass.
  """

  DEF_INVITE_INSTRUCTION_MSG_FMT = ugettext(
      'Please use this form to invite someone to become a %(name)s.')

  DEF_REQUEST_INSTRUCTION_MSG_FMT = ugettext(
      'Please use this form to request to become a %(name)s')

  DEF_INVITE_ERROR_MSG_FMT = ugettext(
      'This user can not receive an invite to become a %(name)s. <br/>'
      'Please make sure there is no outstanding invite or request and '
      'be sure that this user is not a %(name)s.')

  DEF_REQUEST_ERROR_MSG_FMT = ugettext(
      'You can not request to become a %(name)s. <br/>'
      'Please make sure there is no outstanding invite or request and '
      'be sure that you are not a %(name)s already.')


  def __init__(self, params=None):
    """

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
          'soc.views.models.%(module_name)s.invite',
          'Create invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>accept_invite)/%(scope)s/%(lnp)s$',
          'soc.views.models.%(module_name)s.accept_invite',
          'Accept invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>process_request)/%(scope)s/%(lnp)s$',
          'soc.views.models.%(module_name)s.process_request',
          'Process request for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>request)/%(scope)s$',
          'soc.views.models.%(module_name)s.request',
          'Create a Request to become %(name)s')]
    elif params.get('allow_invites'):
      # add patterns concerning only invites
      patterns += [(r'^%(url_name)s/(?P<access_type>invite)/%(scope)s$',
          'soc.views.models.%(module_name)s.invite',
          'Create invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>accept_invite)/%(scope)s/%(lnp)s$',
          'soc.views.models.%(module_name)s.accept_invite',
          'Accept invite for %(name)s'),
          (r'^%(url_name)s/(?P<access_type>process_request)/%(scope)s/%(lnp)s$',
          'soc.views.models.%(module_name)s.process_request',
          'Process request for %(name)s')]

    # add manage pattern
    patterns += [(r'^%(url_name)s/(?P<access_type>manage)/%(scope)s/%(lnp)s$',
        'soc.views.models.%(module_name)s.manage',
        'Manage a %(name)s'),]

    new_params['extra_django_patterns'] = patterns
    new_params['scope_redirect'] = redirects.getInviteRedirect
    new_params['create_template'] = 'soc/role/edit.html'
    new_params['edit_template'] = 'soc/role/edit.html'

    new_params['create_extra_dynafields'] = {
       'latitude':forms.fields.FloatField(widget=forms.HiddenInput,
          required=False),
       'longitude': forms.fields.FloatField(widget=forms.HiddenInput,
          required=False),
       'clean_link_id': cleaning.clean_existing_user('link_id'),
       'clean_home_page': cleaning.clean_url('home_page'),
       'clean_blog': cleaning.clean_url('blog'),
       'clean_photo_url': cleaning.clean_url('photo_url'),
       'scope_path': forms.CharField(widget=forms.HiddenInput,
                                  required=True),
       }

    new_params['extra_dynaexclude'] = ['user', 'status', 'agreed_to_tos_on']

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    # add manage template
    params['manage_template'] = 'soc/%(module_name)s/manage.html' % params

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
    context['page_name'] = page_name
    context['instruction_message'] = (self.DEF_INVITE_INSTRUCTION_MSG_FMT %
        params)

    if request.method == 'POST':
      return self.invitePost(request, context, params, **kwargs)
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

    # set the role to the right name
    fields = {'role': '%(module_name)s' % (params)}

    # get the request view parameters and initialize the create form
    request_params = request_view.view.getParams()
    form = request_params['invite_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=request_params)

  def invitePost(self, request, context, params, **kwargs):
    """Handles the POST request concerning the view that creates an invite
    for attaining a certain Role.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the request view parameters and populate the form using POST data
    request_params = request_view.view.getParams()
    form = request_params['invite_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, form_fields = soc.views.helper.forms.collectCleanedFields(form)

    # get the group entity for which this request is via the scope_path
    group = self._logic.getGroupEntityFromScopePath(params['group_logic'],
         kwargs['scope_path'])

    # get the request scope path
    request_scope_path = self._getRequestScopePathFromGroup(group)

    # create the fields for the new request entity
    request_fields = {'link_id': form_fields['link_id'].link_id,
        'scope': group,
        'scope_path': request_scope_path,
        'role': params['module_name'],
        'role_verbose': params['name'],
        'status': 'group_accepted'}

    if not self._isValidNewRequest(request_fields, params):
      # not a valid invite
      context['error_message'] = self.DEF_INVITE_ERROR_MSG_FMT % (
          params)
      return self.inviteGet(request, context, params, **kwargs)

    # extract the key_name for the new request entity
    key_fields = request_logic.logic.getKeyFieldsFromFields(request_fields)
    key_name = request_logic.logic.getKeyNameFromFields(key_fields)

    # create the request entity
    entity = request_logic.logic.updateOrCreateFromKeyName(request_fields, 
        key_name)

    # send out an invite notification
    notifications_helper.sendInviteNotification(entity)

    group_view = params.get('group_view')
    if not group_view:
      return http.HttpResponseRedirect('/')
    else:
      # redirect to the requests list
      return http.HttpResponseRedirect(
          redirects.getListRequestsRedirect(group, group_view.getParams()))

  def _getRequestScopePathFromGroup(self, group_entity):
    """Returns the scope_path that should be put in a request for a given group.

    Args:
      group_entity: The group entity for which the request scope_path should
                    be returned.
    """

    if group_entity.scope_path:
      request_scope_path = '%s/%s' % (
          group_entity.scope_path, group_entity.link_id)
    else:
      request_scope_path = group_entity.link_id

    return request_scope_path


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
      kwargs: the Key Fields for the specified entity
    """

     # get the context for this webpage
    context = responses.getUniversalContext(request)
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.acceptInvitePost(request, context, params, **kwargs)
    else:
      # request.method == 'GET'
      return self.acceptInviteGet(request, context, params, **kwargs)

  def acceptInviteGet(self, request, context, params, **kwargs):
    """Handles the GET request concerning the creation of a Role via an
    invite.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # create the form using the scope_path and link_id from kwargs 
    # as initial value
    fields = {'link_id': kwargs['link_id'],
              'scope_path': kwargs['scope_path']}
    form = params['invited_create_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

  def acceptInvitePost(self, request, context, params, **kwargs):
    """Handles the POST request concerning the creation of a Role via an
    invite.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # populate the form using the POST data
    form = params['invited_create_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, fields = soc.views.helper.forms.collectCleanedFields(form)

    # call the post process method
    self._acceptInvitePost(fields, request, context, params, **kwargs)

    group_logic = params['group_logic']
    group_entity = group_logic.getFromKeyName(fields['scope_path'])
    fields['scope'] = group_entity

    # make sure that this role becomes active once more in case this user
    # has been reinvited
    fields ['status'] = 'active'

    # get the key_name for the new entity
    key_fields =  self._logic.getKeyFieldsFromFields(fields)
    key_name = self._logic.getKeyNameFromFields(key_fields)

    # create new Role entity
    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # mark the request as completed
    request_helper.completeRequestForRole(entity, params['module_name'])

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
    context['page_name'] = page_name

    logic = params['logic']

    # get the entity for the given fields in kwargs
    fields = {'scope_path': kwargs['scope_path'],
        'link_id': kwargs['link_id']}
    role_entity = logic.getForFields(kwargs, unique=True)

    # get the redirect for the cancel button or when the resignation is done
    redirect = redirects.getListRolesRedirect(role_entity.scope, 
        params['group_view'].getParams())

    # check to see if resign is true
    get_dict = request.GET
    resign = get_dict.get('resign')

    if resign == 'true':
      # change the status of this role_entity to invalid
      fields = {'status': 'invalid'}
      logic.updateEntityProperties(role_entity, fields)

      # redirect to the roles listing
      return http.HttpResponseRedirect(redirect)

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
    context['page_name'] = page_name
    context['instruction_message'] = (self.DEF_REQUEST_INSTRUCTION_MSG_FMT %
        params)

    if request.method == 'POST':
      return self.requestPost(request, context, params, **kwargs)
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

    # set right fields for the request form
    user_entity = user_logic.logic.getForCurrentAccount()
    fields = {'link_id' : user_entity.link_id,
              'role' : params['module_name'],
              'group_id' : kwargs['scope_path']}

    # get the request view parameters and initialize the create form
    request_params = request_view.view.getParams()
    form = request_params['request_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=request_params)

  def requestPost(self, request, context, params, **kwargs):
    """Handles the POST request concerning the creation of a request
    to attain a role.

    Args:
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # get the request view parameters and populate the form using POST data
    request_params = request_view.view.getParams()
    form = request_params['invite_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # get the group entity for which this request is via the scope_path
    group = self._logic.getGroupEntityFromScopePath(params['group_logic'],
         kwargs['scope_path'])

    # get the request scope path
    request_scope_path = self._getRequestScopePathFromGroup(group)

    # defensively set the fields we need for this request and set status to new
    user_entity = user_logic.logic.getForCurrentAccount()
    request_fields = {'link_id' : user_entity.link_id,
        'scope' : group,
        'scope_path' : request_scope_path,
        'role' : params['module_name'],
        'role_verbose' : params['name'],
        'status' : 'new'}

    if not self._isValidNewRequest(request_fields, params):
      # not a valid request
      context['error_message'] = self.DEF_REQUEST_ERROR_MSG_FMT % (
          params)
      return self.requestGet(request, context, params, **kwargs)

    # extract the key_name for the new request entity
    key_fields = request_logic.logic.getKeyFieldsFromFields(request_fields)
    key_name = request_logic.logic.getKeyNameFromFields(key_fields)

    # create the request entity
    entity = request_logic.logic.updateOrCreateFromKeyName(request_fields, key_name)

    # TODO(ljvderijk) send out a message to alert the users able to process this request

    # redirect to roles overview
    return http.HttpResponseRedirect('/user/roles')


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

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    context['page_name'] = page_name

    # get the request entity using the information from kwargs
    fields = {'link_id': kwargs['link_id'],
        'scope_path': kwargs['scope_path'],
        'role': params['module_name']}
    request_entity = request_logic.logic.getForFields(fields, unique=True)
    
    get_dict = request.GET
    
    if 'status' in get_dict.keys():
      if get_dict['status'] in ['group_accepted', 'rejected', 'ignored']:
        # update the request_entity and redirect away from this page
        request_status = get_dict['status']
        request_logic.logic.updateEntityProperties(request_entity, {
            'status': get_dict['status']})

        if request_status == 'group_accepted':
          notifications_helper.sendInviteNotification(request_entity)

        group_view = params.get('group_view')
        if not group_view:
          return http.HttpResponseRedirect('/')
        else:
          # redirect to the requests list
          return http.HttpResponseRedirect(
              redirects.getListRequestsRedirect(request_entity.scope, 
                  group_view.getParams()))

    # put the entity in the context
    context['entity'] = request_entity
    context['module_name'] = params['module_name']

    #display the request processing page using the appropriate template
    template = request_view.view.getParams()['request_processing_template']

    return responses.respond(request, template, context=context)

  def _isValidNewRequest(self, request_fields, params):
    """Checks if this is a valid Request object to make.

    Args:
    request_fields: dict containing the fields for the new request entity.
    params: parameters for the current view
    """
    fields = request_fields.copy()
    fields['status'] = ['new', 'group_accepted', 'ignored']

    request_entity = request_logic.logic.getForFields(fields, unique=True)
    
    if request_entity:
      # already outstanding request
      return False

    # check if the role already exists
    fields = {'scope': request_fields['scope'],
        'link_id': request_fields['link_id'],
        'status': ['active','inactive'],
        }

    role_entity = params['logic'].getForFields(fields, unique=True)

    if role_entity:
      # already has this role
      return False

    # no oustanding request or a valid role
    return True
