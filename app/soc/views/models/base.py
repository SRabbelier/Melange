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
from django.conf.urls import defaults
from django.utils.translation import ugettext_lazy

import soc.logic
import soc.logic.lists
import soc.views.helper.lists
import soc.views.helper.responses

from soc.logic import dicts
from soc.logic import models
from soc.models import linkable
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access


class View(object):
  """Views for entity classes.

  The View class functions specific to Entity classes by relying
  on the the child-classes to define the following fields:

  self._logic: the logic singleton for this entity
  """

  DEF_SUBMIT_MSG_PARAM_NAME = 's'
  DEF_SUBMIT_MSG_PROFILE_SAVED = 0

  DEF_CREATE_NEW_ENTITY_MSG_FMT = ugettext_lazy(
      ' You can create a new %(entity_type)s by visiting'
      ' <a href="%(create)s">Create '
      'a New %(entity_type)s</a> page.')

  def __init__(self, params=None):
    """

    Args:
      params: This dictionary should be filled with the parameters
        specific to this entity, required fields are:
        rights: This dictionary should be filled with the access check
                functions that should be called
        name: the name of the entity (names should have sentence-style caps) 
        name_short: the short form name of the name ('org' vs 'organization')
        name_plural: the plural form of the name
        url_name: the name of the entity used in urls
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
        sidebar_defaults: a dictionary with defaults for the sidebar; each
          value in the dict is a two-tuple:
          (url_format,       # supplied a single positional url_name
           menu_text_format) # supplied the params dict
    """

    rights = {}
    rights['unspecified'] = []
    rights['any_access'] = [access.checkIsLoggedIn]
    rights['public'] = [access.checkIsUser]
    rights['create'] = [access.checkIsDeveloper]
    rights['edit'] = [access.checkIsDeveloper]
    rights['delete'] = [access.checkIsDeveloper]
    rights['list'] = [access.checkIsDeveloper]

    if 'rights' in params:
      rights = dicts.merge(params['rights'], rights)

    new_params = {}
    new_params['rights'] = rights
    new_params['create_redirect'] = '/%(url_name)s' % params
    new_params['edit_redirect'] = '/%(url_name)s/edit' % params
    new_params['missing_redirect'] = '/%(url_name)s/create' % params
    new_params['delete_redirect'] = '/%(url_name)s/list' % params
    new_params['invite_redirect'] = '/request/list'
    
    new_params['sidebar'] = None
    new_params['sidebar_defaults'] = [
     ('/%s/create', 'New %(name)s', 'create'),
     ('/%s/list', 'List %(name_plural)s', 'list'),
    ]
    new_params['sidebar_additional'] = []

    new_params['key_fields_prefix'] = []

    new_params['django_patterns'] = None
    new_params['django_patterns_defaults'] = [
        (r'^%(url_name)s/show/%(key_fields)s$', 
            'soc.views.models.%s.public', 'Show %(name_short)s'),
        (r'^%(url_name)s/create$',
            'soc.views.models.%s.create', 'Create %(name_short)s'),
        (r'^%(url_name)s/create/%(key_fields)s$',
            'soc.views.models.%s.create', 'Create %(name_short)s'),
        (r'^%(url_name)s/delete/%(key_fields)s$',
            'soc.views.models.%s.delete', 'Delete %(name_short)s'),
        (r'^%(url_name)s/edit/%(key_fields)s$',
            'soc.views.models.%s.edit', 'Edit %(name_short)s'),
        (r'^%(url_name)s/list$',
            'soc.views.models.%s.list', 'List %(name_plural)s'),
        ]

    new_params['public_template'] = 'soc/%(module_name)s/public.html' % params
    new_params['create_template'] = 'soc/models/edit.html'
    new_params['edit_template'] = 'soc/models/edit.html'
    new_params['list_template'] = 'soc/models/list.html'
    new_params['invite_template'] = 'soc/models/invite.html'

    new_params['error_public'] = 'soc/%(module_name)s/error.html' % params
    new_params['error_edit'] = 'soc/%(module_name)s/error.html'  % params

    new_params['list_main'] = 'soc/list/main.html'
    new_params['list_pagination'] = 'soc/list/pagination.html'
    new_params['list_row'] = 'soc/%(module_name)s/list/row.html' % params
    new_params['list_heading'] = 'soc/%(module_name)s/list/heading.html' % params

    new_params['list_action'] = (self.getEditRedirect, None)
    new_params['list_params'] = {
        'list_action': 'action',
        'list_description': 'description',
        'list_main': 'main',
        'list_pagination': 'pagination',
        'list_row': 'row',
        'list_heading': 'heading',
        }

    description = ugettext_lazy('List of %(name_plural)s in Google Open Source Programs.')
    new_params['list_description'] = description % params
    new_params['save_message'] = [ugettext_lazy('Profile saved.')]
    new_params['edit_params'] = {
        self.DEF_SUBMIT_MSG_PARAM_NAME: self.DEF_SUBMIT_MSG_PROFILE_SAVED,
        }

    self._params = dicts.merge(params, new_params)
    self._logic = self._params['logic']

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
    except out_of_band.Error, error:
      return error.response(request)

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
    except out_of_band.Error, error:
      return error.response(request, template=params['error_public'],
                            context=context)

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

    if not kwargs:
      return self.edit(request, page_name=page_name, params=params,
                       **empty_kwargs)
    else:
      return self.edit(request, page_name=page_name, params=params,
                       seed=kwargs, **empty_kwargs)

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
      self.checkAccess('edit', request, rights=params['rights'])
    except out_of_band.Error, error:
      return error.response(request)

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      if all(kwargs.values()):
        key_fields = self._logic.getKeyFieldsFromDict(kwargs)
        entity = self._logic.getIfFields(key_fields)
    except out_of_band.Error, error:
      if not seed:
        error.message_fmt = (
          error.message_fmt + self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
            'entity_type_lower' : params['name'].lower(),
            'entity_type' : params['name'],
            'create' : params['missing_redirect']})
        return error.response(request, template=params['error_public'],
                              context=context)

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

    request.path = params['edit_redirect']
    self._editPost(request, entity, fields)

    if not key_name:
      key_fields =  self._logic.getKeyFieldsFromDict(fields)
      key_name = self._logic.getKeyNameForFields(key_fields)

    entity = self._logic.updateOrCreateFromKeyName(fields, key_name)

    if not entity:
      return http.HttpResponseRedirect('/')

    page_params = params['edit_params']
    new_suffix = self._logic.getKeySuffix(entity)

    # redirect to (possibly new) location of the entity
    # (causes 'Profile saved' message to be displayed)
    return helper.responses.redirectToChangedSuffix(
        request, None, new_suffix,
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

  def list(self, request, page_name=None, params=None, filter=None):
    """Displays the list page for the entity type.
    
    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      filter: a dict for the properties that the entities should have
    """

    params = dicts.merge(params, self._params)

    try:
      self.checkAccess('list', request)
    except out_of_band.Error, error:
      return error.response(request)

    content = helper.lists.getListContent(request, params, self._logic, filter)
    contents = [content]

    return self._list(request, params, contents, page_name)

  def _list(self, request, params, contents, page_name):
    """Returns the list page for the specified contents

    Args:
      request: the standard Django HTTP request object
      params: a dict with params for this View
      contents: a list of content dicts
      page_name: the page name displayed in templates as page and header title
    """

    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    context['list'] = soc.logic.lists.Lists(contents)

    context['entity_type'] = params['name']
    context['entity_type_plural'] = params['name_plural']

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
    except out_of_band.Error, error:
      return error.response(request)

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      key_fields = self._logic.getKeyFieldsFromDict(kwargs)
      entity = self._logic.getIfFields(key_fields)
    except out_of_band.Error, error:
      error.message_fmt = (
        error.message_fmt + self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
          'entity_type_lower' : params['name'].lower(),
          'entity_type' : params['name'],
          'create' : params['missing_redirect']})
      return error.response(request, template=params['error_edit'],
                            context=context)

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

  def getEditRedirect(self, entity, _):
    """Returns the edit redirect for the specified entity
    """

    suffix = self._logic.getKeySuffix(entity)
    url_name = self._params['url_name']
    return '/%s/edit/%s' % (url_name, suffix)

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
    context['entity_type_url'] = params['url_name']

    if entity:
      template = params['edit_template']
    else:
      template = params['create_template']

    return helper.responses.respond(request, template, context)

  def checkAccess(self, access_type, request, rights=None):
    """Runs all the defined checks for the specified type

    Args:
      access_type: the type of request (such as 'list' or 'edit')
      request: the Django request object

    Returns:
      True: If all the required access checks have been made successfully
      False: If a check failed, in this case self._response will contain
             the response provided by the failed access check.
    """

    rights = dicts.merge(rights, self._params['rights'])

    # Call each access checker
    for check in rights['any_access']:
      check(request)

    if access_type not in rights:
      for check in rights['unspecified']:
        # No checks defined, so do the 'generic check' and bail out
        check(request)
      return

    for check in rights[access_type]:
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
      pattern = r'(?P<%s>%s)' % (name, linkable.LINK_ID_PATTERN_CORE)
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

    for url, menu_text, access_type in defaults:
      url = url % params['url_name'].lower()
      item = (url, menu_text % params, access_type)
      result.append(item)

    for item in params['sidebar_additional']:
      result.append(item)

    return result

  def getSidebarLinks(self, request, params=None):
    """Returns an dictionary with one sidebar entry.

    Args:
      params: see __init__
    """

    params = dicts.merge(params, self._params)
    rights = params['rights']

    items = []

    for url, menu_text, access_type in self._getSidebarItems(params):
      try:
        self.checkAccess(access_type, request, rights)
        items.append({'url': url, 'title': menu_text})
      except out_of_band.Error:
        pass

    if not items:
      return

    res = {}

    if 'sidebar_heading' not in params:
      params['sidebar_heading'] = params['name']

    res['heading'] = params['sidebar_heading']
    res['items'] = items

    return res

  def getDjangoURLPatterns(self, params=None):
    """Retrieves a list of sidebar entries for this view from self._params.

    If self._params['django_patterns'] is None default entries will be
    constructed.
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
      name = name % params
      module = module % params['module_name']

      url = url % {
          'url_name': params['url_name'],
          'lnp': linkable.LINK_ID_ARG_PATTERN,
          'ulnp': linkable.LINK_ID_PATTERN_CORE,
          'key_fields': key_fields_pattern,
          }

      kwargs = {'page_name': name}

      item = (url, module, kwargs, name)
      patterns.append(item)

    return patterns
