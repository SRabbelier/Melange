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

"""Module for the GSoC organization profile page.
"""

__authors__ = [
  '"Daniel Hans" <daniel.m.hans@gmail.com>',
  ]


from soc.views import forms

from django.core.urlresolvers import reverse
from django.conf.urls.defaults import url

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.exceptions import NotFound

from soc.modules.gsoc.models.organization import GSoCOrganization

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class OrgProfileForm(forms.ModelForm):
  """Django form for the organization profile.
  """

  class Meta:
    model = GSoCOrganization
    css_prefix = 'gsoc_org_page'
    exclude = ['status', 'scope', 'scope_path', 'founder', 'founder', 'slots',
               'slots_calculated', 'nr_applications', 'nr_mentors',
               'scoring_disabled', 'link_id']
    widgets = forms.choiceWidgets(GSoCOrganization,
        ['contact_country', 'shipping_country'])

  clean_description = cleaning.clean_html_content('description')
  clean_contrib_template = cleaning.clean_html_content('contrib_template')
  clean_facebook = cleaning.clean_url('facebook')
  clean_twitter = cleaning.clean_url('twitter')
  clean_blog = cleaning.clean_url('blog')
  clean_pub_mailing_list = cleaning.clean_mailto('pub_mailing_list')
  clean_irc_channel = cleaning.clean_irc('irc_channel')


class OrgCreateProfileForm(OrgProfileForm):
  """Django form to create the organization profile.
  """
  
  class Meta:
    model = GSoCOrganization
    css_prefix = 'gsoc_org_page'
    exclude = ['status', 'scope', 'scope_path', 'founder', 'founder', 'slots',
               'slots_calculated', 'nr_applications', 'nr_mentors',
               'scoring_disabled']
    
    widgets = forms.choiceWidgets(GSoCOrganization,
        ['contact_country', 'shipping_country'])
    

class OrgProfilePage(RequestHandler):
  """View for the Organization Profile page.
  """

  def djangoURLPatterns(self):
    return [
         url(r'^gsoc/profile/organization/%s$' % url_patterns.PROGRAM,
         self, name='create_gsoc_org_profile'),
         url(r'^gsoc/profile/organization/%s$' % url_patterns.ORG,
         self, name='edit_gsoc_org_profile'),
    ]

  def checkAccess(self):
    self.check.isLoggedIn()
    self.check.isProgramActive()

    if 'organization' in self.data.kwargs:
      self.check.isProfileActive()
      key_name = '%s/%s/%s' % (
          self.data.kwargs['sponsor'],
          self.data.kwargs['program'],
          self.data.kwargs['organization']
          )
      self.data.org = GSoCOrganization.get_by_key_name(key_name)
      if not self.data.org:
        NotFound('Organization does not exist.')
      self.check.isOrgAdminForOrganization(self.data.org)
      #probably check if the org is active
    else:
      self.data.org = None
      self.check.fail("Org creation is not supported at this time")

  def templatePath(self):
    return 'v2/modules/gsoc/org_profile/base.html'

  def context(self):
    if not self.data.org:
      form = OrgCreateProfileForm(self.data.POST or None)
    else:
      form = OrgProfileForm(self.data.POST or None, instance=self.data.org)

    return {
        'page_name': "Organization profile",
        'form': form
        }

  def post(self):
    org_profile = self.createOrgProfileFromForm()
    if org_profile:
      self.redirect.organization(org_profile)
      self.redirect.to('edit_gsoc_org_profile')
    else:
      self.get()

  def createOrgProfileFromForm(self):
    """Creates a new organization based on the data inserted in the form.

    Returns:
      a newly created organization entity or None
    """

    if self.data.org:
      form = OrgProfileForm(self.data.POST, instance=self.data.org)
    else:
      form = OrgCreateProfileForm(self.data.POST)

    if not form.is_valid():
      return None

    if not self.data.org:
      form.cleaned_data['founder'] = self.data.user
      form.cleaned_data['scope'] = self.data.program
      form.cleaned_data['scope_path'] = self.data.program.key().name() 
      key_name = '%s/%s' % (
          self.data.program.key().name(),
          form.cleaned_data['link_id']
          )
      entity = form.create(commit=True, key_name=key_name)
      self.data.profile.org_admin_for.append(entity.key())
      self.data.profile.put()
    else:
      entity = form.save(commit=True)

    return entity
