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

"""Views relevant to the User role.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]

import re

from google.appengine.api import users
from django import http
from django import shortcuts
from django import newforms as forms

from soc.views.helpers import forms_helpers
from soc.views.helpers import response_helpers

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
    linkname_user = soc.models.user.User.getUserForLinkname(linkname)
    user = users.get_current_user()
    # if linkname exist in datastore and doesn't belong to current user
    if linkname_user and (linkname_user.id != user):
      raise forms.ValidationError("This link name is already in use.")
    elif not self.LINKNAME_REGEX.match(linkname):
      raise forms.ValidationError("This link name is in wrong format.")
    return linkname


def edit(request, linkname=None, template='soc/user/profile/edit.html'):
  """View for a User to modify the properties of a UserModel.

  Args:
    request: the standard django request object.
    linkname: the User's site-unique "linkname" extracted from the URL
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  #TODO(solydzajs): create controller for User and cleanup code in this handler
  
  #: If user not signed in redirect to sign-in page
  user = users.get_current_user()
  if not user:
    return http.HttpResponseRedirect(users.create_login_url(request.path))

  soc_user = soc.models.user.User.getUser(user)
  
  #: Show custom 404 page when linkname in url doesn't match current user
  if linkname:
    linkname_user = soc.models.user.User.getUserForLinkname(linkname)
    if (linkname_user and linkname_user.id != user) or not linkname_user:
      return http.HttpResponseNotFound('No user exists with that link name "%s"' %
                                linkname)

  #: GET method
  if (request.method != 'POST') and soc_user:
    form = UserForm(initial={'nick_name': soc_user.nick_name,
                             'link_name': soc_user.link_name})
    return response_helpers.respond(request,
        template, {'template': template, 
                   'form': form, 
                   'soc_nick_name': soc_user.nick_name})
  
  #: POST method
  form = UserForm()
  if request.method == 'POST':
    form = UserForm(request.POST)

    if form.is_valid():
      linkname = form.cleaned_data.get('link_name')
      nickname = form.cleaned_data.get("nick_name")
      if not soc_user:
        soc_user = soc.models.user.User(id = user,link_name = linkname,
                                        nick_name = nickname)
      else:
        soc_user.nick_name = nickname
        soc_user.link_name = linkname
      soc_user.put()
      return response_helpers.respond(request,
              template, {'template': template, 
                        'form': form, 
                        'soc_nick_name': nickname,
                        'submit_message': 'Profile saved.'})

  return response_helpers.respond(request,
      template, {'template': template, 'form': form})
