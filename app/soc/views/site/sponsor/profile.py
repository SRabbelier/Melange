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

from django import http
from django import newforms as forms

import soc.logic
from soc.logic import validate
from soc.logic import out_of_band
from soc.logic.helper import access
from soc.logic.site import id_user
from soc.views import helper
import soc.views.helper.forms
import soc.views.helper.requests
import soc.views.helper.responses
import soc.views.helper.widgets
from soc.views import simple
from soc.views.user import profile

import soc.models.sponsor


class CreateForm(helper.forms.DbModelForm):
  """Django form displayed when creating a Sponsor.
  """
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.sponsor.Sponsor
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['founder', 'inheritance_line']
  
  # TODO(pawel.solyga): write validation functions for other fields
  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    if soc.logic.sponsor_logic.getFromFields(link_name=link_name):
      raise forms.ValidationError("This link name is already in use.")
    return link_name


class EditForm(CreateForm):
  """Django form displayed when editing a Sponsor.
  """
  link_name = forms.CharField(widget=helper.widgets.ReadOnlyInput())

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    return link_name


DEF_SITE_SPONSOR_PROFILE_EDIT_TMPL = 'soc/site/sponsor/profile/edit.html'
DEF_SPONSOR_NO_LINKNAME_CHANGE_MSG = 'Sponsor link name cannot be changed.'
DEF_CREATE_NEW_SPONSOR_MSG = ' You can create a new sponsor by visiting' \
                          ' <a href="/site/sponsor/profile">Create ' \
                          'a New Sponsor</a> page.'

def edit(request, link_name=None, template=DEF_SITE_SPONSOR_PROFILE_EDIT_TMPL):
  """View for a Developer to modify the properties of a Sponsor Model entity.

  Args:
    request: the standard django request object
    link_name: the Sponsor's site-unique "link_name" extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.logic.out_of_band.AccessViolationResponse, alt_response:
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)

  logged_in_id = users.get_current_user()
  user = soc.logic.user_logic.getFromFields(email=logged_in_id)
  sponsor_form = None
  existing_sponsor = None

  # try to fetch Sponsor entity corresponding to link_name if one exists
  try:
    existing_sponsor = soc.logic.sponsor_logic.getIfFields(link_name=link_name)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link name doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_SPONSOR_MSG
    return simple.errorResponse(request, error, template, context)
     
  if request.method == 'POST':
    if existing_sponsor:
      sponsor_form = EditForm(request.POST)
    else:
      sponsor_form = CreateForm(request.POST)

    if sponsor_form.is_valid():
      if link_name:
        # Form doesn't allow to change link_name but somebody might want to
        # abuse that manually, so we check if form link_name is the same as
        # url link_name
        if sponsor_form.cleaned_data.get('link_name') != link_name:
          msg = DEF_SPONSOR_NO_LINKNAME_CHANGE_MSG
          error = out_of_band.ErrorResponse(msg)
          return simple.errorResponse(request, error, template, context)
      
      fields = {}      
      
      # Ask for all the fields and pull them out 
      for field in sponsor_form.cleaned_data:
        value = sponsor_form.cleaned_data.get(field)
        fields[field] = value
      
      fields['founder'] = user
      
      form_ln = fields['link_name']
      form_sponsor = soc.logic.sponsor_logic.updateOrCreateFromFields(fields, link_name=form_ln)
      
      if not form_sponsor:
        return http.HttpResponseRedirect('/')
        
      # redirect to new /site/sponsor/profile/form_link_name?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, None, form_ln,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)

  else: # request.method == 'GET'
    if existing_sponsor:
      # is 'Profile saved' parameter present, but referrer was not ourself?
      # (e.g. someone bookmarked the GET that followed the POST submit) 
      if (request.GET.get(profile.SUBMIT_MSG_PARAM_NAME)
          and (not helper.requests.isReferrerSelf(request, suffix=link_name))):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)
      
      # referrer was us, so select which submit message to display
      # (may display no message if ?s=0 parameter is not present)
      context['notice'] = (
          helper.requests.getSingleIndexedParamValue(
              request, profile.SUBMIT_MSG_PARAM_NAME,
              values=profile.SUBMIT_MESSAGES))    
              
      # populate form with the existing Sponsor entity
      sponsor_form = EditForm(instance=existing_sponsor)
    else:
      if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)
      
      # no Sponsor entity exists for this link name, so show a blank form
      sponsor_form = CreateForm()
    
  context.update({'form': sponsor_form,
                  'existing_group':  existing_sponsor,
                  'group_type': 'Sponsor'})

  return helper.responses.respond(request, template, context)


DEF_SITE_SPONSOR_PROFILE_CREATE_TMPL = 'soc/group/profile/edit.html'

def create(request, template=DEF_SITE_SPONSOR_PROFILE_CREATE_TMPL):
  """create() view is same as edit() view, but with no link_name supplied.
  """
  return edit(request, link_name=None, template=template)


def delete(request, link_name=None, template=DEF_SITE_SPONSOR_PROFILE_EDIT_TMPL):
  """Request handler for a Developer to delete Sponsor Model entity.

  Args:
    request: the standard django request object
    link_name: the Sponsor's site-unique "link_name" extracted from the URL
    template: the "sibling" template (or a search list of such templates)
      from which to construct the public.html template name (or names)

  Returns:
    A subclass of django.http.HttpResponse which redirects 
    to /site/sponsor/list.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.logic.out_of_band.AccessViolationResponse, alt_response:
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)

  existing_sponsor = None

  # try to fetch Sponsor entity corresponding to link_name if one exists
  try:
    existing_sponsor = soc.logic.sponsor_logic.getIfFields(link_name=link_name)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link name doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_SPONSOR_MSG
    return simple.errorResponse(request, error, template, context)

  if existing_sponsor:
    # TODO(pawel.solyga): Create specific delete method for Sponsor model
    # Check if Sponsor can be deleted (has no Hosts and Programs)
    soc.logic.sponsor_logic.delete(existing_sponsor)

  return http.HttpResponseRedirect('/site/sponsor/list')