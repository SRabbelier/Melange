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

import re

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


class UserForm(forms_helpers.DbModelForm):
  """Django form displayed when creating or editing a User.
  """
  LINKNAME_PATTERN = r'''(?x)
      ^
      [0-9a-z]  # start with ASCII digit or lowercase
      (
      [0-9a-z]  # additional ASCII digit or lowercase
      |         # -OR-
      _[0-9a-z] # underscore and ASCII digit or lowercase
      )*        # zero or more of OR group
      $'''
  LINKNAME_REGEX = re.compile(LINKNAME_PATTERN)
  
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.user.User
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['id']
  
  def clean_link_name(self):
    linkname = self.cleaned_data.get('link_name')
    linkname_user = id_user.getUserFromLinkName(linkname)
    id = users.get_current_user()
    # if linkname exist in datastore and doesn't belong to current user
    if linkname_user and (linkname_user.id != id):
      raise forms.ValidationError("This link name is already in use.")
    elif not self.LINKNAME_REGEX.match(linkname):
      raise forms.ValidationError("This link name is in wrong format.")
    return linkname


DEF_USER_PROFILE_EDIT_TMPL = 'soc/user/profile/edit.html'

def edit(request, linkname=None, template=DEF_USER_PROFILE_EDIT_TMPL):
  """View for a User to modify the properties of a User Model entity.

  Args:
    request: the standard django request object.
    linkname: the User's site-unique "linkname" extracted from the URL
    template: the template path to use for rendering the template.

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
    # show custom 404 page when linkname doesn't exist in Datastore
    return simple.errorResponse(request, error, template, context)
  
  # linkname_user will be None here if linkname was already None...
  if linkname_user and (linkname_user.id != id):
    # linkname_user exists but is not the currently logged in Google Account,
    # so show public view for that (other) User entity
    return simple.public(request, template, linkname, context)

  user = id_user.getUserFromId(id)
  
  if request.method == 'POST':
    form = UserForm(request.POST)

    if form.is_valid():
      linkname = form.cleaned_data.get('link_name')
      nickname = form.cleaned_data.get("nick_name")

      if not user:
        user = soc.models.user.User(id=id, link_name=linkname,
                                    nick_name=nickname)
      else:
        user.nick_name = nickname
        user.link_name = linkname

      user.put()
      # TODO(tlarsen):
      # if old_linkname:  redirect to new /user/profile/new_linkname
      #   (how to preserve displaying the "Profile saved" message?)
      context.update({'submit_message': 'Profile saved.'})
  else: # request.method == 'GET'
    if user:
      # populate form with the existing User entity
      form = UserForm(instance=user)
    else:
      # no User entity exists for this Google Account, so show a blank form
      form = UserForm()

  context.update({'form': form})
  return response_helpers.respond(request, template, context)
