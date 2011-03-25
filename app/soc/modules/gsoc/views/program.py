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

"""Module for the program settings pages.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django.conf.urls.defaults import url
from django.core.urlresolvers import reverse

from soc.logic.models.document import logic as document_logic
from soc.views.forms import ModelForm

from soc.modules.gsoc.models.program import GSoCProgram
from soc.modules.gsoc.views.base import RequestHandler
from soc.modules.gsoc.views.helper import url_patterns


class ProgramForm(ModelForm):
  """Django form for the program settings.
  """

  class Meta:
    css_prefix = 'program_form'
    model = GSoCProgram
    exclude = ['link_id', 'scope', 'scope_path', 'timeline', 'home', 'slots_allocation']


class ProgramPage(RequestHandler):
  """View for the participant profile.
  """

  def djangoURLPatterns(self):
    return [
        url(r'^gsoc/program/edit/%s$' % url_patterns.PROGRAM, self,
            name='edit_gsoc_program'),
    ]

  def jsonContext(self):
    entities = document_logic.getForFields({
        'prefix': 'gsoc_program',
        'scope': self.data.program.key()
    })

    data = [{'key': str(i.key()),
            'link_id': i.link_id,
            'label': i.title}
            for i in entities]

    return {'data': data}

  def checkAccess(self):
    self.check.isHost()

  def templatePath(self):
    return 'v2/modules/gsoc/program/base.html'

  def context(self):
    program_form = ProgramForm(self.data.POST or None, instance=self.data.program)
    return {
        'page_name': 'Edit program settings',
        'program_form': program_form,
    }

  def validate(self):
    program_form = ProgramForm(self.data.POST, instance=self.data.program)

    if not program_form.is_valid():
      return False

    program_form.save()

  def post(self):
    """Handler for HTTP POST request.
    """
    if self.validate():
      self.redirect.program()
      self.redirect.to('edit_program_settings')
    else:
      self.get()
