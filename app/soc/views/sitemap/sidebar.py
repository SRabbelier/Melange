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

"""Sidebar
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.views import out_of_band
from soc.views.helper import access

SIDEBAR = []


def addMenu(callback):
  global SIDEBAR
  SIDEBAR.append(callback)

def getSidebar(request):
  sidebar = []

  for callback in SIDEBAR:
    menu = callback(request)
    
    if menu:
      # only if there is a menu we should append it
      sidebar.append(menu)

  return sidebar


def getSidebarItems(params):
  """Retrieves a list of sidebar entries for this view

  Params usage:
    The params dictionary is provided to the menu_text's format.

    sidebar: The sidebar value is returned directly if non-False
    sidebar_defaults: The sidebar_defaults are used to construct the
      sidebar items for this View. It is expected to be a tuple of
      three items, the item's url, it's menu_text, and it's
      access_type, see getSidebarLinks on how access_type is used.
    sidebar_additional: The sidebar_additional values are appended
      to the list of items verbatim, and should be in the format
      expected by getSidebarLinks.

  Args:
    params: a dict with params for this View.
  """

  # Return the found result
  if params['sidebar']:
    return params['sidebar']

  # Construct defaults manualy
  defaults = params['sidebar_defaults']

  result = []

  for url, menu_text, access_type in defaults:
    url = url % params['url_name'].lower()
    item = (url, menu_text % params, access_type)
    result.append(item)

  for item in params['sidebar_additional']:
    result.append(item)

  return result


def getSidebarLinks(request, params=None):
  """Returns an dictionary with one sidebar entry.

  Calls getSidebarItems to retrieve the items that should be in the
  menu. Expected is a tuple with an url, a menu_text, and an
  access_type. The access_type is then passed to checkAccess, if it
  raises out_of_band.Error, the item will not be added.

  Args:
    request: the django request object
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

  Returns: A dictionary is returned with it's 'heading' value set
    as explained above. It's 'items' value is constructed by
    calling _getSidebarItems. It constists of dictionaries with a
    url and a title field.
  """

  rights = params['rights']

  items = []

  for url, menu_text, access_type in getSidebarItems(params):
    try:
      access.checkAccess(access_type, request, rights)
      items.append({'url': url, 'title': menu_text})
    except out_of_band.Error:
      pass

  if not items:
    return

  res = {}

  if 'sidebar_heading' not in params:
    params['sidebar_heading'] = params['name']

  res['heading'] = params['sidebar_heading']
  res['items'] = items

  return res
