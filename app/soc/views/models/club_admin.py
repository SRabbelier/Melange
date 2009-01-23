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

"""Views for Club Admins.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]


from django import http
from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import club as club_logic
from soc.logic.models import user as user_logic
from soc.logic.models import request as request_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models import club as club_view
from soc.views.models import request as request_view

import soc.logic.models.club_admin


class View(base.View):
  """View methods for the Club Admin model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['create'] = [access.checkIsHost]
    rights['edit'] = [access.checkIsMyActiveRole(soc.logic.models.club_admin)]
    rights['delete'] = [access.checkIsHost]
    rights['invite'] = [access.checkIsClubAdminForClub]
    rights['accept_invite'] = [access.checkCanCreateFromRequest('club_admin')]

    new_params = {}
    new_params['logic'] = soc.logic.models.club_admin.logic
    new_params['rights'] = rights

    new_params['scope_view'] = club_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['name'] = "Club Admin"

    new_params['extra_dynaexclude'] = ['user', 'state']

    new_params['create_extra_dynafields'] = {
       'scope_path': forms.CharField(widget=forms.HiddenInput,
                                  required=True),
       'clean_link_id' : cleaning.clean_existing_user('link_id'),
       'clean_home_page' : cleaning.clean_url('home_page'),
       'clean_blog' : cleaning.clean_url('blog'),
       'clean_photo_url' : cleaning.clean_url('photo_url')}

    patterns = [(r'^%(url_name)s/(?P<access_type>invite)/%(lnp)s$',
        'soc.views.models.%(module_name)s.invite',
        'Create invite for %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>accept_invite)/%(scope)s/%(lnp)s$',
        'soc.views.models.%(module_name)s.acceptInvite',
        'Accept invite for %(name_plural)s')]

    new_params['extra_django_patterns'] = patterns
    
    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create and store the special form for invited users
    updated_fields = {
        'link_id': forms.CharField(widget=widgets.ReadOnlyInput(),
            required=False)}

    invited_create_form = dynaform.extendDynaForm(
        dynaform = self._params['create_form'],
        dynafields = updated_fields)

    params['invited_create_form'] = invited_create_form


  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    fields['user'] = fields['link_id']
    fields['link_id'] = fields['user'].link_id

    super(View, self)._editPost(request, entity, fields)


  @decorators.merge_params
  @decorators.check_access
  def acceptInvite(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """Creates the page process an invite into a Club Admin.

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
    """Handles the GET request concerning the creation of a Club Admin via an
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
    """Handles the POST request concerning the creation of a Club Admin via an
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
    
    # fill in the appropriate fields that were missing in the form
    fields['user'] = fields['link_id']
    fields['link_id'] = fields['user'].link_id

    club = club_logic.logic.getFromKeyName(fields['scope_path'])
    fields['scope'] = club
    
    # make sure that this role becomes active once more in case this user
    # has been reinvited
    fields ['state'] = 'active'
    
    # get the key_name for the new entity
    key_fields =  self._logic.getKeyFieldsFromDict(fields)
    key_name = self._logic.getKeyNameForFields(key_fields)

    # create new Club Admin entity
    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    # redirect to the roles overview page
    return http.HttpResponseRedirect('/user/roles')


  @decorators.merge_params
  @decorators.check_access
  def invite(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """Creates the page upon which a Club Admin can invite another Club Admin.

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
    for becoming a Club Admin.

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
    for becoming a Club Admin.

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
    
    # get the club entity for which this request is for from link_id in kwargs
    club = club_logic.logic.getForFields({'link_id' : kwargs['link_id']}, unique=True)
    
    # create the fields for the new request entity
    request_fields = {'link_id' : form_fields['link_id'].link_id,
        'scope' : club,
        'scope_path' : club.link_id,
        'role' : params['module_name'],
        'role_verbose' : params['name'],
        'state' : 'group_accepted'}

    # extract the key_name for the new request entity
    key_fields = request_logic.logic.getKeyFieldsFromDict(request_fields)
    key_name = request_logic.logic.getKeyNameForFields(key_fields)

    # create the request entity
    entity = request_logic.logic.updateOrCreateFromKeyName(request_fields, key_name)
    
    # TODO(ljvderijk) redirect to a more useful place like the club homepage
    return http.HttpResponseRedirect('/')


view = View()

acceptInvite = view.acceptInvite
create = view.create
delete = view.delete
edit = view.edit
invite = view.invite
list = view.list
public = view.public
export = view.export

