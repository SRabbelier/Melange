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
from soc.logic.models import mentor as mentor_logic
from soc.logic.models import organization as org_logic
from soc.logic.models import org_admin as org_admin_logic
from soc.logic.models import student as student_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import responses
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
            ['active', 'inactive'], 
            ['new', 'pending', 'accepted', 'rejected']])]
    rights['list'] = ['checkIsDeveloper']
    rights['list_orgs'] = [
        ('checkIsStudent', ['scope_path', ['active']]),
        ('checkCanStudentPropose', 'scope_path')]
    rights['list_self'] = [
        ('checkIsStudent', ['scope_path', ['active', 'inactive']])]
    rights['apply'] = [
        ('checkIsStudent', ['scope_path', ['active']]),
        ('checkCanStudentPropose', 'scope_path')]
    rights['review'] = [('checkRoleAndStatusForStudentProposal',
            [['org_admin', 'mentor', 'host'], 
            ['active'], ['new', 'pending']])]

    new_params = {}
    new_params['logic'] = soc.logic.models.student_proposal.logic
    new_params['rights'] = rights
    new_params['name'] = "Student Proposal"
    new_params['url_name'] = "student_proposal"
    new_params['sidebar_grouping'] = 'Students'

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
        'List my %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>review)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.review',
        'Review %(name)s'),
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
    new_params['review_template'] = 'soc/student_proposal/review.html'

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

    # create the special form for public review
    dynafields = [
        {'name': 'comment',
         'base': forms.CharField,
         'widget': widgets.FullTinyMCE(attrs={'rows': 10, 'cols': 40}),
         'label': 'Comment',
         'required': False,
         },
         ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    public_review_form = dynaform.newDynaForm(dynamodel=None, 
        dynabase=helper.forms.BaseForm, dynainclude=None, 
        dynaexclude=None, dynaproperties=dynaproperties)
    params['public_review_form'] = public_review_form

    # create the special form for mentors
    dynafields = [
        {'name': 'score',
         'base': forms.ChoiceField,
         'label': 'Score',
         'initial': 0,
         'required': False,
         'passthrough': ['initial', 'required', 'choices'],
         'example_text':
             'A score will only be assigned if the review is private!',
         'choices': [(-4,'-4: Wow. This. Sucks.'),
                     (-3,'-3: Needs a lot of work'),
                     (-2,'-2: This is bad'),
                     (-1,'-1: I dont like this'),
                     (0,'0: No score'),
                     (1,'1: Might have potential'),
                     (2,'2: Good'),
                     (3,'3: Almost there'),
                     (4,'4: Made. Of. Awesome.')]
        },
        {'name': 'comment',
         'base': forms.CharField,
         'widget': widgets.FullTinyMCE(attrs={'rows': 10, 'cols': 40}),
         'label': 'Comment',
         'required': False,
         },
        {'name': 'public',
         'base': forms.BooleanField,
         'label': 'Public review',
         'initial': False,
         'required': False,
         'help_text': 'By ticking this box the score will not be assigned, '
             'and the review will be public.',
         },
         ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    mentor_review_form = dynaform.newDynaForm(dynamodel=None, 
        dynabase=helper.forms.BaseForm, dynainclude=None, 
        dynaexclude=None, dynaproperties=dynaproperties)
    params['mentor_review_form'] = mentor_review_form

    # TODO see if autocomplete can be used for mentor field
    dynafields = [
      {'name': 'rank',
         'base': forms.IntegerField,
         'label': 'Set to rank',
         'help_text':
             'Set this proposal to the given rank (ignores the given score)',
         'example_text': 'A rank will only be assigned if the review is private!',
         'min_value': 1,
         'required': False,
         'passthrough': ['min_value', 'required', 'help_text'],
      },
      {'name': 'mentor',
       'base': forms.CharField,
       'label': 'Assign Mentor (Link ID)',
       'required': False,
       'help_text': 'Fill in the Link ID of the Mentor '
           'you would like to assign to this Proposal. '
           'Leave this box empty if you don\'t want any mentor assigned.',
      },
      ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    admin_review_form = dynaform.extendDynaForm(dynaform=mentor_review_form, 
        dynaproperties=dynaproperties)

    params['admin_review_form'] = admin_review_form

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
      fields['link_id'] = 't%i' %(int(time.time()*100))
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
  def public(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """View in which the student can see and reply to the comments on the
       Student Proposal.

    For params see base.view.Public().
    """

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    try:
      entity = self._logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'], context=context)

    context['entity'] = entity
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']

    if request.method == 'POST':
      return self.publicPost(request, context, params, entity, **kwargs)
    else: # request.method == 'GET'
      return self.publicGet(request, context, params, entity, **kwargs)

  def publicPost(self, request, context, params, entity, **kwargs):
    """Handles the POST request for the entity's public page.

    Args:
        entity: the student proposal entity
        rest: see base.View.public()
    """

    # populate the form using the POST data
    form = params['public_review_form'](request.POST)

    if not form.is_valid():
      # get some entity specific context
      self.updatePublicContext(context, entity, params)

      # return the invalid form response
      return self._constructResponse(request, entity=entity, context=context,
          form=form, params=params, template=params['public_template'])

    # get the commentary
    fields = form.cleaned_data
    comment = fields['comment']

    if comment:
      # create a new public review containing the comment
      user_entity = user_logic.logic.getForCurrentAccount()

      if user_entity.key() == entity.scope.user.key():
        # student is posting
        reviewer = entity.scope
      else:
        # check if the person commenting is an org_admin
        # or a mentor for the given proposal
        fields = {'user': user_entity,
                  'scope': entity.org,
                  'status': 'active',
                  }

        reviewer = org_admin_logic.logic.getForFields(fields, unique=True)

        if not reviewer:
          # no org_admin found, maybe it's a mentor?
          reviewer = mentor_logic.logic.getForFields(filter, unique=True)

      # create the review (reviewer might be None if a Host or Developer is posting)
      self._createReviewFor(entity, reviewer, comment, is_public=True)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def publicGet(self, request, context, params, entity, **kwargs):
    """Handles the GET request for the entity's public page.

    Args:
        entity: the student proposal entity
        rest see base.View.public()
    """

    from soc.logic.models.review_follower import logic as review_follower_logic

    get_dict = request.GET

    if get_dict.get('subscription') and (
      get_dict['subscription'] in ['on', 'off']):

      subscription = get_dict['subscription']

      # get the current user
      user_entity = user_logic.logic.getForCurrentAccount()

      # create the fields that should be in the ReviewFollower entity
      fields = {'link_id': user_entity.link_id,
                'scope': entity,
                'scope_path': entity.key().name(),
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
    self.updatePublicContext(context, entity, params)

    context['form'] = params['public_review_form']()
    template = params['public_template']

    return responses.respond(request, template, context=context)

  def updatePublicContext(self, context, entity, params):
    """Updates the context for the public page with information from the entity.

    Args:
      context: the context that should be updated
      entity: a student proposal_entity used to set context
      params: dict with params for the view using this context
    """

    from soc.logic.models.review import logic as review_logic
    from soc.logic.models.review_follower import logic as review_follower_logic

    student_entity = entity.scope

    context['student'] = student_entity
    context['student_name'] = student_entity.name()

    user_entity = user_logic.logic.getForCurrentAccount()

    # check if the current user is the student
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
    """Lists all proposals from the current logged-in user 
       for the given student.

    For params see base.View.public().
    """

    student_entity = student_logic.logic.getFromKeyName(kwargs['scope_path'])

    filter = {'scope' : student_entity,
              'status': ['new', 'pending', 'accepted', 'rejected']}

    list_params = params.copy()
    list_params['list_description'] = 'List of my %(name_plural)s' % list_params
    list_params['list_action'] = (redirects.getPublicRedirect, list_params)

    return self.list(request, access_type=access_type, page_name=page_name,
                     params=list_params, filter=filter, **kwargs)

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
    context['page_name'] = page_name
    context['entity'] = entity
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']

    # get the roles important for reviewing an application
    filter = {'user': user_logic.logic.getForCurrentAccount(),
        'scope': entity.org,
        'status': 'active'}

    org_admin_entity = org_admin_logic.logic.getForFields(filter, unique=True)
    mentor_entity = mentor_logic.logic.getForFields(filter, unique=True)

    # decide which form to use
    if org_admin_entity:
      form = params['admin_review_form']
    else:
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
    # populate the form using the POST data
    form = form(request.POST)

    if not form.is_valid():
      # return the invalid form response
      # get all the extra information that should be in the context
      review_context = self._getDefaultReviewContext(entity, org_admin, mentor)
      context = dicts.merge(context, review_context)

      return self._constructResponse(request, entity=entity, context=context,
          form=form, params=params, template=params['review_template'])

    fields = form.cleaned_data
    is_public = fields['public']
    comment = fields['comment']
    given_score = int(fields['score'])

    if org_admin:
      # org admin found, try to adjust the assigned mentor
      self._adjustMentor(entity, fields['mentor'])
      reviewer = org_admin

      # try to see if the rank is given and adjust the given_score if needed
      rank = fields['rank']
      if rank:
        ranker = self._logic.getRankerFor(entity)
        # if a very high rank is filled in use the highest one that returns a score
        rank = min(ranker.TotalRankedScores(), rank)
        # ranker uses zero-based ranking
        score_and_rank = ranker.FindScore(rank-1)
        # get the score at the requested rank
        score_at_rank = score_and_rank[0][0]
        # calculate the score that should be given to end up at the given rank
        given_score = score_at_rank - entity.score
    else:
      # might be None (if Host or Developer is commenting)
      reviewer = mentor

    if reviewer and (not is_public) and (given_score is not 0):
      # if it is not a public comment and it's made by a member of the
      # organization we update the score of the proposal
      new_score = given_score + entity.score

      properties = {'score': new_score}

      # if the proposal is new we change it status to pending
      if entity.status == 'new':
        properties['status'] = 'pending'

      # update the proposal with the new score
      self._logic.updateEntityProperties(entity, properties)

    # create the review entity
    if comment or (given_score is not 0):
      self._createReviewFor(entity, reviewer, comment, given_score, is_public)

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

    from soc.logic.models.review_follower import logic as review_follower_logic

    get_dict = request.GET

    # check if the current user is a mentor and wants 
    # to change his role for this app
    choice = get_dict.get('mentor')
    if mentor and choice:
      self._adjustPossibleMentors(entity, mentor, choice)

    is_ineligible = get_dict.get('ineligible')
    if org_admin and is_ineligible:
      # mark the proposal invalid and return to the list
      properties = {'status': 'invalid'}
      self._logic.updateEntityProperties(entity, properties)

      redirect = redirects.getListProposalsRedirect(entity.org,
                                                    {'url_name': 'org'})
      return http.HttpResponseRedirect(redirect)

    # check if we should change the subscription state for the current user
    public_subscription = None
    private_subscription = None

    if get_dict.get('public_subscription') and (
      get_dict['public_subscription'] in ['on', 'off']):

      public_subscription = get_dict['public_subscription'] == 'on'

    if get_dict.get('private_subscription') and (
      get_dict['private_subscription'] in ['on', 'off']):
      private_subscription = get_dict['private_subscription'] == 'on'

    if public_subscription != None or private_subscription != None:
      # get the current user
      user_entity = user_logic.logic.getForCurrentAccount()

      # create the fields that should be in the ReviewFollower entity
      fields = {'link_id': user_entity.link_id,
                'scope': entity,
                'scope_path': entity.key().name(),
                'user': user_entity
               }
      # get the keyname for the ReviewFollower entity
      key_name = review_follower_logic.getKeyNameFromFields(fields)

      # determine which subscription properties we should change
      if public_subscription != None:
        fields['subscribed_public'] = public_subscription

      if private_subscription != None:
        fields['subscribed_private'] = private_subscription

      # update the ReviewFollower
      review_follower_logic.updateOrCreateFromKeyName(fields, key_name)

    # set the initial score since the default is ignored
    initial = {'score': 0}

    if org_admin and entity.mentor:
      # set the mentor field to the current mentor
      initial['mentor'] = entity.mentor.link_id

    context['form'] = form(initial)

    # get all the extra information that should be in the context
    review_context = self._getDefaultReviewContext(entity, org_admin, mentor)
    context = dicts.merge(context, review_context)

    template = params['review_template']

    return responses.respond(request, template, context=context)

  def _getDefaultReviewContext(self, entity, org_admin,
                               mentor):
    """Returns the default context for the review page.

    Args:
      entity: Student Proposal entity
      org_admin: org admin entity for the current user/proposal (iff available)
      mentor: mentor entity for the current user/proposal (iff available)
    """

    from soc.logic.models.review import logic as review_logic
    from soc.logic.models.review_follower import logic as review_follower_logic

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
        possible_mentor = mentor_logic.logic.getFromKeyName(mentor_key.name())
        mentor_names.append(possible_mentor.name())

      context['possible_mentors'] = ', '.join(mentor_names)

    # TODO(ljvderijk) listing of total given scores per mentor
    # a dict with key as role.user ?

    # order the reviews by ascending creation date
    order = ['created']

    # get the public reviews
    context['public_reviews'] = review_logic.getReviewsForEntity(entity,
        is_public=True, order=order)

    # get the private reviews
    context['private_reviews'] = review_logic.getReviewsForEntity(entity,
        is_public=False, order=order)

    # which button should we show to the mentor?
    if mentor:
      if mentor.key() in possible_mentors:
        # show "No longer willing to mentor"
        context['remove_me_as_mentor'] = True
      else:
        # show "I am willing to mentor"
        context['add_me_as_mentor'] = True

    if org_admin:
      context['is_org_admin'] = True

    user_entity = user_logic.logic.getForCurrentAccount()

    # check if the current user is subscribed to public or private reviews
    fields = {'scope': entity,
              'user': user_entity,}
    follower_entity = review_follower_logic.getForFields(fields, unique=True)

    if follower_entity:
      context['is_subscribed_public'] =  follower_entity.subscribed_public
      context['is_subscribed_private'] = follower_entity.subscribed_private

    return context

  def _adjustPossibleMentors(self, entity, mentor, choice):
    """Adjusts the possible mentors list for a proposal.

    Args:
      entity: Student Proposal entity
      mentor: Mentor entity
      choice: 1 means want to mentor, 0 do not want to mentor
    """
    possible_mentors = entity.possible_mentors

    if choice == '1':
      # add the mentor to possible mentors list if not already in
      if mentor.key() not in possible_mentors:
        possible_mentors.append(mentor.key())
        fields = {'possible_mentors': possible_mentors}
        self._logic.updateEntityProperties(entity, fields)
    elif choice == '0':
      # remove the mentor from the possible mentors list
      if mentor.key() in possible_mentors:
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

    # update the proposal
    properties = {'mentor': mentor_entity}
    self._logic.updateEntityProperties(entity, properties)

  def _createReviewFor(self, entity, reviewer, comment, score=0, is_public=True):
    """Creates a review for the given proposal and sends out a message to all followers.

    Args:
      entity: Student Proposal entity for which the review should be created
      reviewer: A role entity of the reviewer (if possible, else None)
      comment: The textual contents of the review
      score: The score of the review (only used if the review is not public)
      is_public: Determines if the review is a public review
    """

    import time

    from soc.logic.helper import notifications as notifications_helper
    from soc.logic.models.review import logic as review_logic
    from soc.logic.models.review_follower import logic as review_follower_logic

    # create the fields for the review entity
    fields = {'link_id': 't%i' %(int(time.time()*100)),
        'scope': entity,
        'scope_path': entity.key().name(),
        'author': user_logic.logic.getForCurrentAccount(),
        'content': comment,
        'is_public': is_public,
        'reviewer': reviewer
        }

    # add the given score if the review is not public
    if not is_public:
      fields['score'] = score

    # create a new Review
    key_name = review_logic.getKeyNameFromFields(fields)
    review_entity = review_logic.updateOrCreateFromKeyName(fields, key_name)

    # get all followers
    fields = {'scope': entity}

    if is_public:
      fields['subscribed_public'] = True
    else:
      fields['subscribed_private'] = True

    followers = review_follower_logic.getForFields(fields)

    if is_public:
      # redirect to public page
      redirect_url = redirects.getPublicRedirect(entity, self._params)
    else:
      # redirect to review page
      redirect_url = redirects.getReviewRedirect(entity, self._params)

    for follower in followers:
      # sent to every follower except the reviewer
      if follower.user.key() != review_entity.author.key():
        notifications_helper.sendNewReviewNotification(follower.user,
            review_entity, entity.title, redirect_url)


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
review = decorators.view(view.review)
export = decorators.view(view.export)
pick = decorators.view(view.pick)
