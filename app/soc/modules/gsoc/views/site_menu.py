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

"""This module contains the view for the site menus."""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
]


from google.appengine.api import users

from soc.views.template import Template

from soc.modules.gsoc.views.helper import redirects


def siteMenuContext(data):
  """Generates URL links for the hard-coded GSoC site menu items.
  """


  context = {
      'about_link': redirects.getAboutPageRedirect(data),
      'projects_link': redirects.getAllProjectsRedirect(data),
      'events_link': redirects.getEventsRedirect(data),
      'connect_link': redirects.getConnectRedirect(data),
      'help_link': redirects.getHelpRedirect(data),
  }

  if users.get_current_user():
    context['logout_link'] = users.create_logout_url(self.data.full_path)
  else:
    context['login_link'] = users.create_login_url(self.data.full_path)

  if data.role:
    context['dashboard_link'] = redirects.getDashboardRedirect(data)

  return context

class MainMenu(Template):
  """MainMenu template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    return siteMenuContext(self.data)

  def templatePath(self):
    return "v2/modules/gsoc/mainmenu.html"


class Footer(Template):
  """Footer template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    context = siteMenuContext(self.data)

    program = self.data.program
    if program:
      context.update({
          'privacy_policy_url': redirects.getPrivacyPolicyRedirect(self.data),
          'facebook_url': program.facebook,
          'twitter_url': program.twitter,
          'blogger_url': program.blogger,
          'email_id': program.email,
          'irc_url': program.irc,
          })

    return context

  def templatePath(self):
    return "v2/modules/gsoc/footer.html"
