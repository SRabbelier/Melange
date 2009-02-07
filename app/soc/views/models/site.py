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

"""Views for Site Settings.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import dicts
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import document as document_view
from soc.views.models import presence_with_tos

import soc.models.site
import soc.logic.models.site
import soc.logic.dicts


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
    rights['show'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = soc.logic.models.site.logic
    new_params['rights'] = rights

    new_params['name'] = "Site Settings"
    new_params['name_plural'] = new_params['name']
    new_params['name_short'] = "Site"

    new_params['sidebar_defaults'] = [('/%s/edit', 'Edit %(name)s', 'edit')]
    new_params['sidebar_heading'] = new_params['name_short']

    new_params['edit_template'] = 'soc/site/edit.html'
    new_params['home_template'] = 'soc/site/home.html'

    new_params['create_extra_dynafields'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput, required=True),
        }
    new_params['edit_extra_dynafields'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput, required=True),
        'home_link_id': widgets.ReferenceField(
            reference_url='document',
            required=False, label=ugettext('Home page Document link ID'),
            help_text=soc.models.work.Work.link_id.help_text),
        'tos_link_id': widgets.ReferenceField(
            reference_url='document',
            required=False, label=ugettext('Terms of Service Document link ID'),
            help_text=soc.models.work.Work.link_id.help_text),
        }

    patterns = []

    page_name = "Home Page"
    patterns += [(r'^$', 'soc.views.models.%(module_name)s.main_public', 
                  page_name)]

    page_name = "Edit Site"
    patterns += [(r'^%(url_name)s/(?P<access_type>edit)$',
                  'soc.views.models.%(module_name)s.main_edit',
                  page_name)]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def getSidebarMenus(self, id, user, params=None):
    """See base.View.getSidebarMenus.

    Returns a custom sidebar entry for the 'site' singleton.
    """

    entity = self._logic.getSingleton()

    submenus = []

    if entity:
      submenus += document_view.view.getMenusForScope(entity, self._params)
      if user and accounts.isDeveloper(id, user):
        submenus += [(redirects.getCreateDocumentRedirect(entity, 'site'),
            "Create a New Document", 'any_access')]

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

    keys = self._logic.getKeyFieldNames()

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

    keys = self._logic.getKeyFieldNames()

    # No entity in this case, since Site key values are hard-coded for the
    # Site singleton, so pass in None to match parent method footprint.
    values = self._logic.getKeyValuesFromEntity(None)
    key_values = dicts.zip(keys, values)

    return self.edit(request, "edit", page_name, seed=key_values, **key_values)


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
export = view.export
main_public = view.mainPublic
main_edit = view.mainEdit
home = view.home
