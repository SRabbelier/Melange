#!/usr/bin/python2.5
#
# Copyright 2009 the Melange authors.
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

"""Module contains sidebar related functions.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import operator

from soc.views import out_of_band
from soc.views.helper import access

import soc.cache.sidebar


SIDEBAR = []
SIDEBAR_ACCESS_ARGS = ['SIDEBAR_CALLING']
SIDEBAR_ACCESS_KWARGS = {'SIDEBAR_CALLING': True}


def addMenu(callback):
  """Adds a callback to the menu builder.

  The callback should return a list of menu's when called.
  """

  global SIDEBAR
  SIDEBAR.append(callback)


@soc.cache.sidebar.cache
def getSidebar(id, user):
  """Constructs a sidebar for the current user.
  """

  sidebar = []

  for callback in SIDEBAR:
    menus = callback(id, user)

    for menu in (menus if menus else []):
      sidebar.append(menu)

  return sorted(sidebar, key=lambda x: x.get('group'))


def getSidebarItems(params):
  """Retrieves a list of sidebar entries for this view.

  Params usage:
    The params dictionary is provided to the menu_text's format.

    sidebar: The sidebar value is returned directly if non-False
    sidebar_defaults: The sidebar_defaults are used to construct the
      sidebar items for this View. It is expected to be a tuple of
      three items, the item's url, it's menu_text, and it's
      access_type, see getSidebarMenus on how access_type is used.
    sidebar_additional: The sidebar_additional values are appended
      to the list of items verbatim, and should be in the format
      expected by getSidebarMenus.

  Args:
    params: a dict with params for this View.
  """

  # Return the found result
  if params['sidebar']:
    default = params['sidebar']
    result = default[:]
    for item in params['sidebar_additional']:
      result.append(item)
    return result

  # Construct defaults manualy
  defaults = params['sidebar_defaults']

  result = []

  for item in params['sidebar_additional']:
    result.append(item)

  for url, menu_text, access_type in defaults:
    url = url % params['url_name'].lower()
    item = (url, menu_text % params, access_type)
    result.append(item)

  return result


def getSidebarMenu(id, user, items, params):
  """Returns an dictionary with one sidebar entry.

  Items is expected to be a tuple with an url, a menu_text, and an
  access_type. The access_type is then passed to checkAccess, if it
  raises out_of_band.Error, the item will not be added.

  Args:
    items: see above
    params: a dict with params for this View

  Params usage:
    The params dictionary is passed as argument to getSidebarItems,
    see the docstring of getSidebarItems on how it uses it.

    rights: The rights dictionary is used to check if the user has
      the required rights to see a sidebar item.
      See checkAccess for more details on how the rights dictionary
      is used to check access rights.
    sidebar_heading: The sidebar_heading value is used to set the
      heading variable in the result.
    name: The name value is used if sidebar_heading is not present.

  Returns: 
    A dictionary is returned with it's 'heading' value set as explained above.
    It's 'items' value is constructed by calling _getSidebarItems. It constists
    of dictionaries with a url and a title field.
  """

  rights = params['rights']

  submenus = []

  args = SIDEBAR_ACCESS_ARGS
  kwargs = SIDEBAR_ACCESS_KWARGS

  # reset and pre-fill the Checker's cache
  rights.setCurrentUser(id, user)

  for url, menu_text, access_type in items:
    try:
      rights.checkAccess(access_type, kwargs)
      submenus.append({'url': url, 'title': menu_text})
    except out_of_band.Error:
      pass

  return submenus


def getSidebarMenus(id, user, params=None):
  """Constructs the default sidebar menu for a View.

  Calls getSidebarItems to retrieve the items that should be in the
  menu. Then passes the result to getSidebarMenu. See the respective
  docstrings for an explanation on what they do.

  Args:
    params: a dict with params for this View
  """

  items = getSidebarItems(params)
  submenus = getSidebarMenu(id, user, items, params)

  if not submenus:
    return

  menu = {}

  if 'sidebar_heading' not in params:
    params['sidebar_heading'] = params['name']

  menu['heading'] = params['sidebar_heading']
  menu['items'] = submenus
  menu['group'] = params['sidebar_grouping']

  menus = [menu]

  return menus
