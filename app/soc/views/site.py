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


import os

from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse
from django.forms import widgets as django_widgets
from django.utils.functional import lazy
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic.models.document import logic as document_logic
from soc.models.site import Site
from soc.models.work import Work
from soc.views.base import SiteRequestHandler
from soc.views.forms import ModelForm
from soc.views.helper import widgets as widgets_helper

from soc.modules import callback


def getProgramMap():
  choices = [('', 'Active program')]
  choices += callback.getCore().getProgramMap()
  return choices


class SiteForm(ModelForm):
  """Django form for the site settings.
  """

  class Meta:
    model = Site
    exclude = ['link_id', 'scope', 'scope_path', 'home', 'xsrf_secret_key']
    widgets = {
        'active_program': django_widgets.Select(
            choices=lazy(getProgramMap, list)()),
    }

  def clean_tos(self):
    if self.cleaned_data['tos'] is None:
      return ''
    return self.cleaned_data['tos']

  clean_noreply_email = cleaning.clean_empty_field('noreply_email')


class SitePage(SiteRequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^site/edit$', self, name='edit_site_settings'),
    ]

  def jsonContext(self):
    entities = document_logic.getForFields({'prefix': 'site'})

    data = [{'key': str(i.key()),
            'link_id': i.link_id,
            'label': i.title}
            for i in entities]

    return {'data': data}

  def checkAccess(self):
    # TODO: check is developer
    pass

  def templatePath(self):
    # TODO: make this specific to the current active program
    return 'v2/soc/site/base.html'

  def context(self):
    site_form = SiteForm(self.data.POST or None, instance=self.data.site)
    return {
        'app_version': os.environ.get('CURRENT_VERSION_ID', '').split('.')[0],
        'page_name': 'Edit site settings',
        'site_form': site_form,
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
