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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import http
from django.conf.urls import defaults
from django.utils.translation import ugettext_lazy

import soc.logic
import soc.logic.out_of_band
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.out_of_band

from soc.logic import dicts
from soc.logic import models
from soc.logic import path_link_name
from soc.views import simple
from soc.views import helper
from soc.views.helper import access


class View(object):
  """Views for entity classes.

  The View class functions specific to Entity classes by relying
  on the the child-classes to define the following fields:

  self._logic: the logic singleton for this entity
  """

  DEF_SUBMIT_MSG_PARAM_NAME = 's'
  DEF_SUBMIT_MSG_PROFILE_SAVED = 0

  DEF_CREATE_NEW_ENTITY_MSG = ugettext_lazy(
      ' You can create a new %(entity_type_lower)s by visiting'
      ' <a href="%(create)s">Create '
      'a New %(entity_type)s</a> page.')

  def __init__(self, params=None, rights=None):
    """

    Args:
      rights: This dictionary should be filled with the access check
        functions that should be called, it will be modified in-place.
      params: This dictionary should be filled with the parameters
        specific to this entity, required fields are:
        name: the name of the entity (names should have sentence-style caps) 
        name_short: the short form name of the name ('org' vs 'organization')
        name_plural: the plural form of the name
        edit_form: the class of the Django form to be used when editing
        create_form: the class of the Django form to be used when creating
        edit_template: the Django template to be used for editing
        public_template: the Django template to be used as public page 
        list_template: the Django template to be used as list page
        lists_template: the Django templates to search for the list page
        delete_redirect: the Django template to redirect to on delete
        create_redirect: the Django template to redirect to after creation
        save_message: the message to display when the entity is saved
        edit_params: the params to use when editing
        sidebar: the sidebar menu items for this view
        sidebar_defaults: a dictionary with defaults for the sidebar 
    """

    new_rights = {}
    new_rights['any_access'] = [access.checkIsUser]

    new_params = {}
    new_params['create_redirect'] = '/%s' % params['name_short'].lower()
    new_params['missing_redirect'] = '/%s/create' % params['name_short'].lower()

    new_params['sidebar'] = None
    new_params['sidebar_defaults'] = [
     ('/%s/create', 'New %(name)s'),
     ('/%s/list', 'List %(plural)s'),
    ]
    new_params['sidebar_additional'] = []

    new_params['key_fields_prefix'] = []

    new_params['django_patterns'] = None
    new_params['django_patterns_defaults'] = [
        (r'^%(name_lower)s/show/%(key_fields)s$', 
            'soc.views.models.%s.public', 'Show %(name)s'),
        (r'^%(name_lower)s/create$',
            'soc.views.models.%s.create', 'Create %(name)s'),
        (r'^%(name_lower)s/create/%(key_fields)s$',
            'soc.views.models.%s.create', 'Create %(name)s'),
        (r'^%(name_lower)s/delete/%(key_fields)s$',
            'soc.views.models.%s.delete', 'Delete %(name)s'),
        (r'^%(name_lower)s/edit/%(key_fields)s$',
            'soc.views.models.%s.edit', 'Edit %(name)s'),
        (r'^%(name_lower)s/list$',
            'soc.views.models.%s.list', 'List %(name_plural)s'),
        ]

    new_params['list_redirect_action'] = params['name_short'] + '/edit'

    self._rights = dicts.merge(rights, new_rights)
    self._params = dicts.merge(params, new_params)

  def public(self, request, page_name=None, params=None, **kwargs):
    """Displays the public page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    params = dicts.merge(params, self._params)

    try:
      self.checkAccess('public', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    if not all(kwargs.values()):
      #TODO: Change this into a proper redirect
      return http.HttpResponseRedirect('/')

    try:
      key_fields = self._logic.getKeyFieldsFromDict(kwargs)
      entity = self._logic.getIfFields(key_fields)
    except soc.logic.out_of_band.ErrorResponse, error:
      template = params['public_template']
      return simple.errorResponse(request, page_name, error, template, context)

    self._public(request, entity, context)

    context['entity'] = entity
    context['entity_type'] = params['name']

    template = params['public_template']

    return helper.responses.respond(request, template, context)

  def create(self, request, page_name=None, params=None, **kwargs):
    """Displays the create page for this entity type.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: not used for create()
    """

    params = dicts.merge(params, self._params)

    # Create page is an edit page with no key fields
    empty_kwargs = {}
    fields = self._logic.getKeyFieldNames()
    for field in fields:
      empty_kwargs[field] = None

    request.path = params['create_redirect']
    request.path = helper.requests.replaceSuffix(request.path,
                                                 old_suffix='edit',
                                                 new_suffix='edit')

    if not kwargs:
      return self.edit(request, page_name=page_name, params=params, **empty_kwargs)
    else:
      return self.edit(request, page_name=page_name, params=params, seed=kwargs, **empty_kwargs)

  def edit(self, request, page_name=None, params=None, seed=None, **kwargs):
    """Displays the edit page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity
    """

    params = dicts.merge(params, self._params)

    try:
      self.checkAccess('edit', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      if all(kwargs.values()):
        key_fields = self._logic.getKeyFieldsFromDict(kwargs)
        entity = self._logic.getIfFields(key_fields)
    except soc.logic.out_of_band.ErrorResponse, error:
      if not seed:
        template = params['public_template']
        error.message = error.message + self.DEF_CREATE_NEW_ENTITY_MSG % {
            'entity_type_lower' : params['name'].lower(),
            'entity_type' : params['name'],
            'create' : params['missing_redirect']
            }
        return simple.errorResponse(request, page_name, error, template, context)

    if request.method == 'POST':
      return self.editPost(request, entity, context, params)
    else:
      return self.editGet(request, entity, context, seed, params)

  def editPost(self, request, entity, context, params):
    """Same as edit, but on POST.
    """

    params = dicts.merge(params, self._params)

    if entity:
      form = params['edit_form'](request.POST)
    else:
      form = params['create_form'](request.POST)

    if not form.is_valid():
      return self._constructResponse(request, entity, context, form, params)

    key_name, fields = self.collectCleanedFields(form)

    # get the old_suffix before editing
    old_suffix = self._logic.getKeySuffix(entity)

    self._editPost(request, entity, fields)

    if not key_name:
      key_fields =  self._logic.getKeyFieldsFromDict(fields)
      key_name = self._logic.getKeyNameForFields(key_fields)

    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    if not entity:
      return http.HttpResponseRedirect('/')

    page_params = params['edit_params']
    suffix = self._logic.getKeySuffix(entity)

    # redirect to (possibly new) location of the entity
    # (causes 'Profile saved' message to be displayed)
    return helper.responses.redirectToChangedSuffix(
        request, old_suffix, suffix,
        params=page_params)

  def editGet(self, request, entity, context, seed, params):
    """Same as edit, but on GET.
    """

    params = dicts.merge(params, self._params)
    suffix = self._logic.getKeySuffix(entity)

    # Remove the params from the request, this is relevant only if
    # someone bookmarked a POST page.
    is_self_referrer = helper.requests.isReferrerSelf(request, suffix=suffix)
    if request.GET.get(self.DEF_SUBMIT_MSG_PARAM_NAME):
      if (not entity) or (not is_self_referrer):
        return http.HttpResponseRedirect(request.path)

    if entity:
      # Note: no message will be displayed if parameter is not present
      context['notice'] = helper.requests.getSingleIndexedParamValue(
          request, self.DEF_SUBMIT_MSG_PARAM_NAME,
          values=params['save_message'])

      # populate form with the existing entity
      form = params['edit_form'](instance=entity)
      if 'key_name' in form.fields:
        form.fields['key_name'].initial = entity.key().name()
      self._editGet(request, entity, form)
    else:
      if seed:
        self._editSeed(request, seed)
        form = params['create_form'](initial=seed)
      else:
        form = params['create_form']()

    return self._constructResponse(request, entity, context, form, params)

  def list(self, request, page_name=None, params=None):
    """Displays the list page for the entity type.
    
    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
    """

    params = dicts.merge(params, self._params)

    try:
      self.checkAccess('list', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name

    offset, limit = helper.lists.cleanListParameters(
      offset=request.GET.get('offset'), limit=request.GET.get('limit'))

    # Fetch one more to see if there should be a 'next' link
    entities = self._logic.getForLimitAndOffset(limit + 1, offset=offset)

    context['pagination_form'] = helper.lists.makePaginationForm(request, limit)

    templates = params['lists_template']

    context = helper.lists.setList(request, context, entities, 
                                 offset, limit, templates)

    context['entity_type'] = params['name']
    context['entity_type_plural'] = params['name_plural']
    context['redirect_action'] = params['list_redirect_action']

    template = params['list_template']

    return helper.responses.respond(request, template, context)

  def delete(self, request, page_name=None, params=None, **kwargs):
    """Shows the delete page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: The Key Fields for the specified entity
    """

    params = dicts.merge(params, self._params)

    try:
      self.checkAccess('delete', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      key_fields = self._logic.getKeyFieldsFromDict(kwargs)
      entity = self._logic.getIfFields(key_fields)
    except soc.logic.out_of_band.ErrorResponse, error:
      template = params['edit_template']
      error.message = error.message + self.DEF_CREATE_NEW_ENTITY_MSG % {
          'entity_type_lower' : params['name'].lower(),
          'entity_type' : params['name'],
          'create' : params['missing_redirect']
          }
      return simple.errorResponse(request, page_name, error, template, context)

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

  def _editPost(self, request, entity, fields):
    """Performs any required processing on the entity to post its edit page.

    Args:
      request: the django request object
      entity:  the entity to create or update from POST contents
      fields: the new field values
    """

    pass

  def _public(self, request, entity, context):
    """Performs any required processing to get an entities public page.

    Args:
      request: the django request object
      entity: the entity to make public
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

    pass

  def _editSeed(self, request, seed):
    """Performs any required processing on the form to get its edit page.

    Args:
      request: the django request object
      seed: the fields to seed the create page with
    """

    pass

  def checkUnspecified(self, access_type, request):
    """Checks whether an unspecified access_type should be allowed.

    Args:
      access_type: the access type (such as 'list' or 'edit') that was
                   not present in the _rights dictionary when checking.
    """

    pass

  def _constructResponse(self, request, entity, context, form, params):
    """Updates the context and returns a response for the specified arguments.

    Args:
      request: the django request object
      entity: the entity that is used
      context: the context to be used
      form: the form that will be used
      params: a dict with params for this View
    """

    suffix = self._logic.getKeySuffix(entity)

    context['form'] = form
    context['entity'] = entity
    context['entity_suffix'] = suffix
    context['entity_type'] = params['name']
    context['entity_type_plural'] = params['name_plural']
    context['entity_type_short'] = params['name_short']

    template = params['edit_template']

    return helper.responses.respond(request, template, context)

  def checkAccess(self, access_type, request):
    """Runs all the defined checks for the specified type

    Args:
      access_type: the type of request (such as 'list' or 'edit')
      request: the Django request object

    Returns:
      True: If all the required access checks have been made successfully
      False: If a check failed, in this case self._response will contain
             the response provided by the failed access check.
    """

    # Call each access checker
    for check in self._rights['any_access']:
      check(request)

    if access_type not in self._rights:
       # No checks defined, so do the 'generic check' and bail out
      self.checkUnspecified(access_type, request)
      return

    for check in self._rights[access_type]:
      check(request)

  def collectCleanedFields(self, form):
    """Collects all cleaned fields and returns them with the key_name.

    Args:
      form: The form from which the cleaned fields should be collected
    """

    fields = {}

    key_name = None
    if 'key_name' in form.cleaned_data:
      key_name = form.cleaned_data.pop('key_name')

    for field, value in form.cleaned_data.iteritems():
      fields[field] = value

    return key_name, fields

  def getKeyFieldsPattern(self, params):
    """
    """

    names = self._logic.getKeyFieldNames()
    patterns = params['key_fields_prefix']

    for name in names:
      pattern = r'(?P<%s>%s)' % (name, path_link_name.LINKNAME_PATTERN_CORE)
      patterns.append(pattern)

    result = '/'.join(patterns)
    return result

  def _getSidebarItems(self, params):
    """Retrieves a list of sidebar entries for this view from self._params.

    If params['sidebar'] is None default entries will be constructed 
    """

    # Return the found result
    if params['sidebar']:
      return params['sidebar']

    # Construct defaults manualy
    defaults = params['sidebar_defaults']

    result = []

    for url, title in defaults:
      url = url % params['name_short'].lower()

      title = title % {
          'name': params['name'],
          'plural': params['name_plural']
          }

      item = (url, title)
      result.append(item)

    for item in params['sidebar_additional']:
      result.append(item)

    return result

  def getSidebarLinks(self, params=None):
    """Returns an dictionary with one sidebar entry.

    Args:
      params: see __init__
    """

    params = dicts.merge(params, self._params)

    items = []

    for url, title in self._getSidebarItems(params):
      items.append({'url': url, 'title': title})

    res = {}
    res['heading'] = params['name']
    res['items'] = items

    return res

  def getDjangoURLPatterns(self, params=None):
    """Retrieves a list of sidebar entries for this view from self._params.

    If self._params['django_patterns'] is None default entries will be constructed.
    """

    params = dicts.merge(params, self._params)

    # Return the found result
    if params['django_patterns']:
      return params['django_patterns']

    # Construct defaults manualy
    default_patterns = params['django_patterns_defaults']
    key_fields_pattern = self.getKeyFieldsPattern(params)

    patterns = []

    for url, module, name in default_patterns:
      name_short_lower = params['name_short'].lower()
      name_plural_lower = params['name_plural'].lower() 

      name = name % {
          'name': name_short_lower, 
          'name_plural': name_plural_lower,
          }

      module = module % name_short_lower

      url = url % {
          'name_lower': name_short_lower,
          'lnp': path_link_name.LINKNAME_ARG_PATTERN,
          'ulnp': path_link_name.LINKNAME_PATTERN_CORE,
          'key_fields': key_fields_pattern,
          }

      kwargs = {'page_name': name}

      item = (url, module, kwargs, name)
      patterns.append(item)

    return patterns
