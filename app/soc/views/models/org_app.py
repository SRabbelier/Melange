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

"""Views for Organization App profiles.
"""

__authors__ = [
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import models as model_logic
from soc.logic.models import org_app as org_app_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.models import group_app
from soc.views.models import program as program_view

import soc.logic.dicts


class View(group_app.View):
  """View methods for the Organization Application model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['delete'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic]),
                       ('checkIsActivePeriod', ['org_signup', 'scope_path'])]
    rights['edit'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic]),
                       ('checkIsActivePeriod', ['org_signup', 'scope_path'])]
    rights['list'] = ['checkIsDeveloper']
    rights['public'] = [('checkCanEditGroupApp',
                       [org_app_logic.logic])]
    # TODO(ljvderijk) fix host access check
    rights['review'] = ['checkIsHostForProgram',
                        ('checkCanReviewGroupApp', [org_app_logic.logic])]
    rights['review_overview'] = ['checkIsDeveloper']
    rights['apply'] = ['checkIsUser',
                             ('checkCanCreateOrgApp', ['org_signup'])]

    new_params = {}

    new_params['rights'] = rights
    new_params['logic'] = org_app_logic.logic

    new_params['scope_view'] = program_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['sidebar_grouping'] = 'Organizations'

    patterns = [(r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.views.models.%(module_name)s.create',
        'Create an %(name_plural)s'),]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['applicant', 'backup_admin', 'status',
        'created_on', 'last_modified_on']

    new_params['create_extra_dynafields'] = {
        'scope_path': forms.fields.CharField(widget=forms.HiddenInput,
                                             required=True),
        'clean': cleaning.validate_new_group('link_id', 'scope_path',
            model_logic.organization, org_app_logic)}

    # get rid of the clean method
    new_params['edit_extra_dynafields'] = {
        'clean': (lambda x: x.cleaned_data)}

    new_params['name'] = "Organization Application"
    new_params['name_plural'] = "Organization Applications"
    new_params['name_short'] = "Org App"
    new_params['url_name'] = "org_app"
    new_params['group_url_name'] = 'org'

    new_params['review_template'] = 'soc/org_app/review.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export
review = view.review
review_overview = view.reviewOverview

