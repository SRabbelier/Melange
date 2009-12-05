#!/usr/bin/python2.5
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

"""Views for Student Proposal.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.logic.models.student_proposal import logic as student_proposal_logic
from soc.views.helper import responses
from soc.views.models import base


class View(base.View):
  """View methods for the Student Proposal model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    new_params = {}
    new_params['logic'] = student_proposal_logic
    new_params['name'] = "Student Proposal"
    new_params['url_name'] = "student_proposal"

    patterns = [
        (r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.views.models.%(module_name)s.apply',
        'Create a new %(name)s'),
        (r'^%(url_name)s/(?P<access_type>list_self)/%(scope)s$',
        'soc.views.models.%(module_name)s.list_self',
        'List my %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>list_orgs)/%(scope)s$',
        'soc.views.models.%(module_name)s.list_orgs',
        'List my %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>review)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.review',
        'Review %(name)s'),
    ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

admin = responses.redirectLegacyRequest
apply = responses.redirectLegacyRequest
create = responses.redirectLegacyRequest
delete = responses.redirectLegacyRequest
edit = responses.redirectLegacyRequest
list = responses.redirectLegacyRequest
list_orgs = responses.redirectLegacyRequest
list_self = responses.redirectLegacyRequest
public = responses.redirectLegacyRequest
review = responses.redirectLegacyRequest
export = responses.redirectLegacyRequest
pick = responses.redirectLegacyRequest
