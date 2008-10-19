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

"""Site-wide sidebar menu creation.

"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users

from soc.logic import menu
from soc.logic.site import id_user
from soc.logic.site import map


def buildUserSidebar(id=None, **ignored):
  """Returns a list of menu items for the User portion of the sidebar.
  
  Args:
    id: a Google Account (users.User) object; default is None, in which
      case users.get_current_user() is called 
    **ignored: other keyword arguments supplied to other sidebar builder
      functions, but ignored by this one
  """
  if id is None:
    id = users.get_current_user()

  if not id:
    return [map.user_signin.makeMenuItem()]

  return [map.user_signout.makeMenuItem()]


def buildSiteSidebar(is_admin=None, **ignored):
  """Returns a list of menu items for the Developer portion of the sidebar.
  
  Args:
    is_admin: Boolean indicating that current user is a "Developer"
      (site super-user); default is None, in which case
      id_user.isIdDeveloper() is called 
    **ignored: other keyword arguments supplied to other sidebar builder
      functions, but ignored by this one
  """
  if is_admin is None:
    is_admin = id_user.isIdDeveloper()

  if not is_admin:
    # user is either not logged in or not a "Developer", so return no menu
    return None

  return [map.site_settings_edit.makeMenuItem()]


def buildProgramsSidebar(**unused):
  """Mock-up for Programs section of sidebar menu.
  
  Args:
    **unused: all keyword arguments are currently unused in this mock-up
  
  TODO: actually implement this once Program entities are present in the
    Datastore.
  """
  return [
    menu.MenuItem(
      'Google Summer of Code',
      value='/program/gsoc2009/home',
      sub_menu=menu.Menu(items=[
        menu.MenuItem(
          'Community',
          value='/program/gsoc2009/community'),
        menu.MenuItem(
          'FAQs',
          value='/program/gsoc2009/docs/faqs'),
        menu.MenuItem(
          'Terms of Service',
          value='/program/gsoc2009/docs/tos'),
        ]
      )
    ),
    menu.MenuItem(
      'Google Highly Open Participation',
      value='/program/ghop2008/home',
      sub_menu=menu.Menu(items=[
        menu.MenuItem(
          'Community',
          value='/program/ghop2008/community'),
        menu.MenuItem(
          'FAQs',
          value='/program/ghop2008/docs/faqs'),
        menu.MenuItem(
          'Contest Rules',
          value='/program/ghop2008/docs/rules'),
        ]
      )
    ),
  ]
  

DEF_SIDEBAR_BUILDERS = [
  buildUserSidebar,
  buildSiteSidebar,
  buildProgramsSidebar,
]

def buildSidebar(path=None, builders=DEF_SIDEBAR_BUILDERS, **builder_args):
  """Calls all sidebar builders to construct the sidebar menu.

  Args:
    builders: list of functions that take context as a single
      argument; default is the list of sidebar builder functions present
      in soc.logic.site.sidebar
    **builder_args: keyword arguments passed to each sidebar builder function
      
  Returns:
    an soc.logic.menu.Menu object containing the sidebar menu items 
  """
  menu_items = []

  # call each of the sidebar builders and append any menu items they create
  for builder in builders:
    built_items = builder(**builder_args)
    
    if built_items:
      menu_items.extend(built_items)

  # try to determine which of the menu items is the current path, to indicate
  # that it is "selected"
  if not path:
    # path argument not supplied, so see if an HTTP request object was
    # supplied in the builder_args
    request = builder_args.get('request')

    if request:
      # there is an HTTP request object, so use the path stored in it
      path = request.path

  if path:
    # TODO(tlarsen): scan through list and mark current request.path 
    # as "selected"
    pass

  return menu.Menu(items=menu_items)    
