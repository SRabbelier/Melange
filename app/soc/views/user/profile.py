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

"""Views for editing and examining User profiles.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django import http
from django.utils.translation import ugettext_lazy

from soc.logic import accounts
from soc.logic import models
from soc.logic import out_of_band
from soc.logic import validate
from soc.views import helper
from soc.views import simple
from soc.views.helper import decorators

import soc.logic
import soc.models.user
import soc.views.helper.forms
import soc.views.helper.requests
import soc.views.helper.responses


class UserForm(helper.forms.BaseForm):
  """Django form displayed when creating or editing a User.
  """
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.user.User
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['account', 'former_accounts', 'is_developer']
  
  def clean_link_id(self):
    link_id = self.cleaned_data.get('link_id')
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")

    user = models.user.logic.getForFields({'link_id': link_id},
                                          unique=True)
    
    # Get the currently logged in user account
    current_account = users.get_current_user()
    
    if user:
      if current_account != user.account:
        raise forms.ValidationError("This link ID is already in use.")

    return link_id


DEF_USER_PROFILE_EDIT_TMPL = 'soc/user/edit_self.html'
DEF_USER_ACCOUNT_INVALID_MSG = 'This account is invalid.'

SUBMIT_MSG_PARAM_NAME = 's'

SUBMIT_MESSAGES = (
  ugettext_lazy('Profile saved.'),
)

SUBMIT_MSG_PROFILE_SAVED = 0

SUBMIT_PROFILE_SAVED_PARAMS = {
  SUBMIT_MSG_PARAM_NAME: SUBMIT_MSG_PROFILE_SAVED,
}

@decorators.view
def edit(request, page_name=None, link_id=None, 
         template=DEF_USER_PROFILE_EDIT_TMPL):
  """View for a User to modify the properties of a User Model entity.

  Args:
    request: the standard django request object
    page_name: the page name displayed in templates as page and header title
    link_id: the User's site-unique "link_id" extracted from the URL
    template: the template path to use for rendering the template

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  account = users.get_current_user()
  
  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)

  if (not account) and (not link_id):
    # not logged in, and no link ID, so request that the user sign in 
    return simple.requestLogin(request, page_name, template, context,
        # TODO(tlarsen): /user/profile could be a link to a help page instead
        login_message_fmt=ugettext_lazy(
            'To create a new <a href="/user/profile">User Profile</a>'
            ' or modify an existing one, you must first'
            ' <a href="%(sign_in)s">sign in</a>.'))

  if (not account) and link_id:
    # not logged in, so show read-only public profile for link_id user
    return simple.public(request, page_name=page_name, template=template, 
                         link_id=link_id, context=context)

  link_id_user = None

  # try to fetch User entity corresponding to link_id if one exists
  try:
    if link_id:
      link_id_user = accounts.getUserFromLinkIdOr404(link_id)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link ID doesn't exist in Datastore
    return simple.errorResponse(request, page_name, error, template, context)
  
  # link_id_user will be None here if link ID was already None...
  if link_id_user and (link_id_user.account != account):
    # link_id_user exists but is not the currently logged in Google Account,
    # so show public view for that (other) User entity
    return simple.public(request, page_name=page_name, template=template, 
                         link_id=link_id, context=context)

  if request.method == 'POST':
    form = UserForm(request.POST)

    if form.is_valid():
      new_link_id = form.cleaned_data.get('link_id')
      properties = {
        'link_id': new_link_id,
        'nick_name': form.cleaned_data.get("nick_name"),
        'account': account,
      }

      # check if user account is not in former_accounts
      # if it is show error message that account is invalid
      if models.user.logic.isFormerAccount(account):
        msg = DEF_USER_ACCOUNT_INVALID_MSG
        error = out_of_band.ErrorResponse(msg)
        return simple.errorResponse(request, page_name, error, template, context)
      
      user = models.user.logic.updateOrCreateFromFields(properties, {'link_id': new_link_id})
      
      # redirect to /user/profile?s=0
      # (causes 'Profile saved' message to be displayed)
      return helper.responses.redirectToChangedSuffix(
          request, None, params=SUBMIT_PROFILE_SAVED_PARAMS)
  else: # request.method == 'GET'
    # try to fetch User entity corresponding to Google Account if one exists
    user = models.user.logic.getForFields({'account': account}, unique=True)

    if user:
      # is 'Profile saved' parameter present, but referrer was not ourself?
      # (e.g. someone bookmarked the GET that followed the POST submit) 
      if (request.GET.get(SUBMIT_MSG_PARAM_NAME)
          and (not helper.requests.isReferrerSelf(request,
                                                  suffix=link_id))):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)
    
      # referrer was us, so select which submit message to display
      # (may display no message if ?s=0 parameter is not present)
      context['notice'] = (
          helper.requests.getSingleIndexedParamValue(
              request, SUBMIT_MSG_PARAM_NAME, values=SUBMIT_MESSAGES))

      # populate form with the existing User entity
      form = UserForm(instance=user)
    else:
      if request.GET.get(SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)

      # no User entity exists for this Google Account, so show a blank form
      form = UserForm()

  context['form'] = form
  return helper.responses.respond(request, template, context)


@decorators.view
def create(request, page_name=None, template=DEF_USER_PROFILE_EDIT_TMPL):
  """create() view is same as edit() view, but with no link_id supplied.
  """
  return edit(request, page_name=page_name, link_id=None, template=template)