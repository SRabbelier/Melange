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

"""Site-wide Melange home page views.

public: how the general public sees the site home page of a Melange
  site
  
edit: site settings view for logged-in Developers
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import http
from django import shortcuts
from django import newforms as forms

from soc.logic import out_of_band
from soc.logic import validate
from soc.logic.site import id_user
from soc.views import simple
from soc.views import helper
import soc.views.helper.templates
import soc.views.helper.widgets
from soc.views.helpers import forms_helpers
from soc.views.helpers import response_helpers

import soc.models.site_settings
import soc.models.document
import soc.logic.document
import soc.logic.site.settings


class DocumentForm(forms_helpers.DbModelForm):
  content = forms.fields.CharField(widget=helper.widgets.TinyMCE())

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.document.Document
    
    #: list of model fields which will *not* be gathered by the form
    exclude = ['partial_path', 'link_name',
               'user', 'modified', 'created', 'inheritance_line']


class SiteSettingsForm(forms_helpers.DbModelForm):
  """Django form displayed when creating or editing Site Settings.
  """
  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.site_settings.SiteSettings

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'home']

  def clean_feed_url(self):
    feed_url = self.cleaned_data.get('feed_url')

    if feed_url == '':
      # feed url not supplied (which is OK), so do not try to validate it
      return None
    
    if not validate.isFeedURLValid(feed_url):
      raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

    return feed_url


DEF_SITE_SETTINGS_PATH = 'site'
DEF_SITE_HOME_DOC_LINK_NAME = 'home'

DEF_SITE_HOME_PUBLIC_TMPL = 'soc/site/home/public.html'

def public(request, template=DEF_SITE_HOME_PUBLIC_TMPL):
  """How the "general public" sees the Melange site home page.

  Args:
    request: the standard django request object.
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)
  
  site_settings = soc.logic.site.settings.getSiteSettings(DEF_SITE_SETTINGS_PATH)

  if site_settings:
    context.update({'site_settings': site_settings})
    site_doc = site_settings.home
  
    if site_doc:
      site_doc.content = helper.templates.unescape(site_doc.content)
      context.update({'site_document': site_doc})

  return response_helpers.respond(request, template, context)


DEF_SITE_HOME_EDIT_TMPL = 'soc/site/home/edit.html'

def edit(request, template=DEF_SITE_HOME_EDIT_TMPL):
  """View for Developer to edit content of Melange site home page.

  Args:
    request: the standard django request object.
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """
  # create default template context for use with any templates
  context = response_helpers.getUniversalContext(request)
  
  logged_in_id = users.get_current_user()
  
  alt_response = simple.getAltResponseIfNotDeveloper(request, context, 
                                                     id=logged_in_id)
  if alt_response:
    # not a developer
    return alt_response
  
  alt_response = simple.getAltResponseIfNotLoggedIn(request, context, 
                                                    id=logged_in_id)
  if alt_response:
    # not logged in
    return alt_response
  
  alt_response = simple.getAltResponseIfNotUser(request, context, 
                                                        id = logged_in_id)
  if alt_response:
    # no existing User entity for logged in Google Account. User entity is 
    # required for creating Documents
    return alt_response
                             
  settings_form = None
  document_form = None

  if request.method == 'POST':
    document_form = DocumentForm(request.POST)
    settings_form = SiteSettingsForm(request.POST)

    if document_form.is_valid() and settings_form.is_valid():
      title = document_form.cleaned_data.get('title')
      link_name = DEF_SITE_HOME_DOC_LINK_NAME
      short_name = document_form.cleaned_data.get('short_name')
      abstract = document_form.cleaned_data.get('abstract')
      content = document_form.cleaned_data.get('content')
      
      site_doc = soc.logic.document.updateOrCreateDocument(
          partial_path=DEF_SITE_SETTINGS_PATH, link_name=link_name,
          title=title, short_name=short_name, abstract=abstract,
          content=content, user=id_user.getUserFromId(logged_in_id))
      
      feed_url = settings_form.cleaned_data.get('feed_url')

      site_settings = soc.logic.site.settings.updateOrCreateSiteSettings(
          DEF_SITE_SETTINGS_PATH, home=site_doc, feed_url=feed_url)
      
      context.update({'submit_message': 'Site Settings saved.'})
  else: # request.method == 'GET'
    # try to fetch SiteSettings entity by unique key_name
    site_settings = soc.logic.site.settings.getSiteSettings(
        DEF_SITE_SETTINGS_PATH)

    if site_settings:
      # populate form with the existing SiteSettings entity
      settings_form = SiteSettingsForm(instance=site_settings)
      site_doc = site_settings.home
    else:
      # no SiteSettings entity exists for this key_name, so show a blank form
      settings_form = SiteSettingsForm()
      site_doc = None

    if site_doc:
      # populate form with the existing Document entity
      document_form = DocumentForm(instance=site_doc)
    else:
      # no Document entity exists for this key_name, so show a blank form
      document_form = DocumentForm()
      
  context.update({'document_form': document_form,
                  'settings_form': settings_form })
  
  return response_helpers.respond(request, template, context)
