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


import datetime
import time

from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import organization as org_logic
from soc.logic.models import student as student_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import base
from soc.views.models import student as student_view

import soc.logic.models.student_proposal


class View(base.View):
  """View methods for the Student Proposal model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    # TODO(ljvderijk) Access checks for different views
    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = ['checkIsDeveloper']
    rights['delete'] = ['checkIsDeveloper']
    # TODO(ljvderijk) public should be host/org/student only
    rights['public'] = ['checkIsDeveloper']
    rights['list'] = ['checkIsDeveloper']
    rights['apply'] = ['checkIsDeveloper']

    new_params = {}
    new_params['logic'] = soc.logic.models.student_proposal.logic
    new_params['rights'] = rights
    new_params['name'] = "Student Proposal"
    new_params['url_name'] = "student_proposal"
    new_params['sidebar_grouping'] = 'Student Proposal'

    new_params['scope_view'] = student_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['no_create_with_key_fields'] = True

    patterns = [
        (r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.views.models.%(module_name)s.create',
        'Create a new %(name)s'),
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['org', 'program', 'score',
                                       'status', 'mentor', 'link_id']

    new_params['create_extra_dynafields'] = {
        'content': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'scope_path': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'organization': forms.CharField(label='Organization Link ID',
            required=True),
        'clean_organization': cleaning.clean_link_id('organization'),
        'clean_additional_info': cleaning.clean_url('additional_info'),
        'clean': cleaning.validate_student_proposal('organization',
            'scope_path', student_logic, org_logic),
        }

    new_params['edit_extra_dynafields'] = {
        'organization': forms.CharField(label='Organization Link ID',
            widget=widgets.ReadOnlyInput),
        'link_id': forms.CharField(widget=forms.HiddenInput)
        }

    # TODO(ljvderijk) students should be able to withdraw their proposal

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['link_id'].initial = entity.link_id
    form.fields['organization'].initial = entity.org.link_id

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if not entity:
      fields['link_id'] = 't%i' % (time.time())
    else:
      fields['link_id'] = entity.link_id

    # fill in the scope via call to super
    super(View, self)._editPost(request, entity, fields)

    if not entity:
      # creating a new application so set the program and org field
      fields['program'] = fields['scope'].scope

      filter = {'scope': fields['program'],
                'link_id': fields['organization']}
      fields['org'] = org_logic.logic.getForFields(filter, unique=True)

    # explicitly change the last_modified_on since the content has been edited
    fields['last_modified_on'] = datetime.datetime.now()

  def _public(self, request, entity, context):
    """See base.View._public().
    """

    context['student_name'] = entity.scope.name()

    if entity.mentor:
      context['mentor_name'] = entity.mentor.name()
    else:
      context['mentor_name'] = "No mentor assigned"

view = View()

admin = view.admin
create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export
pick = view.pick
