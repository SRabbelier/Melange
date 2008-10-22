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

"""Site map information, used to generate sidebar menus, urlpatterns, etc.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.api import users

from django.conf.urls import defaults

from soc.logic import models
from soc.logic import path_link_name
from soc.logic.site import page

import soc.logic.models.site_settings


# Home Page view
home = page.Page(
  page.Url(
    r'^$',
    'soc.views.home.public',
    kwargs={
      'path': models.site_settings.logic.DEF_SITE_SETTINGS_PATH,
      'entity_type': 'SiteSettings',
      'template': 'soc/site/home/public.html',
    }),
  'Google Open Source Programs',
  # it should be obvious that every page comes from the home page
  in_breadcrumb=False)

# User authentication view placeholders
# (these are not real Django views, but need to appear in menus, etc.)
user_signin = page.Page(
  page.Url(
    # not a real Django URL regex, just a unique placeholder
    users.create_login_url('/'),
    # no view, since App Engine handles this page
    # (this page will not be placed in urlpatterns)
    None,
    # name is alternate string for view when it is not unique
    name='user-sign-in'),
  'User (sign in)',
  link_url=users.create_login_url('/'),
  parent=home)

user_signout = page.Page(
  page.Url(
    # not a real Django URL regex, just a unique placeholder
    users.create_logout_url('/'),
    # no view, since App Engine handles this page
    # (this page will not be placed in urlpatterns)
    None,
    # name is alternate string for view when it is not unique
    name='user-sign-out'),
  'User (sign out)',
  link_url=users.create_logout_url('/'),
  parent=home)

# User Profile views
user_create = page.Page(
  page.Url(
    r'^user/profile$',
    'soc.views.user.profile.create'),
  'User: Create a New Profile',
  short_name='Site-wide User Profile',
  parent=user_signout)

user_edit = page.Page(
  page.Url(
    r'^user/profile/%s$' % path_link_name.LINKNAME_ARG_PATTERN,
    'soc.views.user.profile.edit'),
  'User: Modify Existing User Profile',
  parent=user_signout)

# Site Home Page views
site_home = page.Page(
  page.Url(
    r'^site/home$',
    'soc.views.home.public',
    kwargs={
      'path': models.site_settings.logic.DEF_SITE_SETTINGS_PATH,
      'entity_type': 'SiteSettings',
      'template': 'soc/site/home/public.html',
    }),
  'Google Open Source Programs',
  # it should be obvious that every page comes from the home page
  in_breadcrumb=False)

site_settings_edit = page.Page(
  page.Url(
    r'^site/settings/edit$',
    'soc.views.site.settings.edit',
    kwargs={
      'path': models.site_settings.logic.DEF_SITE_SETTINGS_PATH,
      'logic': models.site_settings.logic,
    }),
  'Site: Settings',
  short_name='Site Settings',
  parent=home)

# Site User Profile views
site_user_sub_menu = page.NonPage(
  'site-user-sub-menu',
  'Site: Users Sub-Menu',
  short_name='Site Users',
  parent=site_settings_edit)

site_user_lookup = page.Page(
  page.Url(
    r'^site/user/lookup$',
    'soc.views.site.user.profile.lookup'),
  'Site: Look Up an Existing User',
  short_name='Look Up Site User',
  parent=site_user_sub_menu)

site_user_create = page.Page(
  page.Url(
    r'^site/user/profile$',
    'soc.views.site.user.profile.create'),
  'Site: Create New User Profile',
  short_name='Create Site User',
  parent=site_user_sub_menu)

site_user_edit = page.Page(
  page.Url(
    r'^site/user/profile/%s$' % path_link_name.LINKNAME_ARG_PATTERN,
    'soc.views.site.user.profile.edit'),
  'Site: Modify Existing User Profile',
  short_name='Modify Site User',
  parent=site_user_sub_menu)

site_user_list = page.Page(
  page.Url(
    r'^site/user/list$',
    'soc.views.site.user.list.all'),
  'Site: List of Users',
  short_name='List Site Users',
  parent=site_user_sub_menu)

# Document views
docs_show = page.Page(
  page.Url(
    r'^docs/show/%s$' % path_link_name.PATH_LINKNAME_ARGS_PATTERN,
    'soc.views.models.docs.public'),
  'Show Document',
  parent=home)

# Site Document views
site_docs_sub_menu = page.NonPage(
  'site-docs-sub-menu',
  'Site: Documents Sub-Menu',
  short_name='Site Documents',
  parent=site_settings_edit)

site_docs_create = page.Page(
  page.Url(
    r'^docs/edit$',
    'soc.views.models.docs.create'),
  'Site: Create New Document',
  'Create Site Document',
  parent=site_docs_sub_menu)

site_docs_edit = page.Page(
  page.Url(
    r'^docs/edit/%s$' % path_link_name.PATH_LINKNAME_ARGS_PATTERN,
    'soc.views.models.docs.edit'),
  'Site: Modify Existing Document',
  short_name='Modify Site Document',
  parent=site_docs_sub_menu)

site_docs_delete = page.Page(
  page.Url(
    r'^docs/delete/%s$' % path_link_name.PATH_LINKNAME_ARGS_PATTERN,
    'soc.views.models.docs.delete'),
  'Site: Delete Existing Document',
  short_name='Delete Site Document',
  parent=site_docs_sub_menu)

site_docs_list = page.Page(
  page.Url(
    r'^docs/list$',
    'soc.views.models.docs.list'),
  'Site: List of Documents',
  short_name='List Site Documents',
  parent=site_docs_sub_menu)

# Sponsor Group public view
sponsor_profile = page.Page(
  page.Url(
    r'^sponsor/profile/%s$' % path_link_name.LINKNAME_ARG_PATTERN,
    'soc.views.models.sponsor.public'),
  'Sponsor Public Profile',
  parent=home)

# Sponsor Group Site views
site_sponsor_sub_menu = page.NonPage(
  'site-sponsor-sub-menu',
  'Site: Sponsors Sub-Menu',
  short_name='Site Sponsors',
  parent=site_settings_edit)

site_sponsor_create = page.Page(
  page.Url(
    r'^site/sponsor/profile$',
    'soc.views.models.sponsor.create'),
  'Site: Create New Sponsor',
  short_name='Create Site Sponsor',
  parent=site_sponsor_sub_menu)

site_sponsor_delete = page.Page(
  page.Url(
    r'^site/sponsor/profile/delete/%s$' % path_link_name.LINKNAME_ARG_PATTERN,
    'soc.views.models.sponsor.delete'),
  'Site: Delete Existing Sponsor',
  short_name='Delete Site Sponsor',
  parent=site_sponsor_sub_menu)

site_sponsor_edit = page.Page(
  page.Url(
    r'^site/sponsor/profile/%s$' % path_link_name.LINKNAME_ARG_PATTERN,
    'soc.views.models.sponsor.edit'),
  'Site: Modify Existing Sponsor',
  short_name='Modify Site Sponsor',
  parent=site_sponsor_sub_menu)

site_sponsor_list = page.Page(
  page.Url(
    r'^site/sponsor/list$',
    'soc.views.models.sponsor.list'),
  'Site: List of Sponsors',
  short_name='List Site Sponsors',
  parent=site_sponsor_sub_menu)

# Host Group public view
host_profile = page.Page(
  page.Url(
    r'^host/profile/%s/%s$' %
        (path_link_name.GENERIC_ARG_PATTERN % 'sponsor_ln',
         path_link_name.GENERIC_ARG_PATTERN % 'user_ln'),
    'soc.views.models.host.public'),
  'Host Public Profile',
  parent=home)

# Host Group Site views
site_host_sub_menu = page.NonPage(
  'site-host-sub-menu',
  'Site: Host Sub-Menu',
  short_name='Site Hosts',
  parent=site_settings_edit)

site_host_create = page.Page(
  page.Url(
    r'^site/host/profile$',
    'soc.views.models.host.create'),
  'Site: Create New Host',
  short_name='Create Site Host',
  parent=site_host_sub_menu)

site_host_delete = page.Page(
  page.Url(
    r'^site/host/delete/%s/%s$' %
        (path_link_name.GENERIC_ARG_PATTERN % 'sponsor_ln',
         path_link_name.GENERIC_ARG_PATTERN % 'user_ln'),
    'soc.views.models.host.delete'),
  'Site: Delete Existing Host',
  short_name='Delete Site Host',
  parent=site_host_sub_menu)

site_host_edit = page.Page(
  page.Url(
    r'^site/host/profile/%s/%s$' %
        (path_link_name.GENERIC_ARG_PATTERN % 'sponsor_ln',
         path_link_name.GENERIC_ARG_PATTERN % 'user_ln'),
    'soc.views.models.host.edit'),
  'Site: Modify Existing Host',
  short_name='Modify Site Host',
  parent=site_host_sub_menu)

site_host_list = page.Page(
  page.Url(
    r'^site/host/list$',
    'soc.views.models.host.list'),
  'Site: List of Hosts',
  short_name='List Site Hosts',
  parent=site_host_sub_menu)

# these are not really used...
#    (r'^org/profile/(?P<program>ghop[_0-9a-z]+)/(?P<link_name>[_0-9a-z]+)/$',
#     'soc.views.person.profile.edit',
#     {'template': 'ghop/person/profile/edit.html'}),
#    (r'^org/profile/(?P<program>[_0-9a-z]+)/(?P<link_name>[_0-9a-z]+)/$',
#     'soc.views.person.profile.edit'),


ROOT_PAGES = [
  # /, first level of the sidebar menu, excluded from breadcrumbs
  home,

  # alternate view of /, no menu presence
  site_home,
]


def getDjangoUrlPatterns(pages=ROOT_PAGES):
  """Returns Django urlpatterns derived from the site map Pages.

  Args:
    pages: a list of page.Page objects from which to generate urlpatterns
      (from them and from their child Pages); default is ROOT_PAGES

  Raises:
    KeyError if more than one Page has the same urlpattern.

    TODO(tlarsen): this probably does not work correctly, currently, since
    page.Page.makeDjangoUrls() returns a list, and this routine is
    combining lists from potentially multiple page hierarchies.  Each list
    might have a urlpattern that the other contains, but this won't be
    detected by the current code (will Django catch this?).  This really
    needs to be detected earlier via a global Page dictionary.
  """
  urlpatterns = ['']

  for page in pages:
    urlpatterns.extend(page.makeDjangoUrls())

  return defaults.patterns(*urlpatterns)
