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


from google.appengine.ext import db
from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import validate
from soc.views import helper
from soc.views.helper import widgets
from soc.views.models import home_settings

import soc.models.site_settings
import soc.logic.models.site_settings
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


class CreateForm(home_settings.SettingsValidationForm):
  """Django form displayed when creating or editing Site Settings.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.site_settings.SiteSettings

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'home']


class EditForm(CreateForm):
  """Django form displayed a Document is edited.
  """

  pass


class View(home_settings.View):
  """View methods for the Document model
  """

  def __init__(self, original_params=None, original_rights=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View
      original_rights: a dict with right definitions for this View
    """

    params = {}
    rights = {}

    params['name'] = "Site Settings"
    params['name_short'] = "Site"
    params['name_plural'] = "Site Settings"

    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    params['lists_template'] = {
      'list_main': 'soc/list/list_main.html',
      'list_pagination': 'soc/list/list_pagination.html',
      'list_row': 'soc/site_settings/list/site_row.html',
      'list_heading': 'soc/site_settings/list/site_heading.html',
    }

    params['delete_redirect'] = '/site/list'
    params['create_redirect'] = '/site/edit'

    params = dicts.merge(original_params, params)
    rights = dicts.merge(original_rights, rights)

    home_settings.View.__init__(self, original_rights=rights, original_params=params)

    self._logic = soc.logic.models.site_settings.logic

  def main_public(self, request, page_name=None, **kwargs):
    """Displays the main site settings page

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object
      kwargs: not used
    """

    keys = self._logic.getKeyFieldNames()
    values = self._logic.getMainKeyValues()
    key_values = dicts.zip(keys, values)

    return self.public(request, page_name, **key_values)

  def main_edit(self, request, page_name=None, **kwargs):
    """Displays the edit page for the main site settings page

    Args:
      request: the standard Django HTTP request object
      page: a soc.logic.site.page.Page object
      kwargs: not used
    """

    keys = self._logic.getKeyFieldNames()
    values = self._logic.getMainKeyValues()
    key_values = dicts.zip(keys, values)

    return self.edit(request, page_name, **key_values)


view = View()

create = view.create
edit = view.edit
delete = view.delete
list = view.list
public = view.public
main_public = view.main_public
main_edit = view.main_edit
