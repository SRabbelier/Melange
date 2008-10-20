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

"""Page properties, used to generate sidebar menus, urlpatterns, etc.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


import copy
import re

from django.conf.urls import defaults

from python25src import urllib

from soc.logic import menu
from soc.logic.no_overwrite_sorted_dict import NoOverwriteSortedDict


class Url:
  """The components of a Django URL pattern.
  """
   
  def __init__(self, regex, view, kwargs=None, name=None, prefix=''):
    """Collects Django urlpatterns info into a simple object.
    
    The arguments to this constructor correspond directly to the items in
    the urlpatterns tuple, which also correspond to the parameters of
    django.conf.urls.defaults.url().
    
    Args:
      regex: a Django URL regex pattern, which, for obvious reason, must
        be unique
      view: a Django view, either a string or a callable; if a callable,
        a unique 'name' string must be supplied
      kwargs: optional dict of extra arguments passed to the view
        function as keyword arguments, which is copy.deepcopy()'d;
        default is None, which supplies an empty dict {}
      name: optional name of the view; used instead of 'view' if supplied;
        the 'name' or 'view' string, whichever is used, must be unique
        amongst *all* Url objects supplied to a Page object
      prefix: optional view prefix
    """
    self.regex = regex
    self.view = view
    
    if kwargs:
      self.kwargs = copy.deepcopy(kwargs)
    else:
      self.kwargs = {}

    self.name = name
    self.prefix = prefix

  def makeDjangoUrl(self, **extra_kwargs):
    """Returns a Django url() used by urlpatterns, or None if not a view.
    """
    if not self.view:
      return None

    kwargs = copy.deepcopy(self.kwargs)
    kwargs.update(extra_kwargs)
    return defaults.url(self.regex, self.view, kwargs=kwargs,
                        name=self.name, prefix=self.prefix)

  _STR_FMT = '''%(indent)sregex: %(regex)s
%(indent)sview: %(view)s
%(indent)skwargs: %(kwargs)s
%(indent)sname: %(name)s
%(indent)sprefix: %(prefix)s
'''

  def asIndentedStr(self, indent=''):
    """Returns an indented string representation useful for logging.
    
    Args:
      indent: an indentation string that is prepended to each line present
        in the multi-line string returned by this method.
    """
    return self._STR_FMT % {'indent': indent, 'regex': self.regex,
                            'view': self.view, 'kwargs': self.kwargs,
                            'name': self.name, 'prefix': self.prefix}

  def __str__(self):
    """Returns a string representation useful for logging.
    """
    return self.asIndentedStr()


class Page:
  """An abstraction that combines a Django view with sidebar menu info.
  """
  
  def __init__(self, url, long_name, short_name=None, selected=False,
               annotation=None, parent=None, link_url=None,
               in_breadcrumb=True, force_in_menu=False):
    """Initializes the menu item attributes from supplied arguments.
    
    Args:
      url: a Url object
      long_name: title of the Page
      short_name: optional menu item and breadcrumb name; default is
        None, in which case long_name is used
      selected: Boolean indicating if this menu item is selected;
        default is False
      annotation: optional annotation associated with the menu item;
        default is None
      parent: optional Page that is the logical "parent" of this page;
        used to construct hierarchical menus and breadcrumb trails
      link_url: optional alternate URL link; if supplied, it is returned
        by makeLinkUrl(); default is None, and makeLinkUrl() attempts to
        create a URL link from url.regex 
      in_breadcrumb: if True, the Page appears in breadcrumb trails;
        default is True
      force_in_menu: if True, the Page appears in menus even if it does
        not have a usable link_url; default is False, which excludes
        the Page if makeLinkUrl() returns None
    """
    self.url = url
    self.long_name = long_name
    self.annotation = annotation
    self.in_breadcrumb = in_breadcrumb
    self.force_in_menu = force_in_menu
    self.link_url = link_url
    self.selected = selected
    self.parent = parent

    # create ordered, unique mappings of URLs and view names to Pages
    self.child_by_urls = NoOverwriteSortedDict()
    self.child_by_views = NoOverwriteSortedDict()
    
    if not short_name:
      short_name = long_name
      
    self.short_name = short_name
    
    if parent:
      # tell parent Page about parent <- child relationship
      parent.addChild(self)
      
    # TODO(tlarsen): build some sort of global Page dictionary to detect
    #   collisions sooner and to make global queries from URLs to pages
    #   and views to Pages possible (without requiring a recursive search)

  def getChildren(self):
    """Returns an iterator over any child Pages 
    """
    for page in self.child_by_views.itervalues():
      yield page

  children = property(getChildren)

  def getChild(self, url=None, regex=None, view=None,
               name=None, prefix=None, request_path=None):
    """Returns a child Page if one can be identified; or None otherwise.
    
    All of the parameters to this method are optional, but at least one
    must be supplied to return anything other than None.  The parameters
    are tried in the order they are listed in the "Args:" section, and
    this method exits on the first "match".
    
    Args:
      url: a Url object, used to overwrite the regex, view, name, and
        prefix parameters if present; default is None
      regex: a regex pattern string, used to return the associated
        child Page
      view: a view string, used to return the associated child Page
      name: a name string, used to return the associated child Page
      prefix: (currently unused, see TODO below in code)
      request_path: optional HTTP request path string (request.path)
        with no query arguments
    """
    # this code is yucky; there is probably a better way...
    if url:
      regex = url.regex
      view = url.view
      name = url.name
      prefix = url.prefix

    if regex in self.child_by_urls:
      # regex supplied and Page found, so return that Page
      return self.child_by_urls[regex][0]
  
    # TODO(tlarsen): make this work correctly with prefixes

    if view in self.child_views:
      # view supplied and Page found, so return that Page
      return self.child_by_views[view]
  
    if name in self.child_views:
      # name supplied and Page found, so return that Page
      return self.child_by_views[name]

    if request_path.startswith('/'):
      request_path = request_path[1:]

    # attempt to match the HTTP request path with a Django URL pattern
    for pattern, (page, regex) in self.child_by_urls:
      if regex.match(request_path):
        return page

    return None

  def addChild(self, page):
    """Adds a unique Page as a child Page of this parent.
    
    Raises:
      ValueError if page.url.regex is not a string.
      ValueError if page.url.view is not a string.
      ValueError if page.url.name is supplied but is not a string.
      KeyError if page.url.regex is already associated with another Page.
      KeyError if page.url.view/name is already associated with another Page.
    """
    # TODO(tlarsen): see also TODO in __init__() about global Page dictionary

    url = page.url
    
    if url.regex:
      if not isinstance(url.regex, basestring):
        raise ValueError('"regex" must be a string, not a compiled regex')

      # TODO(tlarsen): see if Django has some way exposed in its API to get
      #   the view name from the request path matched against urlpatterns;
      #   if so, there would be no need for child_by_urls, because the
      #   request path could be converted for us by Django into a view/name,
      #   and we could just use child_by_views with that string instead
      self.child_by_urls[url.regex] = (page, re.compile(url.regex))
    # else: NonUrl does not get indexed by regex, because it has none

    # TODO(tlarsen): make this work correctly if url has a prefix
    #   (not sure how to make this work with include() views...)
    if url.name:
      if not isinstance(url.name, basestring):
        raise ValueError('"name" must be a string if it is supplied')

      view = url.name
    elif isinstance(url.view, basestring):
      view = url.view
    else:
      raise ValueError('"view" must be a string if "name" is not supplied')

    self.child_by_views[view] = page

  def delChild(self, url=None, regex=None, view=None, name=None,
               prefix=None):
    """Removes a child Page if one can be identified.
    
    All of the parameters to this method are optional, but at least one
    must be supplied in order to remove a child Page.  The parameters
    are tried in the order they are listed in the "Args:" section, and
    this method uses the first "match".
    
    Args:
      url: a Url object, used to overwrite the regex, view, name, and
        prefix parameters if present; default is None
      regex: a regex pattern string, used to remove the associated
        child Page
      view: a view string, used to remove the associated child Page
      name: a name string, used to remove the associated child Page
      prefix: (currently unused, see TODO below in code)
      
    Raises:
      KeyError if the child Page could not be definitively identified in
      order to delete it.
    """
    # this code is yucky; there is probably a better way...
    if url:
      regex = url.regex
      view = url.view
      name = url.name
      prefix = url.prefix

    # try to find page by regex, view, or name, in turn
    if regex in self.child_by_urls:
      url = self.child_by_urls[regex][0].url
      view = url.view
      name = url.name
      prefix = url.prefix
    elif view in self.child_views:
      # TODO(tlarsen): make this work correctly with prefixes
      regex = self.child_by_views[view].url.regex
    elif name in self.child_views:
      regex = self.child_by_views[name].url.regex

    if regex:
      # regex must refer to an existing Page at this point
      del self.child_urls[regex]

    if not isinstance(view, basestring):
      # use name if view is callable() or None, etc.
      view = name

    # TODO(tlarsen): make this work correctly with prefixes
    del self.child_by_views[view]
    

  def makeLinkUrl(self):
    """Makes a URL link suitable for <A HREF> use.
    
    Returns:
      self.link_url if link_url was supplied to the __init__() constructor
        and it is a non-False value
       -OR-
      a suitable URL extracted from the url.regex, if possible
       -OR-
      None if url.regex contains quotable characters that have not already
        been quoted (that is, % is left untouched, so quote suspect
        characters in url.regex that would otherwise be quoted)
    """
    if self.link_url:
      return self.link_url

    link = self.url.regex
    
    if not link:
      return None

    if link.startswith('^'):
      link = link[1:]
    
    if link.endswith('$'):
      link = link[:-1]

    if not link.startswith('/'):
      link = '/' + link
    
    # path separators and already-quoted characters are OK
    if link != urllib.quote(link, safe='/%'):
      return None

    return link

  def makeMenuItem(self):
    """Returns a menu.MenuItem for the Page (and any child Pages).
    """
    child_items = []
    
    for child in self.children:
      child_item = child.makeMenuItem()
      if child_item:
        child_items.append(child_item)
    
    if child_items:
      sub_menu = menu.Menu(items=child_items)
    else:
      sub_menu = None
    
    link_url = self.makeLinkUrl()
    
    if (not sub_menu) and (not link_url) and (not self.force_in_menu):
      # no sub-menu, no valid link URL, and not forced to be in menu
      return None
    
    return menu.MenuItem(
      self.short_name, value=link_url, sub_menu=sub_menu)

  def makeDjangoUrl(self):
    """Returns the Django url() for the underlying self.url.
    """
    return self.url.makeDjangoUrl(page=self)

  def makeDjangoUrls(self):
    """Returns an ordered mapping of unique Django url() objects.
    
    Raises:
      KeyError if more than one Page has the same urlpattern.
      
    TODO(tlarsen): this really needs to be detected earlier via a
      global Page dictionary
    """
    return self._makeDjangoUrlsDict().values()

  def _makeDjangoUrlsDict(self):
    """Returns an ordered mapping of unique Django url() objects.
    
    Used to implement makeDjangoUrls().  See that method for details.
    """
    urlpatterns = NoOverwriteSortedDict()

    django_url = self.makeDjangoUrl()
    
    if django_url:
      urlpatterns[self.url.regex] = django_url
    
    for child in self.children:
      urlpatterns.update(child._makeDjangoUrlsDict())
    
    return urlpatterns

  _STR_FMT = '''%(indent)slong_name: %(long_name)s
%(indent)sshort_name: %(short_name)s
%(indent)sselected: %(selected)s
%(indent)sannotation: %(annotation)s
%(indent)surl: %(url)s
'''

  def asIndentedStr(self, indent=''):
    """Returns an indented string representation useful for logging.
    
    Args:
      indent: an indentation string that is prepended to each line present
        in the multi-line string returned by this method.
    """
    strings = [ 
        self._STR_FMT % {'indent': indent, 'long_name': self.long_name,
                         'short_name': self.short_name,
                         'selected': self.selected,
                         'annotation': self.annotation,
                         'url': self.url.asIndentedStr(indent + ' ')}]

    for child in self.children:
      strings.extend(child.asIndentedStr(indent + '  '))

    return ''.join(strings)

  def __str__(self):
    """Returns a string representation useful for logging.
    """
    return self.asIndentedStr()


class NonUrl(Url):
  """Placeholder for when a site-map entry is not a linkable URL.
  """
   
  def __init__(self, name):
    """Creates a non-linkable Url placeholder.
    
    Args:
      name: name of the non-view placeholder; see Url.__init__()
    """
    Url.__init__(self, None, None, name=name)

  def makeDjangoUrl(self, **extra_kwargs):
    """Always returns None, since NonUrl is never a Django view.
    """
    return None


class NonPage(Page):
  """Placeholder for when a site-map entry is not a displayable page.
  """

  def __init__(self, non_url_name, long_name, **page_kwargs):
    """Constructs a NonUrl and passes it to base Page class __init__().
    
    Args:
      non_url_name:  unique (it *must* be) string that does not match
        the 'name' or 'view' of any other Url or NonUrl object;
        see Url.__init__() for details
      long_name:  see Page.__init__()
      **page_kwargs:  keyword arguments passed directly to the base
        Page class __init__()
    """
    non_url = NonUrl(non_url_name)
    Page.__init__(self, non_url, long_name, **page_kwargs)
