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

"""Developer views for editing and examining Documents.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users

from django import http
from django import newforms as forms
from django.utils.translation import ugettext_lazy

from soc.logic import document
from soc.logic import out_of_band
from soc.logic import path_linkname
from soc.logic.site import id_user
from soc.views import helper
import soc.views.helper.requests
from soc.views import simple
from soc.views.helpers import custom_widgets
from soc.views.helpers import forms_helpers
from soc.views.helpers import response_helpers
from soc.views.user import profile

import soc.models.document


class EditForm(forms_helpers.DbModelForm):
  """Django form displayed when Developer edits a Document.
  """
  doc_key_name = forms.CharField(widget=forms.HiddenInput)
  content = forms.fields.CharField(widget=custom_widgets.TinyMCE())
  
  class Meta:
    model = soc.models.document.Document
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'user', 'created', 'modified']
 
  def clean_partial_path(self):
    partial_path = self.cleaned_data.get('partial_path')
    # TODO(tlarsen): combine path and link_name and check for uniqueness
    return partial_path

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    # TODO(tlarsen): combine path and link_name and check for uniqueness
    return link_name


DEF_SITE_DOCS_EDIT_TMPL = 'soc/site/docs/edit.html'
DEF_CREATE_NEW_DOC_MSG = ' You can create a new document by visiting the' \
                         ' <a href="/site/docs/edit">Create ' \
                         'a New Document</a> page.'

def edit(request, partial_path=None, linkname=None,
         template=DEF_SITE_DOCS_EDIT_TMPL):
  """View for a Developer to modify the properties of a Document Model entity.

  Args:
    request: the standard django request object
    partial_path: the Document's site-unique "path" extracted from the URL,
      minus the trailing link_name
    link_name: the last portion of the Document's site-unique "path"
      extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)

  logged_in_id = users.get_current_user()
  
  alt_response = simple.getAltResponseIfNotDeveloper(request, context, 
                                                     id=logged_in_id)
  if alt_response:
    # not a developer
    return alt_response
  
  alt_response = simple.getAltResponseIfNotLoggedIn(request, context, 
                                                    id=logged_in_id)
  if alt_response:
    # not logged in
    return alt_response
  
  alt_response = simple.getAltResponseIfNotUser(request, context, 
                                                id = logged_in_id)
  if alt_response:
    # no existing User entity for logged in Google Account. User entity is 
    # required for creating Documents
    return alt_response

  alt_response = simple.getAltResponseIfNotDeveloper(request,
                                                     context=context)
  if alt_response:
    return alt_response

  doc = None  # assume that no Document entity will be found

  path = path_linkname.combinePath([partial_path, linkname])

  # try to fetch Document entity corresponding to path if one exists    
  try:
    doc = document.getDocumentIfPath(path)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when path doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_DOC_MSG
    return simple.errorResponse(request, error, template, context)

  if request.method == 'POST':
    form = EditForm(request.POST)

    if form.is_valid():
      new_partial_path = form.cleaned_data.get('partial_path')
      new_linkname = form.cleaned_data.get('link_name')
      title = form.cleaned_data.get('title')
      short_name = form.cleaned_data.get('short_name')
      abstract = form.cleaned_data.get('abstract')
      content = form.cleaned_data.get('content')
      doc_key_name = form.cleaned_data.get('doc_key_name')
      
      doc = soc.logic.document.updateOrCreateDocument(
          partial_path=new_partial_path, link_name=new_linkname,
          title=title, short_name=short_name, abstract=abstract,
          content=content, user=id_user.getUserFromId(logged_in_id))
      
      if not doc:
        return http.HttpResponseRedirect('/')

      new_path = path_linkname.combinePath([new_partial_path, new_linkname])
        
      # redirect to new /site/docs/edit/new_path?s=0
      # (causes 'Profile saved' message to be displayed)
      return response_helpers.redirectToChangedSuffix(
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
        context['submit_message'] = (
            helper.requests.getSingleIndexedParamValue(
                request, profile.SUBMIT_MSG_PARAM_NAME,
                values=profile.SUBMIT_MESSAGES))

        # populate form with the existing User entity
        form = EditForm(initial={'doc_key_name': doc.key().name(),
            'title': doc.title, 'partial_path': doc.partial_path,
            'link_name': doc.link_name, 'short_name': doc.short_name,
            'abstract': doc.abstract, 'content': doc.content,
            'user': doc.user})       
      else:
        if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
          # redirect to aggressively remove 'Profile saved' query parameter
          return http.HttpResponseRedirect(request.path)
          
        context['lookup_error'] = ugettext_lazy(
            'Document with that path not found.')
        form = EditForm(initial={'link_name': linkname})
    else:  # no link name specified in the URL
      if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)

      # no link name specified, so start with an empty form
      form = EditForm()

  context.update({'form': form,
                  'existing_doc': doc})

  return response_helpers.respond(request, template, context)


class CreateForm(forms_helpers.DbModelForm):
  """Django form displayed when Developer creates a Document.
  """
  doc_key_name = forms.CharField(widget=forms.HiddenInput)
  content = forms.fields.CharField(widget=custom_widgets.TinyMCE())
  
  class Meta:
    model = soc.models.document.Document
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'user', 'created', 'modified']
 
  def clean_partial_path(self):
    partial_path = self.cleaned_data.get('partial_path')
    # TODO(tlarsen): combine path and link_name and check for uniqueness
    return partial_path

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    # TODO(tlarsen): combine path and link_name and check for uniqueness
    return link_name


DEF_SITE_DOCS_CREATE_TMPL = 'soc/site/docs/edit.html'

def create(request, template=DEF_SITE_DOCS_CREATE_TMPL):
  """View for a Developer to create a new Document entity.

  Args:
    request: the standard django request object
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)

  alt_response = simple.getAltResponseIfNotDeveloper(request,
                                                     context=context)
  if alt_response:
    return alt_response

  if request.method == 'POST':
    form = CreateForm(request.POST)

    if form.is_valid():
      new_partial_path = form.cleaned_data.get('partial_path')
      new_linkname = form.cleaned_data.get('link_name')
      title = form.cleaned_data.get('title')
      short_name = form.cleaned_data.get('short_name')
      abstract = form.cleaned_data.get('abstract')
      content = form.cleaned_data.get('content')
      doc_key_name = form.cleaned_data.get('doc_key_name')
      
      doc = soc.logic.document.updateOrCreateDocument(
          partial_path=new_partial_path, link_name=new_linkname,
          title=title, short_name=short_name, abstract=abstract,
          content=content, user=id_user.getUserFromId(logged_in_id))

      if not doc:
        return http.HttpResponseRedirect('/')

      new_path = path_linkname.combinePath([new_partial_path, new_linkname])
        
      # redirect to new /site/docs/edit/new_path?s=0
      # (causes 'Profile saved' message to be displayed)
      return response_helpers.redirectToChangedSuffix(
          request, None, new_path,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # no link name specified, so start with an empty form
    form = CreateForm()

  context.update({'form': form})

  return response_helpers.respond(request, template, context)
