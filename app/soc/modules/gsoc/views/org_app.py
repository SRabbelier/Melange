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

"""Module containing the views for GSoC Organization Application.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from django.conf.urls.defaults import url

from soc.logic.models.org_app_survey import logic as org_app_logic
from soc.views import forms
from soc.views.models.org_app_survey import OrgAppSurveyForm

from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class OrgAppForm(OrgAppSurveyForm, forms.ModelForm):
  """Form for Organization Applications inherited from Surveys.
  """

  #TODO: Rewrite this class while refactoring surveys

  def __init__(self, *args, **kwargs):
    """Act as a bridge between the new Forms APIs and the existing Survey
    Form classes.
    """

    kwargs.update({
        'survey': kwargs.get('instance', None),
        'survey_logic': org_app_logic,
        })

    super(OrgAppForm, self).__init__(*args, **kwargs)


class OrgApp(RequestHandler):
  """View methods for Organization Application Applications.
  """

  def templatePath(self):
    return 'v2/modules/gsoc/org_app/apply.html'

  def djangoURLPatterns(self):
    """Returns the list of tuples for containing URL to view method mapping.
    """

    return [
        url(r'^gsoc/org_app/apply/%s$' % url_patterns.SURVEY, self,
            name='gsoc_org_app_apply')
    ]

  def checkAccess(self):
    """Access checks for GSoC Organization Application.
    """
    pass

  def context(self):
    """Handler to for GSoC Organization Application HTTP get request.
    """

    org_app_keyfields = {
        'prefix': self.kwargs.get('prefix'),
        'scope_path': '%s/%s' % (self.kwargs.get('sponsor'),
                                 self.kwargs.get('program')),
        'link_id': self.kwargs.get('survey'),
        }
    org_app_entity = org_app_logic.getFromKeyFieldsOr404(org_app_keyfields)

    if self.data.request.method == 'POST':
      org_app_form = OrgAppForm(self.data.POST, instance=org_app_entity)
    else:
      org_app_form = OrgAppForm(instance=org_app_entity)

    return {
        'page_name': 'Organization Application',
        'org_app_form': org_app_form,
    }
