#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module for the site global pages.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.forms import widgets as django_widgets
from django.conf.urls.defaults import url
from django.utils.functional import lazy
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.models.work import Work
from soc.models.site import Site
from soc.modules import callback
from soc.views.base import SiteRequestHandler
from soc.views.forms import ModelForm
from soc.views.helper import widgets


def getProgramMap():
  choices = [('', 'Active program')]
  choices += callback.getCore().getProgramMap()
  return choices


class SiteForm(ModelForm):
  """Django form for the site settings.
  """

  class Meta:
    model = Site
    exclude = ['link_id', 'scope', 'scope_path', 'home', 'tos', 'xsrf_secret_key']
    widgets = {
        'active_program': django_widgets.Select(choices=lazy(getProgramMap, list)()),
    }

  home_link_id = widgets.ReferenceField(
      reference_url='document', required=False,
      filter_fields={'prefix': 'site'},
      label=ugettext('Home page Document link ID'),
      help_text=Work.link_id.help_text)

  tos_link_id = widgets.ReferenceField(
      reference_url='document', required=False,
      filter_fields={'prefix': 'site'},
      label=ugettext('Terms of Service Document link ID'),
      help_text=Work.link_id.help_text)

  clean_noreply_email = cleaning.clean_empty_field('noreply_email')


class SitePage(SiteRequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^site/edit$', self, name='edit_site_settings'),
    ]

  def checkAccess(self):
    # TODO: check is developer
    pass

  def templatePath(self):
    # TODO: make this specific to the current active program
    return 'v2/soc/site/base.html'

  def context(self):
    if self.data.request.method == 'POST':
      site_form = SiteForm(self.data.POST, instance=self.data.site)
    else:
      site_form = SiteForm(instance=self.data.site)
    return {
        'page_name': 'Edit site settings',
        'site_form': site_form.render(),
    }

  def validate(self):
    site_form = SiteForm(self.data.POST, instance=self.data.site)

    if not site_form.is_valid():
      return False

    site_form.save()

  def post(self):
    """Handler for HTTP POST request.
    """
    if self.validate():
      self.redirect(reverse('edit_site_settings'))
    else:
      self.get()
