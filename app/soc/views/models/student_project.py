#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""Views for Student Project.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import responses
from soc.views.models import base

from soc.modules.gsoc.logic.models.student_project import logic as \
    student_project_logic

class View(base.View):
  """View methods for the Student Project model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = student_project_logic
    new_params['name'] = "Student Project"
    new_params['url_name'] = "student_project"

    patterns = [
        (r'^%(url_name)s/(?P<access_type>manage_overview)/%(scope)s$',
        'soc.views.models.%(module_name)s.manage_overview',
        'Overview of %(name_plural)s to Manage for'),
        (r'^%(url_name)s/(?P<access_type>manage)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.manage',
        'Manage %(name)s'),
        (r'^%(url_name)s/(?P<access_type>st_edit)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.st_edit',
        'Edit my %(name)s'),
        (r'^%(url_name)s/(?P<access_type>withdraw)/'
          '(?P<scope_path>%(ulnp)s)/%(lnp)s$',
        'soc.views.models.%(module_name)s.withdraw',
        'Withdraw %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>withdraw_project)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.withdraw_project',
        'Withdraw a %(name)s'),
        (r'^%(url_name)s/(?P<access_type>accept_project)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.accept_project',
        'Accept a %(name)s'),
    ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

accept_project = responses.redirectLegacyRequest
admin = responses.redirectLegacyRequest
create = responses.redirectLegacyRequest
delete = responses.redirectLegacyRequest
edit = responses.redirectLegacyRequest
list = responses.redirectLegacyRequest
manage = responses.redirectLegacyRequest
manage_overview = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
st_edit = responses.redirectLegacyRequest
export = responses.redirectLegacyRequest
pick = responses.redirectLegacyRequest
withdraw = responses.redirectLegacyRequest
withdraw_project = responses.redirectLegacyRequest
