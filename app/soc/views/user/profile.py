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
from django import http
from django import shortcuts
from django import newforms as forms
from django.utils.translation import ugettext_lazy

from soc.logic import validate
from soc.logic import out_of_band
from soc.logic.site import id_user
from soc.views import helpers
import soc.views.helpers.request
from soc.views import simple
from soc.views.helpers import forms_helpers
from soc.views.helpers import response_helpers

import soc.models.user


class UserForm(forms_helpers.DbModelForm):
  """Django form displayed when creating or editing a User.
  """
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.user.User
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['id', 'former_ids', 'is_developer']
  
  def clean_link_name(self):
    link_name = self.cleaned_data.get('link_name')
    if not validate.isLinkNameFormatValid(link_name):
      raise forms.ValidationError("This link name is in wrong format.")
    elif not id_user.isLinkNameAvailableForId(link_name):
      raise forms.ValidationError("This link name is already in use.")
    return link_name


DEF_USER_PROFILE_EDIT_TMPL = 'soc/user/profile/edit.html'

SUBMIT_MSG_PARAM_NAME = 's'

SUBMIT_MESSAGES = (
  ugettext_lazy('Profile saved.'),
)

SUBMIT_MSG_PROFILE_SAVED = 0

SUBMIT_PROFILE_SAVED_PARAMS = {
  SUBMIT_MSG_PARAM_NAME: SUBMIT_MSG_PROFILE_SAVED,
}

def edit(request, linkname=None, template=DEF_USER_PROFILE_EDIT_TMPL):
  """View for a User to modify the properties of a User Model entity.

  Args:
    request: the standard django request object
    linkname: the User's site-unique "linkname" extracted from the URL
    template: the template path to use for rendering the template

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  id = users.get_current_user()

  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)

  if (not id) and (not linkname):
    # not logged in, and no link name, so request that the user sign in 
    return simple.requestLogin(request, template, context,
        # TODO(tlarsen): /user/profile could be a link to a help page instead
        login_message_fmt='To create a new'
                          ' <a href="/user/profile">User Profile</a>'
                          ' or modify an existing one, you must first'
                          ' <a href="%(sign_in)s">sign in</a>.')

  if (not id) and linkname:
    # not logged in, so show read-only public profile for linkname user
    return simple.public(request, template, linkname, context)

  # try to fetch User entity corresponding to linkname if one exists    
  try:
    linkname_user = id_user.getUserIfLinkName(linkname)
  except out_of_band.ErrorResponse, error:
    # show custom 404 page when link name doesn't exist in Datastore
    return simple.errorResponse(request, error, template, context)
  
  # linkname_user will be None here if link name was already None...
  if linkname_user and (linkname_user.id != id):
    # linkname_user exists but is not the currently logged in Google Account,
    # so show public view for that (other) User entity
    return simple.public(request, template, linkname, context)

  if request.method == 'POST':
    form = UserForm(request.POST)

    if form.is_valid():
      new_linkname = form.cleaned_data.get('link_name')
      nickname = form.cleaned_data.get("nick_name")

      user = id_user.updateOrCreateUserFromId(
          id, link_name=new_linkname, nick_name=nickname)

      # redirect to new /user/profile/new_linkname?s=0
      # (causes 'Profile saved' message to be displayed)
      return response_helpers.redirectToChangedSuffix(
          request, linkname, new_linkname, params=SUBMIT_PROFILE_SAVED_PARAMS)
  else: # request.method == 'GET'
    # try to fetch User entity corresponding to Google Account if one exists    
    user = id_user.getUserFromId(id)

    if user:
      # is 'Profile saved' parameter present, but referrer was not ourself?
      # (e.g. someone bookmarked the GET that followed the POST submit) 
      if (request.GET.get(SUBMIT_MSG_PARAM_NAME)
          and (not helpers.request.isReferrerSelf(request,
                                                  suffix=linkname))):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)
    
      # referrer was us, so select which submit message to display
      # (may display no message if ?s=0 parameter is not present)
      context['submit_message'] = (
          helpers.request.getSingleIndexedParamValue(
              request, SUBMIT_MSG_PARAM_NAME, values=SUBMIT_MESSAGES))

      # populate form with the existing User entity
      form = UserForm(instance=user)
    else:
      if request.GET.get(SUBMIT_MSG_PARAM_NAME):
        # redirect to aggressively remove 'Profile saved' query parameter
        return http.HttpResponseRedirect(request.path)

      # no User entity exists for this Google Account, so show a blank form
      form = UserForm()

  context.update({'form': form})
  return response_helpers.respond(request, template, context)
