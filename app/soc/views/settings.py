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

"""Home page settings views.

edit: settings view for authorized Developers, Administrators, etc.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  ]


from google.appengine.ext import db

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import models
from soc.logic import validate
from soc.logic.models import document
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators

import soc.logic.models.home_settings
import soc.models.document
import soc.models.home_settings
import soc.models.work
import soc.views.helper.forms
import soc.views.helper.responses
import soc.views.helper.templates
import soc.views.helper.widgets
import soc.views.out_of_band


class SettingsValidationForm(helper.forms.BaseForm):
  """Django form displayed when creating or editing Settings.
  
  This form includes validation functions for Settings fields.
  """

  def clean_feed_url(self):
    feed_url = self.cleaned_data.get('feed_url')

    if feed_url == '':
      # feed url not supplied (which is OK), so do not try to validate it
      return None
    
    if not validate.isFeedURLValid(feed_url):
      raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

    return feed_url


class SettingsForm(SettingsValidationForm):
  """Django form displayed when creating or editing Settings.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """
    #: db.Model subclass for which the form will gather information
    model = soc.models.home_settings.HomeSettings

    #: list of model fields which will *not* be gathered by the form
    exclude = ['inheritance_line', 'home']


class DocSelectForm(helper.forms.BaseForm):
  """Django form displayed to select a Document.
  """

  # TODO(tlarsen): partial_path will be a hard-coded read-only
  #   field for some (most?) User Roles
  partial_path = forms.CharField(required=False,
      label=soc.models.work.Work.partial_path.verbose_name,
      help_text=soc.models.work.Work.partial_path.help_text)

  # TODO(tlarsen): actually, using these two text fields to specify
  #   the Document is pretty cheesy; this needs to be some much better
  #   Role-scoped Document selector that we don't have yet
  link_name = forms.CharField(required=False,
      label=soc.models.work.Work.link_name.verbose_name,
      help_text=soc.models.work.Work.link_name.help_text)

  class Meta:
    model = None


DEF_HOME_EDIT_TMPL = 'soc/settings/edit.html'

@decorators.view
def edit(request, page=None, path=None, logic=models.home_settings.logic,
         settings_form_class=SettingsForm,
         template=DEF_HOME_EDIT_TMPL):
  """View for authorized User to edit contents of a home page.

  Args:
    request: the standard django request object.
    page: a soc.logic.site.page.Page object which is abstraction that
      combines a Django view with sidebar menu info
    path: path that is used to uniquely identify settings
    logic: settings logic object
    settings_form_class:
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse with generated template.
  """

  try:
    access.checkIsDeveloper(request)
  except  soc.views.out_of_band.AccessViolationResponse, alt_response:
    # TODO(tlarsen): change this to just limit Settings paths that can be
    #   viewed or modified by the User in their current Role
    return alt_response.response()

  # create default template context for use with any templates
  context = helper.responses.getUniversalContext(request)
  context['page'] = page

  settings_form = None
  doc_select_form = None
  home_doc = None

  if request.method == 'POST':
    settings_form = settings_form_class(request.POST)
    doc_select_form = DocSelectForm(request.POST)
    
    if doc_select_form.is_valid() and settings_form.is_valid():
      fields = {}
      
      # Ask for all the fields and pull them out 
      for field in settings_form.cleaned_data:
        value = settings_form.cleaned_data.get(field)
        fields[field] = value

      partial_path = doc_select_form.cleaned_data.get('partial_path')
      link_name = doc_select_form.cleaned_data.get('link_name')

      home_doc = document.logic.getFromFields(
          partial_path=partial_path, link_name=link_name)

      if home_doc:
        fields['home'] = home_doc
        context['notice'] = ugettext_lazy('Settings saved.')
      else:
        context['notice'] = ugettext_lazy(
            'Document not specified or could not be found; ' \
            'other Settings saved.')

      key_fields = logic.getKeyFieldsFromDict(fields)
      settings = logic.updateOrCreateFromFields(fields, key_fields)
      
      if settings.home:
        home_doc = settings.home
  else: # request.method == 'GET'
    # try to fetch HomeSettings entity by unique key_name
    settings = logic.getFromFields(path=path)

    if settings:
      # populate form with the existing HomeSettings entity
      settings_form = settings_form_class(instance=settings)

      # check if ReferenceProperty to home Document is valid
      try:
        home_doc = settings.home
      except db.Error:
        pass
    
      if home_doc:
        doc_select_form = DocSelectForm(initial={
            'partial_path': home_doc.partial_path,
            'link_name': home_doc.link_name})
      else:
        doc_select_form = DocSelectForm()
    else:
      # no SiteSettings entity exists for this key_name, so show a blank form
      settings_form = settings_form_class()
      doc_select_form = DocSelectForm()

  context.update({'settings_form': settings_form,
                  'doc_select_form': doc_select_form,
                  'home_doc': home_doc})
  
  return helper.responses.respond(request, template, context)
