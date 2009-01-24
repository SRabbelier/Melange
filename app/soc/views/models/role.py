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


from django import http
from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic.models import request as request_logic
from soc.logic.models import user as user_logic
from soc.logic.helper import request as request_helper
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.models import base
from soc.views.models import request as request_view
from soc.views.models import user as user_view

import soc.models.request
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.helper.widgets


class View(base.View):
  """Views for all entities that inherit from Role.

  All views that only Role entities have are defined in this subclass.
  """
  
  DEF_INVITE_INSTRUCTION_MSG_FMT = ugettext_lazy(
      'Please use this form to invite someone to become a %(name)s.')

  def __init__(self, params=None):
    """

    Args:
      params: This dictionary should be filled with the parameters
    """

    new_params = {}
    # TODO(ljvderijk) add request and process_request
    patterns = [(r'^%(url_name)s/(?P<access_type>invite)/%(scope)s$',
        'soc.views.models.%(module_name)s.invite',
        'Create invite for %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>accept_invite)/%(scope)s/%(lnp)s$',
        'soc.views.models.%(module_name)s.accept_invite',
        'Accept invite for %(name_plural)s')]

    new_params['extra_django_patterns'] = patterns
    new_params['scope_redirect'] = redirects.getInviteRedirect

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

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
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # set the role to the right name
    fields = {'role' : '%(module_name)s' %(params)}

    # get the request view parameters and initialize the create form
    request_params = request_view.view.getParams()
    form = request_params['create_form'](initial=fields)

    # construct the appropriate response
    return super(View, self)._constructResponse(request, entity=None,
        context=context, form=form, params=params)

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
    form = request_params['create_form'](request.POST)

    if not form.is_valid():
      # return the invalid form response
      return self._constructResponse(request, entity=None, context=context,
          form=form, params=params)

    # collect the cleaned data from the valid form
    key_name, form_fields = soc.views.helper.forms.collectCleanedFields(form)
    
    # get the group entity for which this request is via the scope_path
    group_key_fields = kwargs['scope_path'].rsplit('/',1)
    
    if len(group_key_fields) == 1:
      # there is only a link_id
      fields = {'link_id' : group_key_fields[0]}
    else:
      # there is a scope_path and link_id
      fields = {'scope_path' : group_key_fields[0],
                'link_id' : group_key_fields[1]}
    
    group = params['group_logic'].getForFields(fields, unique=True)
    
    if group.scope_path:
      request_scope_path = '%s/%s' % [group.scope_path, group.link_id]
    else:
      request_scope_path = group.link_id

    # create the fields for the new request entity
    request_fields = {'link_id' : form_fields['link_id'].link_id,
        'scope' : group,
        'scope_path' : request_scope_path,
        'role' : params['module_name'],
        'role_verbose' : params['name'],
        'state' : 'group_accepted'}

    # extract the key_name for the new request entity
    key_fields = request_logic.logic.getKeyFieldsFromDict(request_fields)
    key_name = request_logic.logic.getKeyNameForFields(key_fields)

    # create the request entity
    entity = request_logic.logic.updateOrCreateFromKeyName(request_fields, key_name)
    
    # TODO(ljvderijk) redirect to a more useful place like the group homepage
    return http.HttpResponseRedirect('/')


  @decorators.merge_params
  @decorators.check_access
  def acceptInvite(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """Creates the page process an invite into a Role.

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

    # create the form using the scope_path and link_id from kwargs as initial value
    fields = {'link_id' : kwargs['link_id'],
              'scope_path' : kwargs['scope_path']}
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
    fields ['state'] = 'active'

    # get the key_name for the new entity
    key_fields =  self._logic.getKeyFieldsFromDict(fields)
    key_name = self._logic.getKeyNameForFields(key_fields)

    # create new Role entity
    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # mark the request as completed
    request_helper.completeRequestForRole(entity, params['module_name'])

    # redirect to the roles overview page
    return http.HttpResponseRedirect('/user/roles')


  def _acceptInvitePost(self, fields, request, context, params, **kwargs):
    """ Used to post-process data after the fields have been cleaned.

      Args:
      fields : the cleaned fields from the role form
      request: the standard Django HTTP request object
      context: dictionary containing the context for this view
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """
    pass
