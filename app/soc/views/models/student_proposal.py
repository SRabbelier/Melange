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
from django import http

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import organization as org_logic
from soc.logic.models import student as student_logic
from soc.logic.models import user as user_logic
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import params as params_helper
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
    rights['list_orgs'] = [
        ('checkIsStudent', ['scope_path', ['active']]),
        ('checkCanStudentPropose', 'scope_path')]
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
        'soc.views.models.%(module_name)s.apply',
        'Create a new %(name)s'),
        (r'^%(url_name)s/(?P<access_type>list_self)/%(scope)s$',
        'soc.views.models.%(module_name)s.list_self',
        'List my %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>list_orgs)/%(scope)s$',
        'soc.views.models.%(module_name)s.list_orgs',
        'List my %(name_plural)s')
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['org', 'program', 'score',
                                       'status', 'mentor', 'link_id',]

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

    new_params['edit_template'] = 'soc/student_proposal/edit.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

    # create the special form for students
    dynafields = [
        {'name': 'organization',
         'base': forms.CharField,
         'label': 'Organization Link ID',
         'widget': widgets.ReadOnlyInput(),
         'required': False,
         },
        ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    student_create_form = dynaform.extendDynaForm(
        dynaform=self._params['create_form'],
        dynaproperties=dynaproperties)

    params['student_create_form'] = student_create_form


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
  @decorators.check_access
  def apply(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Special view used to prepopulate the form with the organization
       contributors template.

       For params see base.View.public()
    """
    get_dict = request.GET

    if get_dict.get('organization'):
      # organization chosen, prepopulate with template

      # get the organization
      student_entity = student_logic.logic.getFromKeyName(kwargs['scope_path'])
      program_entity = student_entity.scope

      filter = {'link_id': get_dict['organization'],
                'scope': program_entity}

      org_entity = org_logic.logic.getForFields(filter, unique=True)

      if org_entity:
        # organization found use special form
        params['create_form'] = params['student_create_form']
        kwargs['content'] = org_entity.contrib_template

    # Create page is an edit page with no key fields
    empty_kwargs = {}
    fields = self._logic.getKeyFieldNames()
    for field in fields:
      empty_kwargs[field] = None

    return super(View, self).edit(request, access_type, page_name=page_name,
                     params=params, seed=kwargs, **empty_kwargs)

  @decorators.merge_params
  @decorators.check_access
  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """If the POST contains (action, Withdraw) the proposal in kwargs
       will be marked as invalid.

    For params see base.View.edit()
    """

    # check if request.POST contains action
    post_dict = request.POST
    if 'action' in post_dict and post_dict['action'] == 'Withdraw':
      # withdraw this proposal
      filter = {'scope_path': kwargs['scope_path'],
                'link_id': kwargs['link_id']}

      proposal_logic = params['logic']
      student_proposal_entity = proposal_logic.getForFields(filter, unique=True)

      # update the entity mark it as invalid
      proposal_logic.updateEntityProperties(student_proposal_entity,
          {'status': 'invalid'})

      # redirect to the program's homepage
      redirect_url = redirects.getHomeRedirect(student_proposal_entity.program,
          {'url_name': 'program'})

      return http.HttpResponseRedirect(redirect_url)

    return super(View, self).edit(request=request, access_type=access_type,
           page_name=page_name, params=params, seed=seed, **kwargs)

  @decorators.merge_params
  @decorators.check_access
  def listOrgs(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Lists all organization which the given student can propose to.

    For params see base.View.public().
    """

    from soc.views.models import organization as org_view

    student_entity = student_logic.logic.getFromKeyName(kwargs['scope_path'])

    filter = {'scope' : student_entity.scope,
              'status': 'active'}

    list_params = org_view.view.getParams().copy()
    list_params['list_description'] = ('List of %(name_plural)s you can send '
        'your proposal to.') % list_params
    list_params['list_action'] = (redirects.getStudentProposalRedirect,
        {'student_key': student_entity.key().name(),
            'url_name': params['url_name']})

    return self.list(request, access_type=access_type, page_name=page_name,
                     params=list_params, filter=filter, **kwargs)

  @decorators.merge_params
  @decorators.check_access
  def listSelf(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Lists all proposals from the current logged-in user for the given student.

    For params see base.View.public().
    """

    student_entity = student_logic.logic.getFromKeyName(kwargs['scope_path'])

    filter = {'scope' : student_entity,
              'status': ['new', 'pending', 'accepted', 'rejected']}

    list_params = params.copy()
    list_params['list_description'] = 'List of my %(name_plural)s' % list_params

    return self.list(request, access_type=access_type, page_name=page_name,
                     params=list_params, filter=filter, **kwargs)

view = View()

admin = decorators.view(view.admin)
apply = decorators.view(view.apply)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_orgs = decorators.view(view.listOrgs)
list_self = decorators.view(view.listSelf)
public = decorators.view(view.public)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
