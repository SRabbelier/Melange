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


from google.appengine.api import users

from django import http
from django import newforms as forms
from django.utils.translation import ugettext_lazy

from soc.logic import models
from soc.logic import out_of_band
from soc.logic import validate
from soc.logic.site import id_user
from soc.views import simple
from soc.views import helper
from soc.views.helper import access
from soc.views.user import profile

import soc.logic
import soc.models.user
import soc.views.helper.forms
import soc.views.helper.lists
import soc.views.helper.requests
import soc.views.helper.responses


class LookupForm(helper.forms.DbModelForm):
  """Django form displayed for a Developer to look up a User.
  
  This form is manually specified, instead of using
    model = soc.models.user.User
  in the Meta class, because the form behavior is unusual and normally
  required Properties of the User model need to sometimes be omitted.
  
  Also, this form only permits entry and editing  of some of the User entity
  Properties, not all of them.
  """
  id = forms.EmailField(required=False,
      label=soc.models.user.User.id.verbose_name,
      help_text=soc.models.user.User.id.help_text)

  link_name = forms.CharField(required=False,
      label=soc.models.user.User.link_name.verbose_name,
      help_text=soc.models.user.User.link_name.help_text)

  class Meta:
    model = None

  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')

    if not link_name:
      # link name not supplied (which is OK), so do not try to validate it
      return None

    if not validate.isLinkNameFormatValid(link_name):
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

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)

  user = None  # assume that no User entity will be found
  form = None  # assume blank form needs to be displayed
  lookup_message = ugettext_lazy('Enter information to look up a User.')
  email_error = None  # assume no email look-up errors

  if request.method == 'POST':
    form = LookupForm(request.POST)

    if form.is_valid():
      form_id = form.cleaned_data.get('id')
      
      if form_id:
        # email provided, so attempt to look up user by email
        user = models.user.logic.getFromFields(id=form_id)

        if user:
          lookup_message = ugettext_lazy('User found by email.')
        else:
          email_error = ugettext_lazy('User with that email not found.')
          range_width = helper.lists.getPreferredListPagination()
          nearest_user_range_start = id_user.findNearestUsersOffset(
              range_width, id=form_id)
            
          if nearest_user_range_start is not None:            
            context['lookup_link'] = './list?offset=%s&limit=%s' % (
                nearest_user_range_start, range_width)
      if not user:
        # user not found yet, so see if link name was provided
        link_name = form.cleaned_data.get('link_name')
        
        if link_name:
          # link name provided, so try to look up by link name 
          user = id_user.getUserFromLinkName(link_name)
        
          if user:
            lookup_message = ugettext_lazy('User found by link name.')
            email_error = None  # clear previous error, since User was found
          else:
            context['link_name_error'] = ugettext_lazy(
                'User with that link name not found.')
            range_width = helper.lists.getPreferredListPagination()
            nearest_user_range_start = id_user.findNearestUsersOffset(
                range_width, link_name=link_name)
            
            if nearest_user_range_start is not None:
              context['lookup_link'] = './list?offset=%s&limit=%s' % (
                  nearest_user_range_start, range_width)
    # else: form was not valid
  # else:  # method == 'GET'

  if user:
    # User entity found, so populate form with existing User information
    # context['found_user'] = user
    form = LookupForm(initial={'id': user.id.email(),
                               'link_name': user.link_name})

    if request.path.endswith('lookup'):
      # convert /lookup path into /profile/link_name path
      context['edit_link'] = helper.requests.replaceSuffix(
          request.path, 'lookup', 'profile/%s' % user.link_name)
    # else: URL is not one that was expected, so do not display edit link
  elif not form:
    # no pre-populated form was constructed, so show the empty look-up form
    form = LookupForm()

  context.update({'form': form,
                  'found_user': user,
                  'email_error': email_error,
                  'lookup_message': lookup_message})

  return helper.responses.respond(request, template, context)


class EditForm(helper.forms.DbModelForm):
  """Django form displayed when Developer edits a User.
  
  This form is manually specified, instead of using
    model = soc.models.user.User
  in the Meta class, because the form behavior is unusual and normally
  required Properties of the User model need to sometimes be omitted.
  """
  id = forms.EmailField(
      label=soc.models.user.User.id.verbose_name,
      help_text=soc.models.user.User.id.help_text)

  link_name = forms.CharField(
      label=soc.models.user.User.link_name.verbose_name,
      help_text=soc.models.user.User.link_name.help_text)

  nick_name = forms.CharField(
      label=soc.models.user.User.nick_name.verbose_name)

  is_developer = forms.BooleanField(required=False,
      label=soc.models.user.User.is_developer.verbose_name,
      help_text=soc.models.user.User.is_developer.help_text)

  key_name = forms.CharField(widget=forms.HiddenInput)
  
  class Meta:
    model = None
 
  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")

    key_name = self.data.get('key_name')
    user = models.user.logic.getFromKeyName(key_name)

    if user and user.link_name != link_name:
      raise forms.ValidationError("This link name is already in use.")

    return link_name

  def clean_id(self):
    form_id = users.User(email=self.cleaned_data.get('id'))
    if not id_user.isIdAvailable(
        form_id, existing_key_name=self.data.get('key_name')):
      raise forms.ValidationError("This account is already in use.")
    return form_id


DEF_SITE_USER_PROFILE_EDIT_TMPL = 'soc/site/user/profile/edit.html'
DEF_CREATE_NEW_USER_MSG = ' You can create a new user by visiting' \
                          ' <a href="/site/user/profile">Create ' \
                          'a New User</a> page.'

def edit(request, link_name=None, template=DEF_SITE_USER_PROFILE_EDIT_TMPL):
  """View for a Developer to modify the properties of a User Model entity.

  Args:
    request: the standard django request object
    link_name: the User's site-unique "link_name" extracted from the URL
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

  user = None  # assume that no User entity will be found

  # try to fetch User entity corresponding to link_name if one exists
  if link_name:
    user = id_user.getUserFromLinkName(link_name)

  if request.method == 'POST':
    form = EditForm(request.POST)

    if form.is_valid():
      key_name = form.cleaned_data.get('key_name')
      new_link_name = form.cleaned_data.get('link_name')

      properties = {}
      properties['id'] = form.cleaned_data.get('id')
      properties['link_name']  = new_link_name
      properties['nick_name']  = form.cleaned_data.get('nick_name')
      properties['is_developer'] = form.cleaned_data.get('is_developer')
      
      user = models.user.logic.updateOrCreateFromKeyName(properties, key_name)

      #raise forms.ValidationError("lesseee: " + new_link_name + " " +  user.link_name)

      if not user:
        return http.HttpResponseRedirect('/')
        
      # redirect to new /site/user/profile/new_link_name?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, link_name, new_link_name,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # try to fetch User entity corresponding to link name if one exists
    if link_name:
      if user:
        # is 'Profile saved' parameter present, but referrer was not ourself?
        # (e.g. someone bookmarked the GET that followed the POST submit) 
        if (request.GET.get(profile.SUBMIT_MSG_PARAM_NAME)
            and (not helper.requests.isReferrerSelf(request,
                                                    suffix=link_name))):
          # redirect to aggressively remove 'Profile saved' query parameter
          return http.HttpResponseRedirect(request.path)
    
        # referrer was us, so select which submit message to display
        # (may display no message if ?s=0 parameter is not present)
        context['notice'] = (
            helper.requests.getSingleIndexedParamValue(
                request, profile.SUBMIT_MSG_PARAM_NAME,
                values=profile.SUBMIT_MESSAGES))

        # populate form with the existing User entity
        form = EditForm(initial={'key_name': user.key().name(),
            'id': user.id.email(), 'link_name': user.link_name,
            'nick_name': user.nick_name, 'is_developer': user.is_developer})
      else:
        if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
          # redirect to aggressively remove 'Profile saved' query parameter
          return http.HttpResponseRedirect(request.path)
          
        context['lookup_error'] = ugettext_lazy(
            'User with that link name not found.')
        form = EditForm(initial={'link_name': link_name})
    else:  # no link name specified in the URL
      if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)

      # no link name specified, so start with an empty form
      form = EditForm()

  context.update({'form': form,
                  'existing_user': user})

  return helper.responses.respond(request, template, context)


class CreateForm(helper.forms.DbModelForm):
  """Django form displayed when Developer creates a User.

  This form is manually specified, instead of using
    model = soc.models.user.User
  in the Meta class, because the form behavior is unusual and normally
  required Properties of the User model need to sometimes be omitted.
  """
  id = forms.EmailField(
      label=soc.models.user.User.id.verbose_name,
      help_text=soc.models.user.User.id.help_text)

  link_name = forms.CharField(
      label=soc.models.user.User.link_name.verbose_name,
      help_text=soc.models.user.User.link_name.help_text)

  nick_name = forms.CharField(
      label=soc.models.user.User.nick_name.verbose_name)

  is_developer = forms.BooleanField(required=False,
      label=soc.models.user.User.is_developer.verbose_name,
      help_text=soc.models.user.User.is_developer.help_text)
  
  class Meta:
    model = None
  
  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    else:
      if id_user.getUserFromLinkName(link_name):
        raise forms.ValidationError("This link name is already in use.")
    return link_name

  def clean_id(self):
    new_email = self.cleaned_data.get('id')
    form_id = users.User(email=new_email)
    if models.user.logic.getFromFields(email=form_id):
        raise forms.ValidationError("This account is already in use.")
    return form_id


DEF_SITE_CREATE_USER_PROFILE_TMPL = 'soc/site/user/profile/edit.html'

def create(request, template=DEF_SITE_CREATE_USER_PROFILE_TMPL):
  """View for a Developer to create a new User Model entity.

  Args:
    request: the standard django request object
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

  if request.method == 'POST':
    form = CreateForm(request.POST)

    if form.is_valid():
      form_id = form.cleaned_data.get('id')
      link_name = form.cleaned_data.get('link_name')

      properties = {
        'id': form_id,
        'link_name': link_name,
        'nick_name': form.cleaned_data.get('nick_name'),
        'is_developer': form.cleaned_data.get('is_developer'),
      }

      user = models.user.logic.updateOrCreateFromFields(properties, email=form_id)

      if not user:
        return http.HttpResponseRedirect('/')

      # redirect to new /site/user/profile/new_link_name?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, None, link_name,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # no link name specified, so start with an empty form
    form = CreateForm()

  context['form'] = form

  return helper.responses.respond(request, template, context)
