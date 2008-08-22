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
    current_id = users.get_current_user()
    # if linkname exist in datastore and doesn't belong to current user
    if linkname_user and (linkname_user.id != current_id):
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
  
  #TODO(solydzajs): use makeSiblingTemplatePath from templates_helpers and pass
  #                 result to public view
  
  # TODO: use something like the code below, define global public tmpl 
  # template_choices = [makeSiblingTemplatePath(template, 'public.html'),
  # DEF_USER_PROFILE_PUBLIC_TMPL])
  # public(request, linkname=linkname, template=template_choices)
  
  #: If user not signed and there is no linkname redirect to sign-in page
  #: otherwise show public profile for linkname user
  current_id = users.get_current_user()
  if not current_id and not linkname:
    return http.HttpResponseRedirect(users.create_login_url(request.path))
  elif not current_id and linkname:
    return public(request, linkname)
    
  user = soc.models.user.User.getUserForId(current_id)
  
  #: Show custom 404 page when linkname doesn't exist in datastore
  #: or show public view for linkname user
  if linkname:
    linkname_user = soc.models.user.User.getUserForLinkname(linkname)
    if not linkname_user:
      return http.HttpResponseNotFound('No user exists with that link name "%s"' %
                                linkname)
    elif linkname_user and (linkname_user.id != current_id):
      return public(request, linkname)

  #: GET method
  if (request.method != 'POST') and user:
    form = UserForm(initial={'nick_name': user.nick_name,
                             'link_name': user.link_name})
    return response_helpers.respond(request,
        template, {'template': template, 
                   'form': form, 
                   'user': user})
  
  #: POST method
  form = UserForm()
  if request.method == 'POST':
    form = UserForm(request.POST)

    if form.is_valid():
      linkname = form.cleaned_data.get('link_name')
      nickname = form.cleaned_data.get("nick_name")
      if not user:
        user = soc.models.user.User(id = user,link_name = linkname,
                                        nick_name = nickname)
      else:
        user.nick_name = nickname
        user.link_name = linkname
      user.put()
      return response_helpers.respond(request,
              template, {'template': template, 
                         'form': form, 
                         'user': user,
                         'submit_message': 'Profile saved.'})

  return response_helpers.respond(request,
      template, {'template': template, 'form': form})


def public(request, linkname=None,
           template='soc/user/profile/public.html'):
  """A "general public" view of a User on the site.

  Args:
    request: the standard django request object.
    linkname: the User's site-unique "linkname" extracted from the URL
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  #: If linkname is empty or not a valid linkname on the site, display
  #: "user does not exist", otherwise render public view for linkname user
  if linkname:
    linkname_user = soc.models.user.User.getUserForLinkname(linkname)
    if not linkname_user:
      return http.HttpResponseNotFound('No user exists with that link name "%s"' %
                                linkname)
    else:
      return response_helpers.respond(request, 
          template, {'template': template,
                     'user': linkname_user})
      
  return http.HttpResponseNotFound('No user exists with that link name "%s"' %
                            linkname)
