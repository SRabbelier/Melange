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
from soc.logic.models import user as user_logic
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

    rights = access.Checker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkCanStudentPropose', 'scope_path'),
        ('checkRoleAndStatusForStudentProposal',
            [['proposer'], ['active'], ['new', 'pending']])]
    rights['delete'] = ['checkIsDeveloper']
    rights['show'] = [
        ('checkRoleAndStatusForStudentProposal',
            [['proposer', 'org_admin', 'mentor', 'host'], 
            ['active', 'inactive'], ['new', 'pending', 'accepted', 'rejected']])]
    rights['list'] = ['checkIsDeveloper']
    rights['list_self'] = [
        ('checkIsStudent', ['scope_path', ['active', 'inactive']])]
    rights['apply'] = [
        ('checkIsStudent', ['scope_path', ['active']]),
        ('checkCanStudentPropose', 'scope_path')]

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
        (r'^%(url_name)s/(?P<access_type>list_self)/%(scope)s$',
        'soc.views.models.%(module_name)s.list_self',
        'List my %(name_plural)s')
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['org', 'program', 'score',
                                       'status', 'mentor', 'link_id']

    new_params['create_extra_dynaproperties'] = {
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

    new_params['edit_extra_dynaproperties'] = {
        'organization': forms.CharField(label='Organization Link ID',
            widget=widgets.ReadOnlyInput),
        'link_id': forms.CharField(widget=forms.HiddenInput)
        }

    # TODO(ljvderijk) students should be able to withdraw their proposals

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

  @decorators.merge_params
  def listSelf(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Lists all proposals from the current logged-in user.

    For params see base.View.public().
    """

    user_entity = user_logic.logic.getForCurrentAccount()
    filter = {'user': user_entity}
    student_entity = student_logic.logic.getForFields(filter, unique=True)

    filter = {'scope' : student_entity,
              'status': ['new', 'pending', 'accepted', 'rejected']}

    list_params = params.copy()
    list_params['list_description'] = 'List of my %(name_plural)s' % list_params

    return self.list(request, access_type=access_type, page_name=page_name,
                     params=list_params, filter=filter, **kwargs)

view = View()

admin = view.admin
create = view.create
delete = view.delete
edit = view.edit
list = view.list
list_self = view.listSelf
public = view.public
export = view.export
pick = view.pick
