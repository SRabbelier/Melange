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

"""Developer views for editing and examining User profiles.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]

import re
import logging

from google.appengine.api import users
from django import http
from django import shortcuts
from django import newforms as forms

from soc.logic import out_of_band
from soc.logic.site import id_user
from soc.views import simple
from soc.views.helpers import forms_helpers
from soc.views.helpers import response_helpers
from soc.views.helpers import template_helpers

import soc.models.user


class LookupForm(forms_helpers.DbModelForm):
  """Django form displayed for a Developer to look up a User.
  """
  id = forms.EmailField(required=False)
  link_name = forms.CharField(required=False)

  class Meta:
    model = None

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')

    if not link_name:
      # link name not supplied (which is OK), so do not try to validate it
      return None

    if not id_user.isLinkNameFormatValid(link_name):
      raise forms.ValidationError('This link name is in wrong format.')
    
    return link_name

  def clean_id(self):
    email = self.cleaned_data.get('id')
    
    if not email:
      # email not supplied (which is OK), so do not try to convert it
      return None
  
    try:
      return users.User(email=email)
    except users.UserNotFoundError:
      raise forms.ValidationError('Account not found.')
    

DEF_SITE_USER_PROFILE_LOOKUP_TMPL = 'soc/site/user/profile/lookup.html'

def lookup(request, template=DEF_SITE_USER_PROFILE_LOOKUP_TMPL):
  """View for a Developer to look up a User Model entity.

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

  logged_in_id = users.get_current_user()

  alt_response = simple.getAltResponseIfNotDeveloper(request, context, 
                                                        id = logged_in_id)
  if alt_response:
    # not a developer
    return alt_response
  
  alt_response = simple.getAltResponseIfNotLoggedIn(request, context, 
                                                        id = logged_in_id)
  if alt_response:
    # not logged in
    return alt_response

  user = None  # assume that no User entity will be found
  form = None  # assume blank form needs to be displayed
  lookup_message = 'Enter information to look up a User.'
  lookup_error = None  # assume no look-up errors
  edit_link = None  # assume no User entity found to be edited

  if request.method == 'POST':
    form = LookupForm(request.POST)

    if form.is_valid():
      form_id = form.cleaned_data.get('id')
      
      if form_id:
        # email provided, so attempt to look up user by email
        user = id_user.getUserFromId(form_id)

        if user:
          lookup_message = 'User found by email.'
        else:
          lookup_error = 'User with that email not found.'

      if not user:
        # user not found yet, so see if link name was provided
        linkname = form.cleaned_data.get('link_name')
        
        if linkname:
          # link name provided, so try to look up by link name 
          user = id_user.getUserFromLinkName(linkname)
        
          if user:
            lookup_message = 'User found by link name.'
            lookup_error = None  # clear previous error, now that User was found
          else:
            if form_id:
              # email was provided, so look up failure is due to both            
              lookup_error = 'User with that email or link name not found.'            
            else:
              # email was not provided, so look up failure is due to link name            
              lookup_error = 'User with that link name not found.'            
    # else: form was not valid
  # else:  # method == 'GET'

  if user:
    # User entity found, so populate form with existing User information            
    # context['found_user'] = user
    form = LookupForm(initial={'id': user.id,
                               'link_name': user.link_name})

    if request.path.endswith('lookup'):
      # convert /lookup path into /profile/link_name path
      edit_link = '%sprofile/%s' % (request.path[:-len('lookup')],
                                    user.link_name) 
    # else: URL is not one that was expected, so do not display edit link
  elif not form:
    # no pre-populated form was constructed, so show the empty look-up form
    form = LookupForm()

  context.update({'form': form,
                  'edit_link': edit_link,
                  'found_user': user,
                  'lookup_error': lookup_error,
                  'lookup_message': lookup_message})

  return response_helpers.respond(request, template, context)
