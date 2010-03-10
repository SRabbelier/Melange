#!/usr/bin/env python2.5
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

"""Views for Site Settings.
"""

__authors__ = [
    '"Leon Palm" <lpalm@google.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models.site import logic as site_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import document as document_view
from soc.views.models import presence_with_tos

import soc.logic.models.site
import soc.logic.dicts
import soc.logic.system


class View(presence_with_tos.View):
  """View methods for the Document model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['unspecified'] = ['checkIsDeveloper']
    rights['any_access'] = ['allow']
    rights['home'] = ['allow']
    rights['search'] = ['allow']
    rights['show'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = site_logic
    new_params['rights'] = rights

    new_params['name'] = "Site Settings"
    new_params['name_plural'] = new_params['name']
    new_params['document_prefix'] = 'site'
    new_params['name_short'] = "Site"

    new_params['sidebar_developer'] = []

    new_params['sidebar_defaults'] = [('/%s/edit', 'Edit %(name)s', 'edit')]
    new_params['sidebar_heading'] = new_params['name_short']

    new_params['edit_template'] = 'soc/site/edit.html'
    new_params['home_template'] = 'soc/site/home.html'
    new_params['search_template'] = 'soc/site/search.html'

    new_params['create_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput, required=True),
        'noreply_email': forms.EmailField(required=False),
        }
    new_params['edit_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput, required=True),
        'home_link_id': widgets.ReferenceField(
            reference_url='document', required=False,
            filter_fields={'prefix': new_params['document_prefix']},
            label=ugettext('Home page Document link ID'),
            help_text=soc.models.work.Work.link_id.help_text),
        'tos_link_id': widgets.ReferenceField(
            reference_url='document', required=False,
            filter_fields={'prefix': new_params['document_prefix']},
            label=ugettext('Terms of Service Document link ID'),
            help_text=soc.models.work.Work.link_id.help_text),
        'clean_noreply_email': cleaning.clean_empty_field('noreply_email'),
        }

    # XSRF secret key is not editable by mere mortals.
    new_params['extra_dynaexclude'] = ['xsrf_secret_key']

    patterns = []

    page_name = "Home Page"
    patterns += [(r'^$', 'soc.views.models.%(module_name)s.main_public',
                  page_name)]

    page_name = "Edit Site"
    patterns += [(r'^%(url_name)s/(?P<access_type>edit)$',
                  'soc.views.models.%(module_name)s.main_edit',
                  page_name)]

    page_name = "Search"
    patterns += [(r'^%(url_name)s/(?P<access_type>search)$',
                  'soc.views.models.%(module_name)s.search',
                  page_name)]

    if soc.logic.system.isDebug():
      patterns += [('^seed_db$', 'soc.models.seed_db.seed', "Seed DB"),
                   ('^clear_db$', 'soc.models.seed_db.clear', "Clear DB"),
                   ('^reseed_db$', 'soc.models.seed_db.reseed', "Reseed DB"),
                   ('^seed_many$', 'soc.models.seed_db.seed_many', "Seed Many"),
                   ('^new_seed_many$', 'soc.models.seed_db.new_seed_many',
                    "New Seed Many"),
                   ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def getSidebarMenus(self, id, user, params=None):
    """See base.View.getSidebarMenus.

    Returns a custom sidebar entry for the 'site' singleton.
    """

    entity = site_logic.getSingleton()

    submenus = document_view.view.getMenusForScope(entity, self._params)

    try:
      rights = self._params['rights']
      rights.setCurrentUser(id, user)
      rights.checkIsHost()
      is_host = True
    except out_of_band.Error:
      is_host = False

    if is_host:
      submenus += [(redirects.getCreateDocumentRedirect(entity, 'site'),
          "Create a New Document", 'any_access')]

      submenus += [(redirects.getListDocumentsRedirect(entity, 'site'),
          "List Documents", 'any_access')]

    if entity.cse_key:
      # only add the search entry if a key is defined
      submenus += [('/site/search', 'Search', 'any_access')]

    new_params = {}
    new_params['sidebar_additional'] = submenus

    params = dicts.merge(params, new_params)
    return super(View, self).getSidebarMenus(id, user, params=params)

  def mainPublic(self, request, page_name=None, **kwargs):
    """Displays the main site settings page.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      kwargs: not used
    """

    keys = site_logic.getKeyFieldNames()

    # No entity in this case, since Site key values are hard-coded for the
    # Site singleton, so pass in None to match parent method footprint.
    values = self._logic.getKeyValuesFromEntity(None)
    key_values = dicts.zip(keys, values)

    return self.home(request, "home", page_name=page_name, **key_values)

  def mainEdit(self, request, page_name=None, **kwargs):
    """Displays the edit page for the main site settings page.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      kwargs: not used
    """

    keys = site_logic.getKeyFieldNames()

    # No entity in this case, since Site key values are hard-coded for the
    # Site singleton, so pass in None to match parent method footprint.
    values = site_logic.getKeyValuesFromEntity(None)
    key_values = dicts.zip(keys, values)

    return self.edit(request, "edit", page_name, seed=key_values, **key_values)

  @decorators.merge_params
  @decorators.check_access
  def search(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays the search page for the entity specified by **kwargs.

    Params usage:
      rights: The rights dictionary is used to check if the user has
        the required rights to view the admin page for this entity.
        See checkAccess for more details on how the rights dictionary
        is used to check access rights.
      name: The name value is used to set the entity_type in the
        context so that the template can refer to it.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])

    context['page_name'] = page_name
    settings = site_logic.getSingleton()
    context['cse_key'] = settings.cse_key
    template = params['search_template']

    return helper.responses.respond(request, template, context)


view = View()

admin = decorators.view(view.admin)
create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
public = decorators.view(view.public)
export = decorators.view(view.export)
main_public = decorators.view(view.mainPublic)
main_edit = decorators.view(view.mainEdit)
home = decorators.view(view.home)
search = decorators.view(view.search)
