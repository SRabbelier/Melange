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
  '"Todd Larsen" <tlarsen@google.com>',
  '"Sverre Rabbelier" <sverer@rabbelier.nl>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django import http
from django.utils.translation import ugettext_lazy

import soc.logic
import soc.logic.out_of_band
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.out_of_band

from soc.logic import models
from soc.logic import validate
from soc.views import simple
from soc.views import helper
from soc.views.helper import access


class View:
  """Views for entity classes.

  The View class functions specific to Entity classes by relying
  on the the child-classes to define the following fields:

  self._logic: the logic singleton for this entity
  """

  def __init__(self, params=None, rights=None):
    """

    Args:
      rights: This dictionary should be filled with the access check
        functions that should be called
      params: This dictionary should be filled with the parameters
        specific to this entity.
    """

    new_rights = {}
    new_rights['base'] = [access.checkIsLoggedIn]

    self._rights = soc.logic.dicts.mergeDicts(rights, new_rights)
    self._params = params

    self.DEF_SUBMIT_MSG_PARAM_NAME = 's'

    self.DEF_CREATE_NEW_ENTITY_MSG = ugettext_lazy(
        ' You can create a new %(model_type)s by visiting'
        ' <a href="%(create)s">Create '
        'a New %(Type)s</a> page.')

  def public(self, request, page=None, **kwargs):
    """Displays the public page for the entity specified by **kwargs

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object which is abstraction
        that combines a Django view with sidebar menu info
      kwargs: the Key Fields for the specified entity
    """

    try:
      self.checkAccess('edit', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page'] = page
    entity = None

    try:
      entity = self._logic.getIfFields(**kwargs)
    except soc.logic.out_of_band.ErrorResponse, error:
      template = soc._params['public_template']
      return simple.errorResponse(request, error, template, context)

    if not entity:
      #TODO: Change this into a proper redirect
      return http.HttpResponseRedirect('/')

    self._makePublic(entity)

    context['entity'] = entity
    context['entity_type'] = self._params['name']

    template = self._params['public_template']

    return helper.responses.respond(request, template, context)

  def create(self, request, page=None, **kwargs):
    """Displays the create page for this entity type

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object which is abstraction
        that combines a Django view with sidebar menu info
      kwargs: not used for create()
    """

    # Create page is an edit page with no key fields
    kwargs = {}
    return self.edit(request, page=page, **kwargs)

  def edit(self, request, page=None, **kwargs):
    """Displays the public page for the entity specified by **kwargs

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object which is abstraction
        that combines a Django view with sidebar menu info
      kwargs: The Key Fields for the specified entity
    """

    try:
      self.checkAccess('edit', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    context = helper.responses.getUniversalContext(request)
    context['page'] = page
    entity = None

    try:
      entity = self._logic.getIfFields(**kwargs)
    except soc.logic.out_of_band.ErrorResponse, error:
      template = soc._params['public_template']
      error.message = error.message + self.DEF_CREATE_NEW_ENTITY_MSG % {
          'entity_type_lower' : self._params['name_lower'],
          'entity_type_upper' : self._parmas['name_upper'],
          'create' : self._redirects['create']
          }
      return simple.errorResponse(request, error, template, context)

    if request.method == 'POST':
      return self.editPost(request, entity, context)
    else:
      return self.editGet(request, entity, context)

  def editPost(self, request, entity, context):
    """Same as edit, but on POST
    """
    if entity:
      form = self._params['edit_form'](request.POST)
    else:
      form = self._params['create_form'](request.POST)

    if not form.is_valid():
      return

    fields = self.collectCleanedFields(form)

    self._editPost(request, entity, fields)

    keys = self._logic.extractKeyFields(fields)
    entity = self._logic.updateOrCreateFromFields(fields, **keys)

    if not entity:
      return http.HttpResponseRedirect('/')

    params=self._params['edit_params']
    #TODO(SRabbelier) Construct a suffix
    suffix = None

    # redirect to (possibly new) location of the entity
    # (causes 'Profile saved' message to be displayed)
    return helper.responses.redirectToChangedSuffix(
        request, None, suffix,
        params=params)

  def editGet(self, request, entity, context):
    """Same as edit, but on GET
    """
    #TODO(SRabbelier) Construct a suffix
    suffix = None
    is_self_referrer = helper.requests.isReferrerSelf(request, suffix=suffix)

    # Remove the params from the request, this is relevant only if
    # someone bookmarked a POST page.
    if request.GET.get(self.DEF_SUBMIT_MSG_PARAM_NAME):
      if (not entity) or (not is_self_referrer):
        return http.HttpResponseRedirect(request.path)

    if entity:
      # Note: no message will be displayed if parameter is not present
      context['notice'] = helper.requests.getSingleIndexedParamValue(
              request,
              self.DEF_SUBMIT_MSG_PARAM_NAME,
              values=self._params['save_message'])

      # populate form with the existing entity
      form = self._params['edit_form'](instance=entity)
    else:
      form = self._params['create_form']()

    context['form'] = form
    context['entity'] = entity
    context['entity_type'] = self._params['name']
    context['entity_type_plural'] = self._params['name_plural']

    template = self._params['create_template']

    return helper.responses.respond(request, template, context)

  def list(self, request, page=None):
    """Displays the list page for the entity type
    
    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object which is abstraction
        that combines a Django view with sidebar menu info
    """

    try:
      self.checkAccess('list', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    context = helper.responses.getUniversalContext(request)
    context['page'] = page

    offset, limit = helper.lists.cleanListParameters(
      offset=request.GET.get('offset'), limit=request.GET.get('limit'))

    # Fetch one more to see if there should be a 'next' link
    entities = self._logic.getForLimitAndOffset(limit + 1, offset=offset)

    context['pagination_form'] = helper.lists.makePaginationForm(request, limit)

    templates = self._params['lists_template']

    context = helper.lists.setList(request, context, entities, 
                                 offset, limit, templates)

    context['entity_type'] = self._params['name']
    context['entity_type_plural'] = self._params['name_plural']

    template = self._params['list_template']

    return helper.responses.respond(request, template, context)

  def delete(self, request, page=None, **kwargs):
    """Shows the delete page for the entity specified by kwargs

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object which is abstraction
        that combines a Django view with sidebar menu info
      kwargs: The Key Fields for the specified entity
    """

    try:
      self.checkAccess('delete', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page'] = page
    entity = None

    try:
      entity = models.sponsor.logic.getIfFields(**kwargs)
    except soc.logic.out_of_band.ErrorResponse, error:
      template = self._templates['create']
      error.message = error.message + DEF_CREATE_NEW_ENTITY_MSG % {
          'entity_type_lower' : self._name,
          'entity_type_upper' : self._Name,
           'create' : self._redirects['create']
           }
      return simple.errorResponse(request, error, template, context)

    if not entity:
      #TODO: Create a proper error page for this
      return http.HttpResponseRedirect('/')

    if not self._logic.isDeletable(entity):
      # TODO: Direct user to page telling them they can't delete that entity, and why
      pass

    self._logic.delete(entity)
    redirect = self._params['delete_redirect']

    return http.HttpResponseRedirect(redirect)

  def _editPost(self, request, entity, fields):
    """Performs any required processing on the entity to post its edit page

    Args:
      request: The django request object
      entity: the entity to make public
      fields: The new field values
    """

    pass

  def checkUnspecified(self, access_type, request):
    """Checks whether an unspecified access_type should be allowed

    Args:
      access_type: the access type (such as 'list' or 'edit') that was
                   not present in the _rights dictionary when checking.
    """

    pass

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

    if access_type not in self._rights:
      self.checkUnspecified(access_type, request)
      return

    # Call each access checker
    for check in self._rights['base']:
      check(request)

    for check in self._rights[access_type]:
      check(request)

    # All checks were successfull
    return

  def collectCleanedFields(self, form):
    """Collects all cleaned fields from form and returns them 

    Args:
      form: The form from which the cleaned fields should be collected
    """

    fields = {}

    for field, value in form.cleaned_data.iteritems():
      fields[field] = value

    return fields
