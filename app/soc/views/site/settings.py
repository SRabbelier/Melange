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

"""Site Settings views.

edit: settings view for authorized Developers, Administrators, etc.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.logic import models
from soc.views import settings as settings_views
from soc.views.helper import decorators

import soc.logic.models.site_settings
import soc.models.site_settings


class SiteSettingsForm(settings_views.SettingsValidationForm):
  """Django form displayed when creating or editing Site Settings.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.site_settings.SiteSettings

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'home']


@decorators.view
def edit(request, page=None, partial_path=None, link_name=None, 
         logic=models.site_settings.logic,
         settings_form_class=SiteSettingsForm,
         template=settings_views.DEF_HOME_EDIT_TMPL):
  """View for authorized User to edit contents of a Site Settings page.

  Args:
    request: the standard django request object.
    page: a soc.logic.site.page.Page object which is abstraction that
      combines a Django view with sidebar menu info
    path: path that is used to uniquely identify settings
    logic: settings logic object
    settings_form_class: class which should be used as Site Settings Form
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  return settings_views.edit(request, page=page, partial_path=partial_path, 
                             link_name=link_name, logic=logic,
                             settings_form_class=settings_form_class,
                             template=template)
  