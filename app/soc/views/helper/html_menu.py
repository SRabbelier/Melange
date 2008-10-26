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


class HtmlMenu:
  """Ordered collection of MenuItem objects as <p>...</p> paragraphs.
  """
  ITEM_PREFIX_FMT = '%(indent)s<p>'
  ITEM_SUFFIX_FMT = '%(indent)s</p>'

  def __init__(self, menu, item_class=None):
    """Wraps an soc.logic.menu.Menu in order to render it as HTML.
    
    Args:
      menu: an soc.logic.menu.Menu object
      item_class: style used to render the MenuItems contained in menu;
        default is None, which causes AHrefMenuItem to be used  
    """
    self._menu = menu

    # workaround for circular dependency between AHrefMenuItem and this class
    if not item_class:
      item_class = AHrefMenuItem

    self._item_class = item_class

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

    if self._menu.items:
      tags.append(self.ITEM_PREFIX_FMT % {'indent': indent})

      for item in self._menu.items:
        tags.extend(self._item_class(
            item, menu_class=self.__class__).getHtmlTags(indent + ' '))
    
      tags.append(self.ITEM_SUFFIX_FMT % {'indent': indent})

    return tags

  def __str__(self):
    return '\n'.join(self.getHtmlTags(''))


class UlMenu(HtmlMenu):
  """Ordered collection of MenuItem objects as a <ul> list.
  """
  ITEM_PREFIX_FMT = '%(indent)s<ul>'
  ITEM_SUFFIX_FMT = '%(indent)s</ul>'

  def __init__(self, menu, item_class=None):
    """Wraps an soc.logic.menu.Menu in order to render it as HTML.
    
    Args:
      menu: an soc.logic.menu.Menu object
      item_class: style used to render the MenuItems contained in menu;
        default is None, which causes LiMenuItem to be used  
    """
    # workaround for circular dependency between LiMenuItem and this class
    if not item_class:
      item_class = LiMenuItem

    HtmlMenu.__init__(self, menu, item_class=item_class)


class HtmlMenuItem:
  """Base class for specific MenuItem wrappers used by HtmlMenu sub-classes.
  """
  
  def __init__(self, item, menu_class=HtmlMenu):
    """Wraps an soc.logic.menu.MenuItem in order to render it as HTML.
    
    Args:
      item: an soc.logic.menu.MenuItem object to wrap, in order to produce
        a representation of it as HTML tags later
      menu_class: a class derived from HtmlMenu, used to style any sub-menu
        of the MenuItem; default is HtmlMenu
    """
    self._item = self.escapeItem(item)
    self._menu_class = menu_class

  def getItemHtmlTags(self, indent):
    """Returns list of HTML tags for the menu item itself.
    
    This method is intended to be overridden by sub-classes.
    
    Args:
      indent: string prepended to the beginning of each line of output
        (usually consists entirely of spaces)
        
    Returns:
      a list of strings that can be joined with '\n' into a single string
      to produce:
        <b>name</b> value <i>(annotation)</i>
      with value and/or <i>(annotation)</i> omitted if either is missing
    """
    # TODO(tlarsen): implement "selected" style

    tags = ['%s<b>%s</b>' % (indent, self._item.name)]
    
    if self._item.value:
      tags.append('%s%s' % (indent, self._item.value))

    if self._item.annotation:
      tags.append('%s<i>(%s)</i>' % (indent, self._item.annotation))
      
    return tags

  def getSubMenuHtmlTags(self, indent):
    """Returns list of HTML tags for any sub-menu, if one exists.
    
    Args:
      indent: string prepended to the beginning of each line of output
        (usually consists entirely of spaces)
        
    Returns:
      an empty list if there is no sub-menu
        -OR-
      the list of HTML tags that render the entire sub-menu (depends on the
      menu_class that was provided to __init__()
    """
    if not self._item.sub_menu:
      return []
  
    return self._menu_class(self._item.sub_menu,
        item_class=self.__class__).getHtmlTags(indent)

  def getHtmlTags(self, indent):
    """Returns list of HTML tags for a menu item (and possibly its sub-menus).
    
    Args:
      indent: string prepended to the beginning of each line of output
        (usually consists entirely of spaces)
        
    Returns:
      a list of strings that can be joined with '\n' into a single string
      to produce an HTML representation of the wrapped MenuItem, with
      arbitrarily nested sub-menus possibly appended
    """
    return self.getItemHtmlTags(indent) + self.getSubMenuHtmlTags(indent)

  def escapeItem(self, item):
    """HTML-escapes possibly user-supplied fields to prevent XSS.
    
    Args:
      item: an soc.logic.menu.MenuItem that is altered in-place; the
        fields that are potentially user-provided (name, value, annotation)
        are escaped using self.escapeText()
        
    Returns:
      the originally supplied item, for convenience, so that this method can
      be combined with an assignment
    """
    item.name = self.escapeText(item.name)
    item.value = self.escapeText(item.value)
    item.annotation = self.escapeText(item.annotation)
    return item

  def escapeText(self, text):
    """
    """
    # TODO(tlarsen): user-supplied content *must* be escaped to prevent XSS
    return text

  def __str__(self):
    return '\n'.join(self.getHtmlTags(''))


class AHrefMenuItem(HtmlMenuItem):
  """Provides HTML menu item properties as attributes as an <a href> link. 
  """
  
  def getItemHtmlTags(self, indent):
    """Returns list of HTML tags for the menu item itself.
    
    Args:
      indent: string prepended to the beginning of each line of output
        (usually consists entirely of spaces)
        
    Returns:
      a list of strings that can be joined with '\n' into a single string
      to produce an <a href="...">...</a> link, or just the MenuItem.name
      as plain text if there was no AHrefMenuItem.value URL
    """
    # TODO(tlarsen): implement "selected" style

    if not self._item.value:
      # if no URL, then not a link, so just display item.name as text
      return [self._item.name]
  
    # URL supplied, so make an <a href="item.value">item.name</a> link
    return ['%s<a href="%s">%s</a>' % (indent, self._item.value, self._item.name)]

class LiMenuItem(AHrefMenuItem):
  """Provides HTML menu item properties as attributes as an <li> list item.
  """

  def __init__(self, item, menu_class=UlMenu):
    """Wraps an soc.logic.menu.MenuItem in order to render it as HTML.
    
    Args:
      item: an soc.logic.menu.MenuItem object to wrap, in order to produce
        a representation of it as HTML tags later
      menu_class: a class derived from HtmlMenu, used to style any sub-menu
        of the MenuItem; default is UlMenu
    """
    AHrefMenuItem.__init__(self, item, menu_class=menu_class)

  def getHtmlTags(self, indent):
    """Returns <a href> link wrapped as an <li> list item.
    
    See also AHrefMenuItem.getHtmlTags().
    """
    return (['%s<li>' % indent]
            + AHrefMenuItem.getHtmlTags(self, indent + ' ')
            + ['%s</li>' % indent])
