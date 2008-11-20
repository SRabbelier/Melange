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

"""Developer views for editing and examining Sponsor profiles.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django import http

from soc.logic import models
from soc.logic import out_of_band
from soc.logic import validate
from soc.logic.models import sponsor
from soc.views import helper
from soc.views import simple
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.user import profile

import soc.logic
import soc.models.sponsor as sponsor_model
import soc.views.helper.forms
import soc.views.helper.requests
import soc.views.helper.responses
import soc.views.helper.widgets
import soc.views.out_of_band


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when creating a Sponsor.
  """
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = sponsor_model.Sponsor
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['founder', 'inheritance_line']
  
  # TODO(pawel.solyga): write validation functions for other fields
  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
    if models.sponsor.logic.getFromFields(link_id=link_id):
      raise forms.ValidationError("This link ID is already in use.")
    return link_id


class EditForm(CreateForm):
  """Django form displayed when editing a Sponsor.
  """
  link_id = forms.CharField(widget=helper.widgets.ReadOnlyInput())
  founded_by = forms.CharField(widget=helper.widgets.ReadOnlyInput(),
                               required=False)

  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
    return link_id


DEF_SITE_SPONSOR_PROFILE_EDIT_TMPL = 'soc/site/sponsor/profile/edit.html'
DEF_SPONSOR_NO_LINK_ID_CHANGE_MSG = 'Sponsor link ID cannot be changed.'
DEF_CREATE_NEW_SPONSOR_MSG = ' You can create a new sponsor by visiting' \
                          ' <a href="/site/sponsor/profile">Create ' \
                          'a New Sponsor</a> page.'

@decorators.view
def edit(request, page_name=None, link_id=None,
         template=DEF_SITE_SPONSOR_PROFILE_EDIT_TMPL):
  """View for a Developer to modify the properties of a Sponsor Model entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    link_id: the Sponsor's site-unique "link_id" extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  user = models.user.logic.getForFields(
      {'account': users.get_current_user()}, unique=True)
  sponsor_form = None
  existing_sponsor = None

  # try to fetch Sponsor entity corresponding to link_id if one exists
  try:
    existing_sponsor = sponsor.logic.getIfFields(link_id=link_id)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link ID doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_SPONSOR_MSG
    return simple.errorResponse(request, page_name, error, template, context)
     
  if request.method == 'POST':
    if existing_sponsor:
      sponsor_form = EditForm(request.POST)
    else:
      sponsor_form = CreateForm(request.POST)

    if sponsor_form.is_valid():
      if link_id:
        # Form doesn't allow to change link_id but somebody might want to
        # abuse that manually, so we check if form link_id is the same as
        # url link_id
        if sponsor_form.cleaned_data.get('link_id') != link_id:
          msg = DEF_SPONSOR_NO_LINK_ID_CHANGE_MSG
          error = out_of_band.ErrorResponse(msg)
          return simple.errorResponse(request, page_name, error, template, context)
      
      fields = {}      
      
      # Ask for all the fields and pull them out 
      for field in sponsor_form.cleaned_data:
        value = sponsor_form.cleaned_data.get(field)
        fields[field] = value
      
      if not existing_sponsor:
        fields['founder'] = user
      
      form_ln = fields['link_id']
      key_fields = models.sponsor.logic.getKeyFieldsFromKwargs(fields)
      form_sponsor = models.sponsor.logic.updateOrCreateFromFields(
          fields, key_fields)
      
      if not form_sponsor:
        return http.HttpResponseRedirect('/')
        
      # redirect to new /site/sponsor/profile/form_link_id?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, None, form_ln,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)

  else: # request.method == 'GET'
    if existing_sponsor:
      # is 'Profile saved' parameter present, but referrer was not ourself?
      # (e.g. someone bookmarked the GET that followed the POST submit) 
      if (request.GET.get(profile.SUBMIT_MSG_PARAM_NAME)
          and (not helper.requests.isReferrerSelf(request, suffix=link_id))):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)
      
      # referrer was us, so select which submit message to display
      # (may display no message if ?s=0 parameter is not present)
      context['notice'] = (
          helper.requests.getSingleIndexedParamValue(
              request, profile.SUBMIT_MSG_PARAM_NAME,
              values=profile.SUBMIT_MESSAGES))    
              
      # populate form with the existing Sponsor entity
      founder_link_id = existing_sponsor.founder.link_id
      sponsor_form = EditForm(instance=existing_sponsor, 
                              initial={'founded_by': founder_link_id})
    else:
      if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)
      
      # no Sponsor entity exists for this link ID, so show a blank form
      sponsor_form = CreateForm()
    
  context.update({'form': sponsor_form,
                  'entity':  existing_sponsor,
                  'entity_type': sponsor_model.Sponsor.TYPE_NAME,
                  'entity_type_short': sponsor_model.Sponsor.TYPE_NAME_SHORT})

  return helper.responses.respond(request, template, context)


DEF_SITE_SPONSOR_PROFILE_CREATE_TMPL = 'soc/group/profile/edit.html'

@decorators.view
def create(request, page_name=None, template=DEF_SITE_SPONSOR_PROFILE_CREATE_TMPL):
  """create() view is same as edit() view, but with no link_id supplied.
  """
  return edit(request, page_name=page_name, link_id=None, template=template)


@decorators.view
def delete(request, page_name=None, link_id=None,
           template=DEF_SITE_SPONSOR_PROFILE_EDIT_TMPL):
  """Request handler for a Developer to delete Sponsor Model entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    link_id: the Sponsor's site-unique "link_id" extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which redirects 
    to /site/sponsor/list.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  existing_sponsor = None

  # try to fetch Sponsor entity corresponding to link_id if one exists
  try:
    existing_sponsor = models.sponsor.logic.getIfFields(link_id=link_id)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link ID doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_SPONSOR_MSG
    return simple.errorResponse(request, page_name, error, template, context)

  if existing_sponsor:
    # TODO(pawel.solyga): Create specific delete method for Sponsor model
    # Check if Sponsor can be deleted (has no Hosts and Programs)
    models.sponsor.logic.delete(existing_sponsor)

  return http.HttpResponseRedirect('/site/sponsor/list')