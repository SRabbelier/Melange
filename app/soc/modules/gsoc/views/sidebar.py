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

"""This module contains sidebar view."""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
]


from google.appengine.api import users

from soc.modules.gsoc.views.helper import redirects
 

# TODO: this is a draft version of the class. It will be changed due to
# some further decisions on how the views should look like
class Sidebar(object):
  """Sidebar view.
  """

  def getSidearContext(self, request):
    """Generates URL links for the hard-coded GSoC sidebar items.
    """

    context = {}

    # get login link
    context['login_link'] = users.create_login_url(
        request.path.encode('utf-8'))

    # get logout link
    context['logout_link'] = users.create_logout_url(
        request.path.encode('utf-8'))

    # get about link
    context['about'] = redirects.getAboutPageRedirect()

    # get projects link
    context['projects'] = redirects.getAllProjectsRedirect()

    # get events link
    context['events'] = redirects.getEventsRedirect()

    # get connect link
    context['connect'] = redirects.getConnectRedirect()

    # get help link
    context['help'] = redirects.getHelpRedirect()

    return context
