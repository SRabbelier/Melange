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

"""Views for editing and examining Documents.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users

from django import forms
from django import http
from django.utils.translation import ugettext_lazy

from soc.logic import models
from soc.logic import out_of_band
from soc.logic import path_link_name
from soc.logic.models import document

from soc.views import helper
from soc.views import simple
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.user import profile

import soc.models.document
import soc.views.helper.forms
import soc.views.helper.requests
import soc.views.helper.responses
import soc.views.helper.widgets
import soc.views.out_of_band


DEF_CREATE_NEW_DOC_MSG = ' You can create a new document by visiting the' \
                         ' <a href="/document/edit">Create ' \
                         'a New Document</a> page.'

SUBMIT_MESSAGES = (
 ugettext_lazy('Document saved.'),
)


def getDocForForm(form):
  """Extracts doc fields from a form and creates a new doc from it.
  """

  user = users.get_current_user()

  scope_path = form.cleaned_data.get('scope_path')
  link_id = form.cleaned_data.get('link_id')

  properties = {}
  properties['scope_path'] = scope_path
  properties['link_id'] = link_id
  properties['title'] = form.cleaned_data.get('title')
  properties['short_name'] = form.cleaned_data.get('short_name')
  properties['content'] = form.cleaned_data.get('content')
  properties['author'] = models.user.logic.getForFields({'id': user}, unique=True)
  properties['is_featured'] = form.cleaned_data.get('is_featured')

  key_fields = document.logic.getKeyFieldsFromDict(properties)

  doc = document.logic.updateOrCreateFromFields(properties, key_fields)
  return doc


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when Developer creates a Document.
  """
  content = forms.fields.CharField(widget=helper.widgets.TinyMCE(
      attrs={'rows':10, 'cols':40}))

  class Meta:
    model = soc.models.document.Document

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'author', 'created', 'modified']

  def clean_scope_path(self):
    scope_path = self.cleaned_data.get('scope_path')
    # TODO(tlarsen): combine path and link_id and check for uniqueness
    return scope_path

  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    # TODO(tlarsen): combine path and link_id and check for uniqueness
    return link_id


DEF_DOCS_CREATE_TMPL = 'soc/models/edit.html'

@decorators.view
def create(request, page_name=None, template=DEF_DOCS_CREATE_TMPL):
  """View to create a new Document entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    # TODO(tlarsen): change this to just limit the Documents that can be
    #   created by the User in their current Role
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  if request.method == 'POST':
    form = CreateForm(request.POST)

    if form.is_valid():
      doc = getDocForForm(form)

      if not doc:
        return http.HttpResponseRedirect('/')

      new_path = path_link_name.combinePath([doc.scope_path, doc.link_id])

      # redirect to new /document/edit/new_path?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, None, new_path,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # no link ID specified, so start with an empty form
    form = CreateForm()

  context['form'] = form

  return helper.responses.respond(request, template, context)


DEF_DOCS_EDIT_TMPL = 'soc/models/edit.html'

class EditForm(CreateForm):
  """Django form displayed a Document is edited.
  """
  doc_key_name = forms.fields.CharField(widget=forms.HiddenInput)
  created_by = forms.fields.CharField(widget=helper.widgets.ReadOnlyInput(),
                                      required=False)


@decorators.view
def edit(request, page_name=None, scope_path=None, link_id=None,
         template=DEF_DOCS_EDIT_TMPL):
  """View to modify the properties of a Document Model entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    scope_path: the Document's site-unique "path" extracted from the URL,
      minus the trailing link_id
    link_id: the last portion of the Document's site-unique "path"
      extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    # TODO(tlarsen): change this to just limit the Documents that can be
    #   edited by the User in their current Role
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  doc = None  # assume that no Document entity will be found

  path = path_link_name.combinePath([scope_path, link_id])

  # try to fetch Document entity corresponding to path if one exists    
  try:
    if path:
      doc = document.logic.getFromFields(scope_path=scope_path,
                                         link_id=link_id)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when path doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_DOC_MSG
    return simple.errorResponse(request, page_name, error, template, context)

  if request.method == 'POST':
    form = EditForm(request.POST)

    if form.is_valid():
      doc = getDocForForm(form)
      
      if not doc:
        return http.HttpResponseRedirect('/')

      new_path = path_link_name.combinePath([doc.scope_path, doc.link_id])
        
      # redirect to new /document/edit/new_path?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, path, new_path,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # try to fetch Document entity corresponding to path if one exists
    if path:
      if doc:
        # is 'Profile saved' parameter present, but referrer was not ourself?
        # (e.g. someone bookmarked the GET that followed the POST submit) 
        if (request.GET.get(profile.SUBMIT_MSG_PARAM_NAME)
            and (not helper.requests.isReferrerSelf(request, suffix=path))):
          # redirect to aggressively remove 'Profile saved' query parameter
          return http.HttpResponseRedirect(request.path)
    
        # referrer was us, so select which submit message to display
        # (may display no message if ?s=0 parameter is not present)
        context['notice'] = (
            helper.requests.getSingleIndexedParamValue(
                request, profile.SUBMIT_MSG_PARAM_NAME,
                values=SUBMIT_MESSAGES))

        # populate form with the existing Document entity
        author_link_id = doc.author.link_id
        form = EditForm(initial={'doc_key_name': doc.key().name(),
            'title': doc.title, 'scope_path': doc.scope_path,
            'link_id': doc.link_id, 'short_name': doc.short_name,
            'content': doc.content, 'author': doc.author,
            'is_featured': doc.is_featured, 'created_by': author_link_id})
      else:
        if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
          # redirect to aggressively remove 'Profile saved' query parameter
          return http.HttpResponseRedirect(request.path)
          
        context['lookup_error'] = ugettext_lazy(
            'Document with that path not found.')
        form = EditForm(initial={'link_id': link_id})
    else:  # no link ID specified in the URL
      if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)

      # no link ID specified, so start with an empty form
      form = EditForm()

  context.update({'form': form,
                  'entity': doc})

  return helper.responses.respond(request, template, context)


@decorators.view
def delete(request, page_name=None, scope_path=None, link_id=None,
           template=DEF_DOCS_EDIT_TMPL):
  """Request handler to delete Document Model entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    scope_path: the Document's site-unique "path" extracted from the URL,
      minus the trailing link_id
    link_id: the last portion of the Document's site-unique "path"
      extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which redirects 
    to /site/document/list.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    # TODO(tlarsen): change this to just limit the Documents that can be
    #   deleted by the User in their current Role
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  existing_doc = None
  path = path_link_name.combinePath([scope_path, link_id])

  # try to fetch Document entity corresponding to path if one exists    
  try:
    if path:
      existing_doc = document.logic.getFromFields(scope_path=scope_path,
                                                  link_id=link_id)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when path doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_DOC_MSG
    return simple.errorResponse(request, page_name, error, template, context)

  if existing_doc:
    document.logic.delete(existing_doc)

  return http.HttpResponseRedirect('/document/list')
