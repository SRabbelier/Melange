#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module containing the RequestData object that will be created for each
request in the GSoC module.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users

from soc.logic.models.site import logic as site_logic
from soc.logic.models.user import logic as user_logic


class RequestData(object):
  """Object containing data we query for each request.

  Fields:
    site: the Site entity
    user: the user entity (if logged in)
    request: the request object (as provided by django)
    args: the request args (as provided by djang)
    kwargs: the request kwargs (as provided by django)
    path: the url of the current query, encoded as utf-8 string
    full_path: same as path, but including any GET args
    GET: the GET dictionary (from the request object)
    POST: the POST dictionary (from the request object)
    is_developer: is the current user a developer
    gae_user: the Google Appengine user object
  """

  def __init__(self):
    """Constructs an empty RequestData object.
    """
    self.site = None
    self.user = None
    self.request = None
    self.args = []
    self.kwargs = {}
    self.GET = None
    self.POST = None
    self.is_developer = False
    self.gae_user = None

  def populate(self, redirect, request, args, kwargs):
    """Populates the fields in the RequestData object.

    Args:
      request: Django HTTPRequest object.
      args & kwargs: The args and kwargs django sends along.
    """
    self.redirect = redirect
    self.request = request
    self.args = args
    self.kwargs = kwargs
    self.GET = request.GET
    self.POST = request.POST
    self.path = request.path.encode('utf-8')
    self.full_path = request.get_full_path().encode('utf-8')
    self.site = site_logic.getSingleton()
    self.user = user_logic.getCurrentUser()
    if users.is_current_user_admin():
      self.is_developer = True
    if self.user and self.user.is_developer:
      self.is_developer = True
    self.gae_user = users.get_current_user()
