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


def siteMenuContext(data):
  """Generates URL links for the hard-coded GSoC site menu items.
  """
  redirect = data.redirect

  context = {
      'about_link': redirect.document(data.program.about_page).url(),
      'events_link': redirect.document(data.program.events_page).url(),
      'connect_link': redirect.document(
          data.program.connect_with_us_page).url(),
      'help_link': redirect.document(data.program.help_page).url(),
  }

  if users.get_current_user():
    context['logout_link'] = redirect.logout().url()
  else:
    context['login_link'] = redirect.login().url()

  if data.profile:
    context['dashboard_link'] = redirect.dashboard().url()

  if data.timeline.studentsAnnounced():
    context['projects_link'] = redirect.allProjects().url()

  return context


class Header(Template):
  """MainMenu template.
  """

  def __init__(self, data):
    self.data = data

  def templatePath(self):
    return "v2/modules/gsoc/header.html"

  def context(self):
    return {
        'home_link': self.data.redirect.homepage().url()
    }


class MainMenu(Template):
  """MainMenu template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    context = siteMenuContext(self.data)
    context.update({
        'home_link': self.data.redirect.homepage().url()
    })
    return context

  def templatePath(self):
    return "v2/modules/gsoc/mainmenu.html"


class Footer(Template):
  """Footer template.
  """

  def __init__(self, data):
    self.data = data

  def context(self):
    context = siteMenuContext(self.data)
    redirect = self.data.redirect

    program = self.data.program
    context.update({
        'privacy_policy_url': redirect.document(program.privacy_policy).url(),
        'facebook_url': program.facebook,
        'twitter_url': program.twitter,
        'blogger_url': program.blogger,
        'email_id': program.email,
        'irc_url': program.irc,
        })

    return context

  def templatePath(self):
    return "v2/modules/gsoc/footer.html"
