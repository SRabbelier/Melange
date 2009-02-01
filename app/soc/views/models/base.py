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

"""Helpers functions for displaying views.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import http
from django.utils import simplejson
from django.utils.translation import ugettext

from soc.logic import dicts
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import forms
from soc.views.helper import redirects
from soc.views import sitemap

import soc.logic
import soc.logic.lists
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.helper.params


class View(object):
  """Views for entity classes.

  The View class functions specific to Entity classes by relying
  on the the child-classes to define the following fields:

  self._logic: the logic singleton for this entity
  """

  DEF_CREATE_NEW_ENTITY_MSG_FMT = ugettext(
      ' You can create a new %(entity_type)s by visiting'
      ' <a href="%(create)s">Create '
      'a New %(entity_type)s</a> page.')

  DEF_CREATE_INSTRUCTION_MSG_FMT = ugettext(
      'Please select a %s for the new %s.')

  def __init__(self, params=None):
    """

    Args:
      params: This dictionary should be filled with the parameters
        specific to this entity. See the methods in this class on
        the fields it should contain, and how they are used.
    """

    self._params = helper.params.constructParams(params)
    self._logic = params['logic']

  @decorators.merge_params
  @decorators.check_access
  def public(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays the public page for the entity specified by **kwargs.

    Params usage:
      rights: The rights dictionary is used to check if the user has
        the required rights to view the public page for this entity.
        See checkAccess for more details on how the rights dictionary
        is used to check access rights.
      error_public: The error_public value is used as template when
        the key values (as defined by the page's url) do not
        correspond to an existing entity.
      name: The name value is used to set the entity_type in the
        context so that the template can refer to it.
      public_template: The public_template value is used as template
        to display the public page of the found entity.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    if not all(kwargs.values()):
      #TODO: Change this into a proper redirect
      return http.HttpResponseRedirect('/')

    try:
      key_fields = self._logic.getKeyFieldsFromFields(kwargs)
      entity = self._logic.getFromKeyFieldsOr404(key_fields)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'], context=context)

    self._public(request, entity, context)

    context['entity'] = entity
    context['entity_type'] = params['name']

    template = params['public_template']

    return helper.responses.respond(request, template, context=context)

  @decorators.merge_params
  @decorators.check_access
  def export(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays the export page for the entity specified by **kwargs.

    Params usage:
      rights: The rights dictionary is used to check if the user has
        the required rights to view the export page for this entity.
        See checkAccess for more details on how the rights dictionary
        is used to check access rights.
      error_export: The error_export value is used as template when
        the key values (as defined by the page's url) do not
        correspond to an existing entity.
      name: The name value is used to set the entity_type in the
        context so that the template can refer to it.
      export_template: The export_template value is used as template
        to display the export page of the found entity.
      export_content_type: The export_content_type value is used to set
        the Content-Type header of the HTTP response.  If empty (or None),
        public() is called instead.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    if not params.get('export_content_type'):
      return self.public(request, access_type, page_name=page_name,
                         params=params, **kwargs)

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    if not all(kwargs.values()):
      #TODO: Change this into a proper redirect
      return http.HttpResponseRedirect('/')

    try:
      key_fields = self._logic.getKeyFieldsFromFields(kwargs)
      entity = self._logic.getFromKeyFieldsOr404(key_fields)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_export'], context=context)

    self._export(request, entity, context)

    context['entity'] = entity
    context['entity_type'] = params['name']

    template = params['export_template']

    response_args = {'mimetype': params['export_content_type']}

    return helper.responses.respond(request, template, context=context,
                                    response_args=response_args)

  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays the create page for this entity type.

    Params usage:
      The params dictionary is passed on to edit, see the docstring
      for edit on how it uses it.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used for create()
    """

    new_params = dicts.merge(params, self._params)

    if ('scope_view' in new_params) and ('scope_path' not in kwargs):
      view = new_params['scope_view'].view
      redirect = new_params['scope_redirect']
      return self.select(request, view, redirect,
                         params=params, page_name=page_name, **kwargs)

    params = new_params

    # Create page is an edit page with no key fields
    empty_kwargs = {}
    fields = self._logic.getKeyFieldNames()
    for field in fields:
      empty_kwargs[field] = None

    return self.edit(request, access_type, page_name=page_name,
                     params=params, seed=kwargs, **empty_kwargs)

  @decorators.merge_params
  @decorators.check_access
  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """Displays the edit page for the entity specified by **kwargs.

    Params usage:
      The params dictionary is passed on to either editGet or editPost
      depending on the method type of the request. See the docstring
      for editGet and editPost on how they use it.

      rights: The rights dictionary is used to check if the user has
        the required rights to edit (or create) a new entity.
        See checkAccess for more details on how the rights dictionary
        is used to check access rights.
      name: The name value is used to construct the message_fmt of the
        raised error when there key_values do not define an existing
        entity. See DEF_CREATE_NEW_ENTITY_MSG_FMT on how the name
        (and the lower() version of it) is used.
      missing_redirect: The missing_redirect value is also used to
        construct the message_fmt mentioned above.
      error_public: The error_public value is used as the template for
        the error response mentioned above.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity
    """

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      if all(kwargs.values()):
        key_fields = self._logic.getKeyFieldsFromFields(kwargs)
        entity = self._logic.getFromKeyFieldsOr404(key_fields)
    except out_of_band.Error, error:
      if not seed:
        error.message_fmt = (
          error.message_fmt + self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
            'entity_type_lower' : params['name'].lower(),
            'entity_type' : params['name'],
            'create' : params['missing_redirect']})
        return helper.responses.errorResponse(
            error, request, template=params['error_public'], context=context)

    if request.method == 'POST':
      return self.editPost(request, entity, context, params=params)
    else:
      return self.editGet(request, entity, context, seed, params=params)

  @decorators.merge_params
  def editPost(self, request, entity, context, params=None):
    """Processes POST requests for the specified entity.

    Params usage:
      The params dictionary is passed to _constructResponse when the
      form is not valid (see edit_form and create_form below). See
      the docstring of _constructResponse on how it uses it.

      edit_form: The edit_form value is used as form when there is an
        existing entity. It is provided with with the request.POST
        dictionary on construction. The collectCleanedFields method
        is called with the newly constructed form. If the form is
        not valid, it is passed as argument to _constructResponse.
      create_form: The create_form value is used in a similar way to
        edit_form, only it is used when there is no existing entity.
      edit_redirect: The edit_redirect value is used as the first part
        of the url if the form was valid. The last part of the url is
        created using the getKeySuffix method of the _logic object.
      edit_params: The edit_params dictionary is used as argument to
        redirectToChangedSuffix, it will be appended to the url in the
        standard ?key=value format.

    Args:
      request: a django request object
      entity: the entity that will be modified or created, may be None
      context: the context dictionary that will be provided to Django
      params: required, a dict with params for this View
    """

    if entity:
      form = params['edit_form'](request.POST)
    else:
      form = params['create_form'](request.POST)

    if not form.is_valid():
      return self._constructResponse(request, entity, context, form, params)

    key_name, fields = forms.collectCleanedFields(form)

    self._editPost(request, entity, fields)

    if not key_name:
      key_fields =  self._logic.getKeyFieldsFromFields(fields)
      key_name = self._logic.getKeyNameFromFields(key_fields)

    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    if not entity:
      return http.HttpResponseRedirect('/')

    page_params = params['edit_params']
    params['suffix'] = self._logic.getKeySuffix(entity)

    request.path = params['edit_redirect'] % params

    # redirect to (possibly new) location of the entity
    # (causes 'Profile saved' message to be displayed)
    return helper.responses.redirectToChangedSuffix(
        request, None, params=page_params)

  @decorators.merge_params
  def editGet(self, request, entity, context, seed, params=None):
    """Processes GET requests for the specified entity.

    Params usage:
      The params dictionary is passed to _constructResponse, see the
      docstring  of _constructResponse on how it uses it.

      save_message: The save_message list is used as argument to
        getSingleIndexedParamValue when an existing entity was saved.
      edit_form: The edit_form is used as form if there is an existing
        entity. The existing entity is passed as instance to it on
        construction. If key_name is part of it's fields it will be
        set to the entity's key().name() value. It is also passed as
        argument to the _editGet method. See the docstring for
        _editGet on how it uses it.
      create_form: The create_form is used as form if there was no
        existing entity. If the seed argument is present, it is passed
        as the 'initial' argument on construction. Otherwise, it is
        called with no arguments.
      submit_msg_param_name: The submit_msg_param_name value is used
        as the key part in the ?key=value construct for the submit
        message parameter (see also save_message).

    Args:
      request: the django request object
      entity: the entity that will be edited, may be None
      context: the context dictionary that will be provided to django
      seed: if no entity is provided, the initial values for the new entity
      params: required, a dict with params for this View
    """

    suffix = self._logic.getKeySuffix(entity)

    # Remove the params from the request, this is relevant only if
    # someone bookmarked a POST page.
    is_self_referrer = helper.requests.isReferrerSelf(request, suffix=suffix)
    if request.GET.get(params['submit_msg_param_name']):
      if (not entity) or (not is_self_referrer):
        return http.HttpResponseRedirect(request.path)

    if entity:
      # Note: no message will be displayed if parameter is not present
      context['notice'] = helper.requests.getSingleIndexedParamValue(
          request, params['submit_msg_param_name'],
          values=params['save_message'])

      # populate form with the existing entity
      form = params['edit_form'](instance=entity)

      if 'key_name' in form.fields:
        form.fields['key_name'].initial = entity.key().name()

      self._editGet(request, entity, form)
    else:
      seed = seed if seed else {}
      self._editSeed(request, seed)

      if seed:
        form = params['create_form'](initial=seed)
      else:
        form = params['create_form']()

    return self._constructResponse(request, entity, context, form, params)

  @decorators.merge_params
  @decorators.check_access
  def list(self, request, access_type,
           page_name=None, params=None, filter=None):
    """Displays the list page for the entity type.
    
    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      filter: a dict for the properties that the entities should have

    Params usage:
      The params dictionary is passed as argument to getListContent in
      the soc.views.helper.list module. See the docstring for getListContent 
      on how it uses it. The params dictionary is also passed as argument to 
      the _list method. See the docstring for _list on how it uses it.
    """

    content = helper.lists.getListContent(request, params, filter)
    contents = [content]

    return self._list(request, params, contents, page_name)

  def _list(self, request, params, contents, page_name):
    """Returns the list page for the specified contents.

    Args:
      request: the standard Django HTTP request object
      params: a dict with params for this View
      contents: a list of content dicts
      page_name: the page name displayed in templates as page and header title

    Params usage:
      name: The name value is used to set the entity_type in the
        context so that the template can refer to it.
      name_plural: The name_plural value is used to set
        the entity_type_plural value in the context so that the
        template can refer to it.
      list_template: The list_template value is used as template for
        to display the list of all entities for this View.
    """

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    context['list'] = soc.logic.lists.Lists(contents)

    context['entity_type'] = params['name']
    context['entity_type_plural'] = params['name_plural']

    template = params['list_template']

    return helper.responses.respond(request, template, context)

  @decorators.merge_params
  @decorators.check_access
  def delete(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Shows the delete page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity

    Params usage:
      rights: The rights dictionary is used to check if the user has
        the required rights to delete the specified entity. See checkAccess 
        for more details on how the rights dictionary is used to check access 
        rights.
      name: used in the same way as in edit(), see it's docstring for
        a more detailed explanation on how it is used.
      missing_redirect: see name
      error_edit: see name
      delete_redirect: The delete_redirect value is used as the url to
        redirect to after having successfully deleted the entity.
    """

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      key_fields = self._logic.getKeyFieldsFromFields(kwargs)
      entity = self._logic.getFromKeyFieldsOr404(key_fields)
    except out_of_band.Error, error:
      error.message_fmt = (
        error.message_fmt + self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
          'entity_type_lower' : params['name'].lower(),
          'entity_type' : params['name'],
          'create' : params['missing_redirect']})
      return helper.responses.errorResponse(
          error, request, template=params['error_edit'], context=context)

    if not entity:
      #TODO: Create a proper error page for this
      return http.HttpResponseRedirect('/')

    if not self._logic.isDeletable(entity):
      # TODO: Update the notice area telling the user that they
      # can't delete the entity
      pass

    self._logic.delete(entity)
    redirect = params['delete_redirect']

    return http.HttpResponseRedirect(redirect)

  def select(self, request, view, redirect,
             page_name=None, params=None, filter=None):
    """Displays a list page allowing the user to select an entity.

    After having selected the Scope, the user is redirected to the
    'create a new entity' page with the scope_path set appropriately.

    Params usage:
      The params dictionary is also passed to getListContent from
        the helper.list module, please refer to its docstring also.
      The params dictionary is passed to self._list as well, refer
        to its docstring for details on how it uses it.

    Args:
      request: the standard Django HTTP request object
      view: the view for which to generate the select page
      redirect: the redirect to use
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      filter: a filter that all displayed entities should satisfy
    """

    params = dicts.merge(params, view.getParams())
    params = dicts.merge(params, self._params)
    params['list_action'] = (redirect, self._params)
    params['list_description'] = self.DEF_CREATE_INSTRUCTION_MSG_FMT % (
        params['name'], self._params['name'])

    content = helper.lists.getListContent(request, params, filter=filter)
    contents = [content]

    return self._list(request, params, contents, page_name)

  @decorators.merge_params
  @decorators.check_access
  def pick(self, request, acces_type, page_name=None, params=None):
    """Displays a list page allowing the user to select an entity.

    After having selected an entity, the user is redirected to the
    return_url as specified in the GET args.

    Params usage:
      The params dictionary is passed to self.select, refer
        to its docstring for details on how it uses it.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
    """

    get_dict = request.GET

    # scope_path is not required
    scope_path = get_dict.get('scope_path', None)
    return_url = get_dict['continue']
    field = get_dict['field']

    filter = {}

    if scope_path:
      filter['scope_path'] = scope_path

    data = self._logic.getForFields(filter=filter, limit=1000)

    data = [i.toDict() for i in data]

    to_json = {
        'data': data,
        'return_url': return_url,
        'field': field,
        }

    json = simplejson.dumps(to_json)

    context = {'json': json}
    template = 'soc/json.html'

    return helper.responses.respond(request, template, context)

  def _editPost(self, request, entity, fields):
    """Performs any required processing on the entity to post its edit page.

    Args:
      request: the django request object
      entity: the entity to create or update from POST contents
      fields: the new field values
    """

    # If scope_logic is not defined, this entity has no scope
    if not self._params['scope_logic']:
      return

    # If this entity is unscoped, do not try to retrieve a scope
    if 'scope_path' not in fields:
      return

    scope = self._params['scope_logic'].logic.getFromKeyName(
        fields['scope_path'])
    fields['scope'] = scope

  def _public(self, request, entity, context):
    """Performs any required processing to get an entity's public page.

    Args:
      request: the django request object
      entity: the entity to make public
      context: the context object
    """
    pass

  def _export(self, request, entity, context):
    """Performs any required processing to get an entity's export page.

    Args:
      request: the django request object
      entity: the entity to export
      context: the context object
    """
    pass

  def _editGet(self, request, entity, form):
    """Performs any required processing on the form to get its edit page.

    Args:
      request: the django request object
      entity: the entity to get
      form: the django form that will be used for the page
    """

    # fill in the email field with the data from the entity
    if 'scope_path' in form.fields:
      form.fields['scope_path'].initial = entity.scope_path

    field = request.GET.get('field', None)
    value = request.GET.get('value', None)

    if field and value and field in form.fields:
      form.fields[field].initial = value


  def _editSeed(self, request, seed):
    """Performs any required processing on the form to get its edit page.

    Args:
      request: the django request object
      seed: the fields to seed the create page with
    """

    field = request.GET.get('field', None)
    value = request.GET.get('value', None)

    if field and value:
      seed[field] = value

  def _constructResponse(self, request, entity, context, form, params):
    """Updates the context and returns a response for the specified arguments.

    Args:
      request: the django request object
      entity: the entity that is used and set in the context
      context: the context to be used
      form: the form that will be used and set in the context
      params: a dict with params for this View

    Params usage:
      name: The name_plural value is used to set the entity_type
       value in the context so that the template can refer to it.
      name_plural: same as name, but used to set entity_type_plural
      name_short: same as name, but used to set entity_type_short
      url_name: same as name, but used to set entity_type_url
      edit_template: The edit_template value is used as template when
        there is an existing entity to display the edit page for the
        specified entity.
      create_template: similar to edit_template, but is used when
        there is no existing entity.
    """

    suffix = self._logic.getKeySuffix(entity)

    context['form'] = form
    context['entity'] = entity
    context['entity_suffix'] = suffix
    context['entity_type'] = params['name']
    context['entity_type_plural'] = params['name_plural']
    context['entity_type_short'] = params['name_short']
    context['entity_type_url'] = params['url_name']
    context['edit_cancel_redirect'] = params.get('edit_cancel_redirect')
    context['return_url'] = request.path

    if params.get('export_content_type') and entity:
      context['export_link'] = redirects.getExportRedirect(entity, params)

    if entity:
      template = params['edit_template']
    else:
      template = params['create_template']

    return helper.responses.respond(request, template, context)

  def getParams(self):
    """Returns this view's params attribute.
    """

    return self._params

  @decorators.merge_params
  def getSidebarMenus(self, id, user, params=None):
    """Returns an dictionary with one sidebar entry.

    Args:
      params: a dict with params for this View

    Params usage:
      The params dictionary is passed as argument to getSidebarItems
      from the soc.views.sitemap.sidebar module, see the docstring
      of _getSidebarItems on how it uses it.
    """

    return sitemap.sidebar.getSidebarMenus(id, user, params=params)

  @decorators.merge_params
  def getDjangoURLPatterns(self, params=None):
    """Retrieves a list of sidebar entries for this view

    Params usage:
      The params dictionary is passed to the getDjangoURLPatterns
      function in the soc.views.sitemap.sitemap module, see the
      docstring of getDjangoURLPatterns on how it uses it.

    Args:
      params: a dict with params for this View
    """

    return sitemap.sitemap.getDjangoURLPatterns(params)

