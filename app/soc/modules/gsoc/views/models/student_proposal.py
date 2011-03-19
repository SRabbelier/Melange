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

"""Views for Student Proposal.
"""

__authors__ = [
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Leo (Chong Liu)" <HiddenPython@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime
import time

from google.appengine.ext import db

from django import forms
from django import http
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base

from soc.modules.gsoc.logic.models import mentor as mentor_logic
from soc.modules.gsoc.logic.models import org_admin as org_admin_logic
from soc.modules.gsoc.logic.models import organization as org_logic
from soc.modules.gsoc.logic.models import program as program_logic
from soc.modules.gsoc.logic.models import student as student_logic
from soc.modules.gsoc.logic.models import student_proposal as \
    student_proposal_logic
from soc.modules.gsoc.views.models import student as student_view
from soc.modules.gsoc.views.helper import access


class View(base.View):
  """View methods for the Student Proposal model.
  """

  DEF_REVIEW_NOT_APPEARED_MSG = ugettext(
      'Your review has been saved. '
      'However, it may take some time for your review to appear. ' 
      'Please refresh your browser or check back later to view your review.')

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GSoCChecker(params)
    rights['create'] = ['checkIsDeveloper']
    rights['edit'] = [('checkCanStudentPropose', ['scope_path', False]),
        ('checkRoleAndStatusForStudentProposal',
            [['proposer'], ['active'], ['new', 'pending', 'invalid']])]
    rights['delete'] = ['checkIsDeveloper']
    rights['private'] = [
        ('checkRoleAndStatusForStudentProposal',
            [['proposer', 'org_admin', 'mentor', 'host'], 
            ['active', 'inactive'], 
            ['new', 'pending', 'accepted', 'rejected', 'invalid']])]
    rights['show'] = ['checkIsStudentProposalPubliclyVisible']
    rights['comment'] = [
        ('checkRoleAndStatusForStudentProposal',
            [['org_admin', 'mentor', 'host'], 
            ['active', 'inactive'],
            ['new', 'pending', 'accepted', 'rejected', 'invalid']])]
    rights['list'] = ['checkIsDeveloper']
    rights['list_orgs'] = [
        ('checkIsStudent', ['scope_path', ['active']]),
        ('checkCanStudentPropose', ['scope_path', False])]
    rights['list_self'] = [
        ('checkIsStudent', ['scope_path', ['active', 'inactive']])]
    rights['apply'] = [
        ('checkIsStudent', ['scope_path', ['active']]),
        ('checkCanStudentPropose', ['scope_path', True])]
    rights['review'] = [
            ('checkIsBeforeEvent',
            ['accepted_students_announced_deadline', None,
             program_logic.logic]),
            ('checkRoleAndStatusForStudentProposal',
            [['org_admin', 'mentor', 'host'], 
            ['active'],
            ['new', 'pending', 'accepted', 'invalid']])]

    new_params = {}
    new_params['logic'] = student_proposal_logic.logic
    new_params['rights'] = rights
    new_params['name'] = "Student Proposal"
    new_params['url_name'] = "gsoc/student_proposal"
    new_params['module_package'] = 'soc.modules.gsoc.views.models'
    new_params['sidebar_grouping'] = 'Students'

    new_params['scope_view'] = student_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['no_create_with_key_fields'] = True

    patterns = [
        (r'^%(url_name)s/(?P<access_type>apply)/%(scope)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.apply',
        'Create a new %(name)s'),
        (r'^%(url_name)s/(?P<access_type>list_self)/%(scope)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.list_self',
        'List my %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>list_orgs)/%(scope)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.list_orgs',
        'List my %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>review)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.review',
        'Review %(name)s'),
        (r'^%(url_name)s/(?P<access_type>public)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.public',
        'Public view for %(name)s'),
        (r'^%(url_name)s/(?P<access_type>private)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.private',
        'Private view of %(name)s'),
        (r'^%(url_name)s/(?P<access_type>comment)/%(key_fields)s$',
        'soc.modules.gsoc.views.models.%(module_name)s.comment',
        'Comment view of %(name)s'),
    ]

    new_params['extra_django_patterns'] = patterns

    new_params['extra_dynaexclude'] = ['org', 'program', 'score',
                                       'status', 'mentor', 'link_id',
                                       'possible_mentors']

    new_params['create_extra_dynaproperties'] = {
        'content': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'scope_path': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'organization': forms.CharField(label='Organization Link ID',
            required=True),
        'clean_abstract': cleaning.clean_content_length('abstract'),
        'clean_content': cleaning.clean_html_content('content'),
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

    new_params['comment_template'] = 'soc/student_proposal/comment.html'
    new_params['edit_template'] = 'soc/student_proposal/edit.html'
    new_params['private_template'] = 'soc/student_proposal/private.html'
    new_params['review_template'] = 'soc/student_proposal/review.html'
    new_params['public_template'] = 'soc/student_proposal/public.html'
    new_params['review_after_deadline_template'] = \
        'soc/student_proposal/review_after_deadline.html'

    new_params['public_field_extra'] = lambda entity: {
        "student": entity.scope.name(),
        "organization_name": entity.org.name,
    }
    new_params['public_field_keys'] = [
        "title", "student", "organization_name", "last_modified_on",
    ]
    new_params['public_field_names'] = [
        "Title", "Student", "Organization Name", "Last Modified On",
    ]

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

    self._params['student_create_form'] = student_create_form

    # create the special form for public review
    base_fields = [
        {'name': 'comment',
         'base': forms.CharField,
         'widget': widgets.FullTinyMCE(attrs={'rows': 10, 'cols': 40}),
         'label': 'Comment',
         'required': False,
         'example_text': 'Caution, you will not be able to edit your comment!',
         },
         ]

    dynafields = [field.copy() for field in base_fields]
    dynaproperties = params_helper.getDynaFields(dynafields)
    dynaproperties['clean_comment'] = cleaning.clean_html_content('comment')

    public_review_form = dynaform.newDynaForm(dynamodel=None, 
        dynabase=helper.forms.BaseForm, dynainclude=None, 
        dynaexclude=None, dynaproperties=dynaproperties)
    self._params['public_review_form'] = public_review_form

    # create the special form for mentors when the scoring is locked

    # this fields is used by the on-page JS
    base_fields.append(
        {'name': 'public',
         'base': forms.BooleanField,
         'label': 'Review visible to Student',
         'initial': False,
         'required': False,
         'help_text': 'By ticking this box the score will not be assigned, '
             'and the review will be visible to the student.',
         })

    dynafields = [field.copy() for field in base_fields]
    dynaproperties = params_helper.getDynaFields(dynafields)
    dynaproperties['clean_comment'] = cleaning.clean_html_content('comment')
    locked_review_form = dynaform.newDynaForm(dynamodel=None, 
        dynabase=helper.forms.BaseForm, dynainclude=None, 
        dynaexclude=None, dynaproperties=dynaproperties)
    self._params['locked_review_form'] = locked_review_form

    # create the form for mentors when the scoring is unlocked
    base_fields.append(
        {'name': 'score',
         'base': forms.ChoiceField,
         'label': 'Score',
         'initial': 0,
         'required': False,
         'passthrough': ['initial', 'required', 'choices'],
         'choices': [(-4,'-4'),
                     (-3,'-3'),
                     (-2,'-2'),
                     (-1,'-1'),
                     (0,'No score'),
                     (1,'1'),
                     (2,'2'),
                     (3,'3'),
                     (4,'4')]
        })

    dynafields = [field.copy() for field in base_fields]
    dynaproperties = params_helper.getDynaFields(dynafields)
    dynaproperties['clean_comment'] = cleaning.clean_html_content('comment')
    mentor_review_form = dynaform.newDynaForm(dynamodel=None, 
        dynabase=helper.forms.BaseForm, dynainclude=None, 
        dynaexclude=None, dynaproperties=dynaproperties)
    self._params['mentor_review_form'] = mentor_review_form
    self._show_review_not_appeared_msg = False

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
      fields['link_id'] = 't%i' % (int(time.time()*100))
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

  @decorators.merge_params
  @decorators.check_access
  def public(self, request, access_type, page_name=None, params=None, **kwargs):
    """View which allows the student to show his or her proposal to other
    users. Anyway, they can only see the content of the proposal itself,
    without comments, scores, etc.
    
    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])

    context['entity'] = entity
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']
    context['page_name'] = 'Proposal titled "%s" from %s' % (
        entity.title, entity.scope.name())
    context['student_name'] = entity.scope.name()

    template = params['public_template']

    return responses.respond(request, template, context=context)

  @decorators.merge_params
  @decorators.check_access
  def private(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View in which the student can see and reply to the comments on the
       Student Proposal.

    For params see base.view.Public().
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['entity'] = entity
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']
    context['page_name'] = 'Proposal titled "%s" from %s' % (
        entity.title, entity.scope.name())

    if request.method == 'POST':
      return self.privatePost(request, context, params, entity, **kwargs)
    else: # request.method == 'GET'
      return self.privateGet(request, context, params, entity, **kwargs)

  def privatePost(self, request, context, params, entity, **kwargs):
    """Handles the POST request for the entity's public page.

    Args:
        entity: the student proposal entity
        rest: see base.View.public()
    """

    # populate the form using the POST data
    form = params['public_review_form'](request.POST)

    if not form.is_valid():
      # get some entity specific context
      self.updatePrivateContext(context, entity, params)

      # return the invalid form response
      return self._constructResponse(request, entity=entity, context=context,
          form=form, params=params, template=params['public_template'])

    # get the commentary
    fields = form.cleaned_data
    comment = fields['comment']

    if comment:
      # create the review
      self._createReviewFor(entity, comment, is_public=True)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def privateGet(self, request, context, params, entity, **kwargs):
    """Handles the GET request for the entity's public page.

    Args:
        entity: the student proposal entity
        rest see base.View.public()
    """

    from soc.modules.gsoc.logic.models.review_follower import logic as \
        review_follower_logic

    get_dict = request.GET

    if get_dict.get('subscription') and (
      get_dict['subscription'] in ['on', 'off']):

      subscription = get_dict['subscription']

      # get the current user
      user_entity = user_logic.logic.getCurrentUser()

      # create the fields that should be in the ReviewFollower entity
      # pylint: disable=E1103
      fields = {'link_id': user_entity.link_id,
                'scope': entity,
                'scope_path': entity.key().id_or_name(),
                'user': user_entity
               }
      # get the keyname for the ReviewFollower entity
      key_name = review_follower_logic.getKeyNameFromFields(fields)

      # determine if we should set subscribed_public to True or False
      if subscription == 'on':
        fields['subscribed_public'] = True
      elif subscription == 'off':
        fields['subscribed_public'] = False

      # update the ReviewFollower
      review_follower_logic.updateOrCreateFromKeyName(fields, key_name)

    # get some entity specific context
    self.updatePrivateContext(context, entity, params)

    context['form'] = params['public_review_form']()
    template = params['private_template']

    return responses.respond(request, template, context=context)

  def updatePrivateContext(self, context, entity, params):
    """Updates the context for the /private page with information 
    from the entity.

    Args:
      context: the context that should be updated
      entity: a student proposal_entity used to set context
      params: dict with params for the view using this context
    """

    from soc.modules.gsoc.logic.models.review import logic as review_logic
    from soc.modules.gsoc.logic.models.review_follower import logic as \
        review_follower_logic

    student_entity = entity.scope

    context['student'] = student_entity
    context['student_name'] = student_entity.name()

    user_entity = user_logic.logic.getCurrentUser()

    # check if the current user is the student
    # pylint: disable=E1103
    if user_entity.key() == student_entity.user.key():
      # show the proposal edit link
      context['edit_link'] = redirects.getEditRedirect(entity, params)

    # check if the current user is subscribed to this proposal's public reviews
    fields = {'user': user_entity,
        'scope': entity,
        'subscribed_public': True}

    context['is_subscribed'] = review_follower_logic.getForFields(fields,
                                                                  unique=True)

    context['public_reviews'] = review_logic.getReviewsForEntity(entity,
        is_public=True, order=['created'])

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
        # organization found use special form and also seed this form
        params['create_form'] = params['student_create_form']
        # pylint: disable=E1103
        kwargs['organization'] = org_entity.link_id
        kwargs['content'] = org_entity.contrib_template

    return super(View, self).create(request, access_type, page_name=page_name,
                     params=params, **kwargs)

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

      comment = "Student withdrew proposal."
      self._createReviewFor(student_proposal_entity, comment)
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

    from soc.modules.gsoc.views.models import organization as org_view

    student_entity = student_logic.logic.getFromKeyName(kwargs['scope_path'])

    filter = {'scope': student_entity.scope,
              'status': 'active'}

    list_params = org_view.view.getParams().copy()
    list_params['list_description'] = ('List of %(name_plural)s you can send '
        'your proposal to.') % list_params
    list_params['public_row_extra'] = lambda entity: {
        'link': redirects.getStudentProposalRedirect(entity,
        {'student_key': student_entity.key().id_or_name(),
            'url_name': params['url_name']})
    }

    return self.list(request, access_type='allow', page_name=page_name,
                     params=list_params, filter=filter, **kwargs)

  def getListSelfData(self, request, list_params, ip_params, scope_path):
    """Returns the listSelf data.
    """

    student_entity = student_logic.logic.getFromKeyName(scope_path)
    fields = {'scope' : student_entity}

    idx = lists.getListIndex(request)

    if idx == 0:
      fields['status'] = ['new', 'pending', 'accepted', 'rejected']
      params = list_params
    elif idx == 1:
      fields['status'] = 'invalid'
      params = ip_params
    else:
      return lists.getErrorResponse(request, "idx not valid")

    contents = lists.getListData(request, params, fields)

    return lists.getResponse(request, contents)

  @decorators.merge_params
  @decorators.check_access
  def listSelf(self, request, access_type,
               page_name=None, params=None, **kwargs):
    """Lists all proposals from the current logged-in user 
       for the given student.

    For params see base.View.public().
    """

    context = {}

    list_params = params.copy()
    list_params['list_description'] = \
        'List of my %(name_plural)s.' % list_params
    list_params['public_row_extra'] = lambda entity: {
        'link': redirects.getStudentPrivateRedirect(entity, list_params)
    }

    ip_params = list_params.copy() # ineligible proposals

    description = ugettext('List of my ineligible/withdrawn %s.') % (
        ip_params['name_plural'])

    ip_params['list_description'] = description
    ip_params['public_row_extra'] = lambda entity: {
        'link': redirects.getPublicRedirect(entity, ip_params)
    }

    if lists.isDataRequest(request):
      scope_path = kwargs['scope_path']
      return self.getListSelfData(request, list_params, ip_params, scope_path)

    valid_list = lists.getListGenerator(request, list_params, idx=0)
    ip_list = lists.getListGenerator(request, ip_params, idx=1)

    contents = [valid_list, ip_list]

    return self._list(request, list_params, contents, page_name, context)

  @decorators.merge_params
  @decorators.check_access
  def review(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View that allows Organization Admins and Mentors to review the proposal.

       For Args see base.View.public().
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = '%s "%s" from %s' % (page_name, entity.title,
                                                entity.scope.name())
    context['entity'] = entity
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']
    if self._show_review_not_appeared_msg:
      context['header_msg'] = self.DEF_REVIEW_NOT_APPEARED_MSG
      self._show_review_not_appeared_msg = False

    # get the roles important for reviewing an application
    filter = {
        'user': user_logic.logic.getCurrentUser(),
        'scope': entity.org,
        'status': 'active'
        }

    org_admin_entity = org_admin_logic.logic.getForFields(filter, unique=True)
    mentor_entity = mentor_logic.logic.getForFields(filter, unique=True)

    # decide which form to use
    if org_admin_entity:
      # create a form for admin review
      # it is done here, because of the dynamic choices list for the mentors

      # firstly, get the list of all possible mentors to assign
      choices = []
      choices.append(('', 'No mentor'))

      # prefer those mentors who volunteer to mentor this proposal 
      filter = {
          '__key__': entity.possible_mentors
          }
      order = ['name_on_documents']
      possible_mentors = mentor_logic.logic.getForFields(filter, order=order)
      for mentor in possible_mentors:
        choices.append((mentor.link_id, mentor.document_name()))

      # also list the rest of the mentors
      filter = {
          'scope': entity.org
          }
      all_mentors = mentor_logic.logic.getForFields(filter, order=order)
      for mentor in all_mentors:
        if mentor.key() in entity.possible_mentors:
          continue
        choices.append((mentor.link_id, mentor.document_name()))

      dynafields = [
        {'name': 'rank',
           'base': forms.IntegerField,
           'label': 'Set to rank',
           'help_text':
               'Set this proposal to the given rank (ignores the given score)',
           'min_value': 1,
           'required': False,
           'passthrough': ['min_value', 'required', 'help_text'],
        },
        {'name': 'mentor',
         'base': forms.ChoiceField,
         'passthrough': ['initial', 'required', 'choices'],
         'label': 'Assign Mentor',
         'choices': choices,
         'required': False,
         'help_text': 'Choose the mentor you would like to assign to this '
             'Proposal. Choose "No mentor" if you don\'t want any '
             'mentor assigned.'
         },
        ]

      dynaproperties = params_helper.getDynaFields(dynafields)
      dynaproperties['clean_comment'] = cleaning.clean_html_content('comment')

      form = dynaform.extendDynaForm(
          dynaform=params['mentor_review_form'], 
          dynaproperties=dynaproperties)

    else:
      # the current user is not an org admin
      if entity.org.scoring_disabled:
        # reviews are disabled, don't show score field
        form = params['locked_review_form']
      else:
        # reviews are enabled, show the score field
        form = params['mentor_review_form']

    if request.method == 'POST':
      return self.reviewPost(request, context, params, entity,
                             form, org_admin_entity, mentor_entity, **kwargs)
    else:
      # request.method == 'GET'
      return self.reviewGet(request, context, params, entity,
                            form, org_admin_entity, mentor_entity, **kwargs)

  def reviewPost(self, request, context, params, entity, form,
                 org_admin, mentor, **kwargs):
    """Handles the POST request for the proposal review view.

    Args:
        entity: the student proposal entity
        form: the form to use in this view
        org_admin: org admin entity for the current user/proposal (iff available)
        mentor: mentor entity for the current user/proposal (iff available)
        rest: see base.View.public()
    """

    from soc.modules.gsoc.tasks.proposal_review import run_create_review_for

    post_dict = request.POST

    if post_dict.get('subscribe') or post_dict.get('unsubscribe'):
      self._handleSubscribePost(request, entity)
      return http.HttpResponseRedirect('')
    elif post_dict.get('want_mentor'):
      # Check if the current user is a mentor
      if mentor:
        self._adjustPossibleMentors(entity, mentor)
      return http.HttpResponseRedirect('')
    elif post_dict.get('ineligble'):
      self._handleIneligiblePost(request, entity)

      redirect = redirects.getListProposalsRedirect(
          entity.org, {'url_name': 'gsoc/org'})
      return http.HttpResponseRedirect(redirect)

    # populate the form using the POST data
    form = form(post_dict)

    if not form.is_valid():
      # return the invalid form response
      # get all the extra information that should be in the context
      review_context = self._getDefaultReviewContext(entity, org_admin, mentor)
      context = dicts.merge(context, review_context)

      return self._constructResponse(request, entity=entity, context=context,
          form=form, params=params, template=params['review_template'])

    fields = form.cleaned_data
    user = user_logic.logic.getCurrentUser()
    # Adjust mentor if necessary
    # NOTE: it cannot be put in the same transaction with student_proposal 
    # since they are not in the same entity group
    if org_admin and 'org_admin_action' in request.POST:
      prev_mentor = entity.mentor.key() if entity.mentor else None
      # org admin found, try to adjust the assigned mentor
      self._adjustMentor(entity, fields['mentor'])
      current_mentor = entity.mentor.key() if entity.mentor else None
      mentor_changed = False
      if prev_mentor != current_mentor:
        mentor_name = entity.mentor.name() if entity.mentor else 'None'
        mentor_changed = True
    # try to see if the rank is given and adjust the given_score if needed
    # NOTE: it cannot be put in the same transaction with student_proposal 
    # since they are not in the same entity group
    rank = fields['rank']
    if rank:
      ranker = self._logic.getRankerFor(entity)
      # if a very high rank is filled in use the highest 
      # one that returns a score
      rank = min(ranker.TotalRankedScores(), rank)
      # ranker uses zero-based ranking
      (scores, _) = ranker.FindScore(rank-1)
      # since we only use one score we need it out of the list with scores
      score_at_rank = scores[0]

    # Update student_proposal, rank and review within one transaction
    def txn():
      given_score = fields.get('score')
      # Doing this instead of get('score',0) because fields.get does not use the
      # default argument for u''.
      given_score = int(given_score) if given_score else 0

      is_public = fields['public']

      comment = fields.get('comment')
      comment = comment if comment else ''

      # Reload entity in case that it has changed
      current_entity = db.get(entity.key())

      if org_admin and 'org_admin_action' in request.POST:
        # admin actions are not public, so force private comment
        is_public = False

        if mentor_changed:
          comment = '%s Changed mentor to %s.' %(comment, mentor_name)

        # try to see if the rank is given and adjust the given_score if needed
        if rank:
          # calculate the score that should be given to end up at the given rank
          # give +1 to make sure that in the case of a tie they end up top
          given_score = score_at_rank - current_entity.score + 1
          comment = '%s Proposal has been set to rank %i.' %(comment, rank)

      # store the properties to update the proposal with
      properties = {}

      if (org_admin or mentor) and (not is_public) and (given_score is not 0):
        # if it is not a public comment and it's made by a member of the
        # organization we update the score of the proposal
        new_score = given_score + current_entity.score
        properties = {'score': new_score}

      if comment or (given_score is not 0):
        # if the proposal is new we change it status to pending
        if current_entity.status == 'new':
          properties['status'] = 'pending'

        # create a review for current_entity using taskqueue
        run_create_review_for(current_entity, comment, given_score, 
                              is_public, user, self._params)
      if properties.values():
        # there is something to update
        self._logic.updateEntityProperties(current_entity, properties)

    db.run_in_transaction(txn)
    # Inform users that review may not appear immediately
    self._show_review_not_appeared_msg = True
    # redirect to the same page
    return http.HttpResponseRedirect('')

  def reviewGet(self, request, context, params, entity, form,
                 org_admin, mentor, **kwargs):
    """Handles the GET request for the proposal review view.

    Args:
        entity: the student proposal entity
        form: the form to use in this view
        org_admin: org admin entity for the current user/proposal (iff available)
        mentor: mentor entity for the current user/proposal (iff available)
        rest: see base.View.public()
    """

    initial = {}

    # set the initial score since the default is ignored
    initial['score'] = 0

    # set initial values for fields that are available only for org admins
    if org_admin and entity.mentor:
      initial['mentor'] = entity.mentor.link_id

    context['form'] = form(initial)

    # create the special form for mentors
    comment_public = ['public', 'comment']
    comment_private = ['score']
    comment_admin = ['rank', 'mentor']
    class FilterForm(object):
      """Helper class used for form filtering.
      """
      def __init__(self, form, fields):
        self.__form = form
        self.__fields = fields

      @property
      def fields(self):
        """Property that returns all fields as dictionary."""
        fields = self.__form.fields.iteritems()
        return dict([(k, i) for k, i in fields if k in self.__fields])

      def __iter__(self):
        for field in self.__form:
          if field.name not in self.__fields:
            continue
          yield field

      _marker = []
      def __getattr__(self, key, default=_marker):
        if default is self._marker:
          return getattr(self.__form, key)
        else:
          return getattr(self.__form, key, default)

    context['form'] = form(initial)
    context['comment_public'] = FilterForm(context['form'], comment_public)
    context['comment_private'] = FilterForm(context['form'], comment_private)
    context['comment_admin'] = FilterForm(context['form'], comment_admin)

    # get all the extra information that should be in the context
    review_context = self._getDefaultReviewContext(entity, org_admin, mentor)
    context = dicts.merge(context, review_context)

    template = params['review_template']

    return responses.respond(request, template, context=context)

  @decorators.merge_params
  @decorators.check_access
  def comment(self, request, access_type,
              page_name=None, params=None, **kwargs):
    """View for org admins and mentors which is shown after the student
    application perdiod. The view displays scores, both public and private
    reviews and content of the proposal, but does not allow new scores
    and ranks. 
    
    For Args see base.View.public()
    """

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'])

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = '%s "%s" from %s' % (page_name, entity.title,
        entity.scope.name())
    context['entity'] = entity
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']

    if request.method == 'POST':
      return self.commentPost(request, context, params, entity, **kwargs)
    else:
      # request.method == 'GET'
      return self.commentGet(request, context, params, entity, **kwargs)

  def commentPost(self, request, context, params, entity, **kwargs):
    """Handles the POST request for the proposal comment view.
    """

    post_dict = request.POST

    if post_dict.get('subscribe') or post_dict.get('unsubscribe'):
      self._handleSubscribePost(request, entity)
      return http.HttpResponseRedirect('')

    form = params['public_review_form'](post_dict)

    if not form.is_valid():
      # get some entity specific context
      self.updateCommentContext(context, entity, params)

      # return the invalid form response
      return self._constructResponse(request, entity=entity, context=context,
          form=form, params=params, template=params['comment_template'])

    # get the commentary
    fields = form.cleaned_data
    comment = fields['comment']

    if comment:
      # create the review
      self._createReviewFor(entity, comment, is_public=True)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def commentGet(self, request, context, params, entity, **kwargs):
    """Handles the GET request for the proposal review view.
    """

    self.updateCommentContext(context, entity, params)

    context['form'] = params['public_review_form']()
    template = params['comment_template']

    return responses.respond(request, template, context=context)

  def updateCommentContext(self, context, entity, params):
    """Updates the context for the /comment page with information 
    from the entity.

    Args:
      context: the context that should be updated
      entity: a student proposal_entity used to set context
      params: dict with params for the view using this context
    """

    student_entity = entity.scope

    # update the student data
    context['student'] = student_entity
    context['student_name'] = student_entity.name()

    # update the mentor data
    if entity.mentor:
      context['mentor_name'] = entity.mentor.name()
    else:
      context['mentor_name'] = None

    # update the reviews context
    self._updateReviewsContext(context, entity)

    # update the scores context
    self._updateScoresContext(context, entity)

  def _updateReviewsContext(self, context, entity):
    """Updates the context for the reviews related to a given student proposal.

    Args:
      context: the context that should be updated
      entity: a student proposal_entity used to set context
    """

    from soc.modules.gsoc.logic.models.review import logic as review_logic

    # order the reviews by ascending creation date
    order = ['created']

    # get the public reviews
    public_reviews = review_logic.getReviewsForEntity(entity,
        is_public=True, order=order)

    # get the private reviews
    private_reviews = review_logic.getReviewsForEntity(entity,
        is_public=False, order=order)

    # create a summary of all the private reviews
    review_summary = {}

    for private_review in private_reviews:

      if private_review.score == 0:
        continue

      reviewer = private_review.author

      reviewer_key = reviewer.key().id_or_name()
      reviewer_summary = review_summary.get(reviewer_key)

      if reviewer_summary:
        # we already have something on file for this reviewer
        old_total_score = reviewer_summary['total_score']
        reviewer_summary['total_score'] = old_total_score + private_review.score
        reviewer_summary['individual_scores'].append(private_review.score)

        old_total_comments = reviewer_summary['total_comments']
        reviewer_summary['total_comments'] = old_total_comments + 1
      else:
        # create a new summary for this reviewer
        review_summary[reviewer_key] = {
            'name': reviewer.name,
            'total_comments': 1,
            'total_score': private_review.score,
            'individual_scores': [private_review.score]
            }

    # update the reviews in the context
    context['public_reviews'] = public_reviews
    context['private_reviews'] = private_reviews
    context['review_summary'] = review_summary

  def _updateScoresContext(self, context, entity):
    """Updates the context for the scores related to a given student proposal

    Args:
      context: the context that should be updated
      entity: a student proposal_entity used to set context
    """

    review_summary = context['review_summary']

    score_summary = []
    total_scores = [i['total_score'] for i in review_summary.itervalues()]
    max_score = max(total_scores) if total_scores else 0
    min_score = min(total_scores) if total_scores else 0
    for score in xrange(min_score, max_score + 1):
      # do not display info if the total score is 0
      if not score:
        continue

      number = len([summary for summary in review_summary.itervalues() \
          if summary['total_score'] == score])
      if number:
        score_summary.append({'score': score, 'number': number})
    context['score_summary'] = score_summary

  def _getDefaultReviewContext(self, entity, org_admin,
                               mentor):
    """Returns the default context for the review page.

    Args:
      entity: Student Proposal entity
      org_admin: org admin entity for the current user/proposal (iff available)
      mentor: mentor entity for the current user/proposal (iff available)
    """

    from soc.modules.gsoc.logic.models.proposal_duplicates import logic \
        as duplicates_logic
    from soc.modules.gsoc.logic.models.review_follower import logic as \
        review_follower_logic

    context = {}

    context['student'] = entity.scope
    context['student_name'] = entity.scope.name()

    if entity.mentor:
      context['mentor_name'] = entity.mentor.name()
    else:
      context['mentor_name'] = "No mentor assigned"

    # set the possible mentors in the context
    possible_mentors = entity.possible_mentors

    if not possible_mentors:
      context['possible_mentors'] = "None"
    else:
      mentor_names = []

      for mentor_key in possible_mentors:
        possible_mentor = mentor_logic.logic.getFromKeyName(
            mentor_key.id_or_name())
        mentor_names.append(possible_mentor.name())

      context['possible_mentors'] = ', '.join(mentor_names)

    # update the reviews context
    self._updateReviewsContext(context, entity)

    # update the scores context
    self._updateScoresContext(context, entity)

    if mentor:
      context['is_mentor'] = True
      if not entity.mentor or entity.mentor.key() != mentor.key():
        # which button to (un)propose yourself as mentor should we show
        if mentor.key() in possible_mentors:
          # show "No longer willing to mentor"
          context['remove_me_as_mentor'] = True
        else:
          # show "I am willing to mentor"
          context['add_me_as_mentor'] = True

    if org_admin:
      context['is_org_admin'] = True

      # when the duplicates can be visible obtain the
      # duplicates for this proposal
      if entity.program.duplicates_visible:
        fields = {'student': entity.scope,
                      'is_duplicate': True}

        duplicate_entity = duplicates_logic.getForFields(fields, unique=True)

        if duplicate_entity:
          # this list also contains the current proposal
          # entity, so remove it
          duplicate_keys = duplicate_entity.duplicates
          duplicate_keys.remove(entity.key())
          context['sp_duplicates'] = db.get(duplicate_keys)

    user_entity = user_logic.logic.getCurrentUser()

    # check if the current user is subscribed to public or private reviews
    fields = {'scope': entity,
              'user': user_entity,}
    follower_entity = review_follower_logic.getForFields(fields, unique=True)

    if follower_entity:
      # pylint: disable=E1103
      context['is_subscribed'] =  follower_entity.subscribed_public

    return context

  def _adjustPossibleMentors(self, entity, mentor):
    """Adjusts the possible mentors list for a proposal.

    Args:
      entity: Student Proposal entity
      mentor: Mentor entity
    """

    if not mentor:
      # nothing to do here
      return

    possible_mentors = entity.possible_mentors

    # determine wether we need to add or remove this mentor
    add = mentor.key() not in possible_mentors

    if add:
      # add the mentor to possible mentors list if not already in
      possible_mentors.append(mentor.key())
      fields = {'possible_mentors': possible_mentors}
      self._logic.updateEntityProperties(entity, fields)
    else:
      # remove the mentor from the possible mentors list
      possible_mentors.remove(mentor.key())
      fields = {'possible_mentors': possible_mentors}
      self._logic.updateEntityProperties(entity, fields)

  def _adjustMentor(self, entity, mentor_id):
    """Changes the mentor to the given link_id.

    Args:
      entity: Student Proposal entity
      mentor_id: Link ID of the mentor that needs to be assigned
                 Iff not given then removes the assigned mentor
    """

    if entity.mentor and entity.mentor.link_id == mentor_id:
      # no need to change
      return

    if mentor_id:
      # try to locate the mentor
      fields = {'link_id': mentor_id,
                'scope': entity.org,
                'status': 'active'}

      mentor_entity = mentor_logic.logic.getForFields(fields, unique=True)

      if not mentor_entity:
        # no mentor found, do not update
        return
    else:
      # reset to None
      mentor_entity = None

    properties = {'mentor': mentor_entity}

    if entity.status == 'new':
      # transition to pending status
      properties['status'] = 'pending'

    # update the proposal
    self._logic.updateEntityProperties(entity, properties)

  def _createReviewFor(self, entity, comment, score=0, is_public=True):
    """Creates a review for the given proposal and sends 
       out a message to all followers.

    Args:
      entity: Student Proposal entity for which the review should be created
      comment: The textual contents of the review
      score: The score of the review (only used if the review is not public)
      is_public: Determines if the review is a public review
    """

    user = user_logic.logic.getCurrentUser()
    student_proposal_logic.logic.createReviewFor(self, entity, user, 
                                                 comment, score, is_public)

  def _handleSubscribePost(self, request, entity):
    """Handles the POST request for subscription management.

    Args:
      request: The HTTPRequest object
      entity: The StudentProposal entity to (un)subscribe to
    """

    from soc.modules.gsoc.logic.models.review_follower import logic as \
        review_follower_logic

    post_dict = request.POST

    # check if we should change the subscription state for the current user
    subscribe = None

    if post_dict.get('subscribe'):
      subscribe = True
    elif post_dict.get('unsubscribe'):
      subscribe = False

    if subscribe != None:
      # get the current user
      user_entity = user_logic.logic.getCurrentUser()

      # create the fields that should be in the ReviewFollower entity
      # pylint: disable=E1103
      fields = {'link_id': user_entity.link_id,
                'scope': entity,
                'scope_path': entity.key().id_or_name(),
                'user': user_entity
               }
      # get the keyname for the ReviewFollower entity
      key_name = review_follower_logic.getKeyNameFromFields(fields)

      # set both the subscription properties, this is a requested enhancement
      # see also Issue 538.
      fields['subscribed_public'] = subscribe
      fields['subscribed_private'] = subscribe

      # update the ReviewFollower
      return review_follower_logic.updateOrCreateFromKeyName(fields, key_name)

  def _handleIneligiblePost(self, request, entity):
    """Handles the POST request for eligibilety management.

    Args:
      request: The HTTPRequest object
      entity: The StudentProposal entity to make (in)eligible to
    """

    if not request.POST.get('ineligble'):
      return

    if entity.status not in ['accepted', 'rejeceted', 'invalid']:
      # mark the proposal invalid
      properties = {'status': 'invalid'}
      self._logic.updateEntityProperties(entity, properties)

      comment = "Marked Student Proposal as Ineligible."
      self._createReviewFor(entity, comment, is_public=False)
    elif entity.status == 'invalid':
      # mark the proposal as new
      properties = {'status': 'new'}
      self._logic.updateEntityProperties(entity, properties)

      comment = "Marked Student Proposal as Eligible."
      self._createReviewFor(entity, comment, is_public=False)

    return entity


view = View()

admin = decorators.view(view.admin)
apply = decorators.view(view.apply)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_orgs = decorators.view(view.listOrgs)
list_self = decorators.view(view.listSelf)
comment = decorators.view(view.comment)
public = decorators.view(view.public)
private = decorators.view(view.private)
review = decorators.view(view.review)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
