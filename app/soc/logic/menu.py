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

"""Representations and manipulation of arbitrarily nested menus.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users

from django.utils import datastructures


class Menu:
  """Ordered collection of MenuItem objects.
  
  MenuItems are retrievable as an ordered list or individually by their
  MenuItem.text key.
  """
  
  def __init__(self, items=None):
    """Initializes ordered list of MenuItems.
    
    Args:
      items: list of MenuItem objects in display order
    """
    if not items:
      items = []
    
    items = [(i.name, i) for i in items]
    self._items = datastructures.SortedDict(data=items)

  def getItem(self, name):
    """Returns a MenuItem retrieved by its MenuItem.text."""
    return self._items.get(name)

  def setItem(self, item):
    """Overwrites an existing MenuItem, or appends a new one."""
    self._items[item.name] = item

  def delItem(self, name):
    """Removes an existing MenuItem."""
    del self._items[name]

  def _getItems(self):
    """Returns an ordered list of the MenuItems."""
    return self._items.values()

  items = property(_getItems, doc=
    """Read-only list of MenuItems, for use in templates.""")


class MenuItem:
  """Provides menu item properties as easily-accessible attributes.
  """
  
  def __init__(self, name, value=None, selected=False, annotation=None,
                sub_menu=None):
    """Initializes the menu item attributes from supplied arguments.
    
    Args:
      name: name of the menu item
      value: optional value associated with the menu item;
        default is None
      selected: Boolean indicating if this menu item is selected;
        default is False
      annotation: optional annotation associated with the menu item;
        default is None
      sub_menu: a Menu of sub-items to display below this menu item;
        default is None, indicating no sub-menu
    """
    self.name = name
    self.value = value
    self.selected = selected
    self.annotation = annotation
    self.sub_menu = sub_menu
