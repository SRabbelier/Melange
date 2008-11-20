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

from django import forms
from django import http
from django.utils.translation import ugettext_lazy

from soc.logic import accounts
from soc.logic import models
from soc.logic import out_of_band
from soc.logic import validate
from soc.views import simple
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.user import profile

import soc.logic
import soc.models.user
import soc.views.helper.forms
import soc.views.helper.lists
import soc.views.helper.requests
import soc.views.helper.responses


class LookupForm(helper.forms.BaseForm):
  """Django form displayed for a Developer to look up a User.
  
  This form is manually specified, instead of using
    model = soc.models.user.User
  in the Meta class, because the form behavior is unusual and normally
  required Properties of the User model need to sometimes be omitted.
  
  Also, this form only permits entry and editing  of some of the User entity
  Properties, not all of them.
  """
  account = forms.EmailField(required=False,
      label=soc.models.user.User.account.verbose_name,
      help_text=soc.models.user.User.account.help_text)

  link_id = forms.CharField(required=False,
      label=soc.models.user.User.link_id.verbose_name,
      help_text=soc.models.user.User.link_id.help_text)

  class Meta:
    model = None

  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')

    if not link_id:
      # link ID not supplied (which is OK), so do not try to validate it
      return None

    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError('This link ID is in wrong format.')
    
    return link_id

  def clean_account(self):
    email = self.cleaned_data.get('account')
    
    if not email:
      # email not supplied (which is OK), so do not try to convert it
      return None
  
    try:
      return users.User(email=email)
    except users.UserNotFoundError:
      raise forms.ValidationError('Account not found.')
    

DEF_SITE_USER_PROFILE_LOOKUP_TMPL = 'soc/user/lookup.html'

@decorators.view
def lookup(request, page_name=None, template=DEF_SITE_USER_PROFILE_LOOKUP_TMPL):
  """View for a Developer to look up a User Model entity.

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
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  user = None  # assume that no User entity will be found
  form = None  # assume blank form needs to be displayed
  lookup_message = ugettext_lazy('Enter information to look up a User.')
  email_error = None  # assume no email look-up errors
  context['lookup_link'] = None

  if request.method == 'POST':
    form = LookupForm(request.POST)

    if form.is_valid():
      form_account = form.cleaned_data.get('account')
      
      if form_account:
        # email provided, so attempt to look up user by email
        user = models.user.logic.getForFields(
            {'account': form_account}, unique=True)

        if user:
          lookup_message = ugettext_lazy('User found by email.')
        else:
          email_error = ugettext_lazy('User with that email not found.')
          range_width = helper.lists.getPreferredListPagination()
          nearest_user_range_start = (
              models.user.logic.findNearestEntitiesOffset(
                  width, [('account', form_account)]))
            
          if nearest_user_range_start is not None:            
            context['lookup_link'] = './list?offset=%s&limit=%s' % (
                nearest_user_range_start, range_width)
      if not user:
        # user not found yet, so see if link ID was provided
        link_id = form.cleaned_data.get('link_id')
        
        if link_id:
          # link ID provided, so try to look up by link ID 
          user = models.user.logic.getForFields({'link_id': link_id},
                                                unique=True)        
          if user:
            lookup_message = ugettext_lazy('User found by link ID.')
            # clear previous error, since User was found
            email_error = None
            # clear previous lookup_link, since User was found, the lookup_link
            # is not needed to display.
            context['lookup_link'] = None
          else:
            context['link_id_error'] = ugettext_lazy(
                'User with that link ID not found.')
            if context['lookup_link'] is None:
              range_width = helper.lists.getPreferredListPagination()
              nearest_user_range_start = (
                models.user.logic.findNearestEntitiesOffset(
                    width, [('link_id', link_id)]))
            
              if nearest_user_range_start is not None:
                context['lookup_link'] = './list?offset=%s&limit=%s' % (
                    nearest_user_range_start, range_width)
    # else: form was not valid
  # else:  # method == 'GET'

  if user:
    # User entity found, so populate form with existing User information
    # context['found_user'] = user
    form = LookupForm(initial={'account': user.account.email(),
                               'link_id': user.link_id})

    if request.path.endswith('lookup'):
      # convert /lookup path into /profile/link_id path
      context['edit_link'] = helper.requests.replaceSuffix(
          request.path, 'lookup', 'profile/%s' % user.link_id)
    # else: URL is not one that was expected, so do not display edit link
  elif not form:
    # no pre-populated form was constructed, so show the empty look-up form
    form = LookupForm()

  context.update({'form': form,
                  'found_user': user,
                  'email_error': email_error,
                  'lookup_message': lookup_message})

  return helper.responses.respond(request, template, context)


class EditForm(helper.forms.BaseForm):
  """Django form displayed when Developer edits a User.
  
  This form is manually specified, instead of using
    model = soc.models.user.User
  in the Meta class, because the form behavior is unusual and normally
  required Properties of the User model need to sometimes be omitted.
  """
  account = forms.EmailField(
      label=soc.models.user.User.account.verbose_name,
      help_text=soc.models.user.User.account.help_text)

  link_id = forms.CharField(
      label=soc.models.user.User.link_id.verbose_name,
      help_text=soc.models.user.User.link_id.help_text)

  nick_name = forms.CharField(
      label=soc.models.user.User.nick_name.verbose_name)

  is_developer = forms.BooleanField(required=False,
      label=soc.models.user.User.is_developer.verbose_name,
      help_text=soc.models.user.User.is_developer.help_text)

  key_name = forms.CharField(widget=forms.HiddenInput)
  
  class Meta:
    model = None
 
  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")

    key_name = self.data.get('key_name')
    if key_name:
      key_name_user = user_logic.logic.getFromKeyName(key_name)

      if link_id_user and key_name_user and \
          link_id_user.account != key_name_user.account:
        raise forms.ValidationError("This link ID is already in use.")

    return link_id

  def clean_account(self):
    form_account = users.User(email=self.cleaned_data.get('account'))
    if not accounts.isAccountAvailable(
        form_account, existing_key_name=self.data.get('key_name')):
      raise forms.ValidationError("This account is already in use.")
    if models.user.logic.isFormerAccount(form_account):
      raise forms.ValidationError("This account is invalid. "
          "It exists as a former account.")
    return form_account


DEF_SITE_USER_PROFILE_EDIT_TMPL = 'soc/user/edit.html'
DEF_CREATE_NEW_USER_MSG = ' You can create a new user by visiting' \
                          ' <a href="/site/user/profile">Create ' \
                          'a New User</a> page.'

@decorators.view
def edit(request, page_name=None, link_id=None,
         template=DEF_SITE_USER_PROFILE_EDIT_TMPL):
  """View for a Developer to modify the properties of a User Model entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    link_id: the User's site-unique "link_id" extracted from the URL
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

  user = None  # assume that no User entity will be found

  # try to fetch User entity corresponding to link_id if one exists
  try:
    if link_id:
      user = accounts.getUserFromLinkIdOr404(link_id)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link ID doesn't exist in Datastore
    error.message = error.message + DEF_CREATE_NEW_USER_MSG
    return simple.errorResponse(request, page_name, error, template, context)


  if request.method == 'POST':
    form = EditForm(request.POST)

    if form.is_valid():
      key_name = form.cleaned_data.get('key_name')
      new_link_id = form.cleaned_data.get('link_id')

      properties = {}
      properties['account'] = form.cleaned_data.get('account')
      properties['link_id']  = new_link_id
      properties['nick_name']  = form.cleaned_data.get('nick_name')
      properties['is_developer'] = form.cleaned_data.get('is_developer')
      
      user = models.user.logic.updateOrCreateFromKeyName(properties, key_name)

      if not user:
        return http.HttpResponseRedirect('/')
        
      # redirect to new /site/user/profile/new_link_id?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, link_id, new_link_id,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # try to fetch User entity corresponding to link ID if one exists
    if link_id:
      if user:
        # is 'Profile saved' parameter present, but referrer was not ourself?
        # (e.g. someone bookmarked the GET that followed the POST submit) 
        if (request.GET.get(profile.SUBMIT_MSG_PARAM_NAME)
            and (not helper.requests.isReferrerSelf(request,
                                                    suffix=link_id))):
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
            'account': user.account.email(), 'link_id': user.link_id,
            'nick_name': user.nick_name, 'is_developer': user.is_developer})
      else:
        if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
          # redirect to aggressively remove 'Profile saved' query parameter
          return http.HttpResponseRedirect(request.path)
          
        context['lookup_error'] = ugettext_lazy(
            'User with that link ID not found.')
        form = EditForm(initial={'link_id': link_id})
    else:  # no link ID specified in the URL
      if request.GET.get(profile.SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)

      # no link ID specified, so start with an empty form
      form = EditForm()

  context.update({'form': form,
                  'existing_user': user})

  return helper.responses.respond(request, template, context)


class CreateForm(helper.forms.BaseForm):
  """Django form displayed when Developer creates a User.

  This form is manually specified, instead of using
    model = soc.models.user.User
  in the Meta class, because the form behavior is unusual and normally
  required Properties of the User model need to sometimes be omitted.
  """
  account = forms.EmailField(
      label=soc.models.user.User.account.verbose_name,
      help_text=soc.models.user.User.account.help_text)

  link_id = forms.CharField(
      label=soc.models.user.User.link_id.verbose_name,
      help_text=soc.models.user.User.link_id.help_text)

  nick_name = forms.CharField(
      label=soc.models.user.User.nick_name.verbose_name)

  is_developer = forms.BooleanField(required=False,
      label=soc.models.user.User.is_developer.verbose_name,
      help_text=soc.models.user.User.is_developer.help_text)
  
  class Meta:
    model = None
  
  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
    else:
      if models.user.logic.getForFields({'link_id': link_id},
                                        unique=True):
        raise forms.ValidationError("This link ID is already in use.")
    return link_id

  def clean_account(self):
    new_email = self.cleaned_data.get('account')
    form_account = users.User(email=new_email)
    if models.user.logic.getForFields({'account': form_account}, unique=True):
      raise forms.ValidationError("This account is already in use.")
    if models.user.logic.isFormerAccount(form_account):
      raise forms.ValidationError("This account is invalid. "
          "It exists as a former account.")
    return form_account


DEF_SITE_CREATE_USER_PROFILE_TMPL = 'soc/user/edit.html'

@decorators.view
def create(request, page_name=None, template=DEF_SITE_CREATE_USER_PROFILE_TMPL):
  """View for a Developer to create a new User Model entity.

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
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page_name'] = page_name

  if request.method == 'POST':
    form = CreateForm(request.POST)

    if form.is_valid():
      form_account = form.cleaned_data.get('account')
      link_id = form.cleaned_data.get('link_id')

      properties = {
        'account': form_account,
        'link_id': link_id,
        'nick_name': form.cleaned_data.get('nick_name'),
        'is_developer': form.cleaned_data.get('is_developer'),
      }

      key_fields = {'email': form_account.email()}
      user = models.user.logic.updateOrCreateFromFields(properties,
                                                        key_fields)

      if not user:
        return http.HttpResponseRedirect('/')

      # redirect to new /site/user/profile/new_link_id?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, 'create', 'edit/' + link_id,
          params=profile.SUBMIT_PROFILE_SAVED_PARAMS)
  else: # method == 'GET':
    # no link ID specified, so start with an empty form
    form = CreateForm()

  context['form'] = form

  return helper.responses.respond(request, template, context)