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

"""Helpers for displaying arbitrarily nested menus as HTML lists.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from soc.logic import menu


class UlMenu(menu.Menu):
  """Ordered collection of MenuItem objects as a <ul> list.
  """

  def __init__(self, items=None):
    """Passes the menu items to the base class __init__().
    """
    menu.Menu.__init__(self, items=items)

  def getHtmlTags(self, indent):
    """Returns list of HTML tags for arbitrarily nested items in the menu.
    
    Args:
      indent: string prepended to the beginning of each line of output
        (usually consists entirely of spaces)
        
    Returns:
      a list of strings that can be joined with '\n' into a single string
      to produce an entire <ul>...</ul> list in HTML
    """
    tags = []

    if self.items:
      tags.append('%s<ul>' % indent)

      for item in self.items:
        tags.extend(item.getHtmlTags(indent + ' '))
    
      tags.append('%s</ul>' % indent)

    return tags

  def __str__(self):
    return '\n'.join(self.getHtmlTags(''))


class AHrefMenuItem(menu.MenuItem):
  """Provides HTML menu item properties as attributes as an <a href> link. 
  """
  
  def __init__(self, text, url=None, selected=False, help_text=None,
               sub_menu=None):
    """Initializes the menu item attributes from supplied arguments.
    
    Args:
      text: text displayed for the menu item link anchor
      url: optional URL to be placed in the menu item link href;
        default is None
      selected: Boolean indicating if this menu item is selected;
        default is False
      help_text: optional help text associated with the menu item
      sub_menu: see menu.MenuItem.__init__() 
    """
    menu.MenuItem.__init__(self, text, selected=selected, sub_menu=sub_menu)
    self.url = url
    self.help_text = help_text

  def getHtmlTags(self, indent):
    """Returns list of HTML tags for a menu item (and possibly its sub-menus).
    
    Args:
      indent: string prepended to the beginning of each line of output
        (usually consists entirely of spaces)
        
    Returns:
      a list of strings that can be joined with '\n' into a single string
      to produce an <a href="...">...</a> link, or just the MenuItem.name
      as plain text if there was no AHrefMenuItem.url; may also append
      arbitrarily nested sub-menus
    """
    tags = []

    # TODO(tlarsen): user-supplied content *must* be escaped to prevent XSS

    # TODO(tlarsen): implement "selected" style
    if self.url:
      tags.append('%s<a href=' % indent)
      tags.append('"%s">%s</a>' % (self.url, self.name))
    else:
      # if no URL, then not a link, so just display text
      tags.append(item.name)

    # TODO(tlarsen): implement the mouse-over support for item.help_text

    if self.sub_menu:
      tags.extend(self.sub_menu.getHtmlTags(indent + ' '))
          
    return tags

  def __str__(self):
    return '\n'.join(self.getHtmlTags(''))


class LiMenuItem(AHrefMenuItem):
  """Provides HTML menu item properties as attributes as an <li> list item.
  """
  
  def __init__(self, text, url=None, selected=False, help_text=None,
               sub_menu=None):
    """Initializes the menu item attributes from supplied arguments.
    
    Args:
      text, url, selected, help_text, sub_menu:
        see AHrefMenuItem.__init__() 
    """
    AHrefMenuItem.__init__(self, text, url=url, selected=selected,
                           help_text=help_text, sub_menu=sub_menu)

  def getHtmlTags(self, indent):
    """Returns <a href> link wrapped as an <li> list item.
    
    See also AHrefMenuItem.getHtmlTags().
    """
    return (['%s<li>' % indent]
            + AHrefMenuItem.getHtmlTags(self, indent + ' ')
            + ['%s</li>' % indent])
