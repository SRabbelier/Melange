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

"""Views for Tasks.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>',
    '"Daniel Hans" <daniel.m.hans@gmail.com>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import datetime
import logging
import time

from google.appengine.ext import blobstore
from google.appengine.ext import db
from google.appengine.runtime import apiproxy_errors

from django import forms
from django import http
from django.utils import simplejson
from django.utils.timesince import timeuntil
from django.utils.translation import ugettext

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.helper import timeline as timeline_helper
from soc.logic.models import host as host_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import decorators
from soc.views.helper import dynaform
from soc.views.helper import lists
from soc.views.helper import params as params_helper
from soc.views.helper import redirects
from soc.views.helper import requests
from soc.views.helper import responses
from soc.views.helper import widgets
from soc.views.models import base

from soc.modules.gci.logic import cleaning as gci_cleaning
from soc.modules.gci.logic.helper import notifications as gci_notifications
from soc.modules.gci.logic.models import mentor as gci_mentor_logic
from soc.modules.gci.logic.models import organization as gci_org_logic
from soc.modules.gci.logic.models import org_admin as gci_org_admin_logic
from soc.modules.gci.logic.models import task as gci_task_logic
from soc.modules.gci.models import task as gci_task_model
from soc.modules.gci.views.helper import access
from soc.modules.gci.views.helper import redirects as gci_redirects
from soc.modules.gci.views.models import organization as gci_org_view
from soc.modules.gci.tasks import bulk_create as bulk_create_tasks
from soc.modules.gci.tasks import ranking_update
from soc.modules.gci.tasks import task_update
import soc.modules.gci.logic.models.task


class View(base.View):
  """View methods for the Tasks.
  """

  DEF_AWAITING_REG_MSG = ugettext(
      'The task is open but you cannot claim this task since you '
      'have not completed the student signup after finishing your '
      'first task.')

  DEF_CAN_EDIT_TASK_MSG = ugettext(
      'The task can be edited by clicking on the edit link '
      'next to the title above.')

  DEF_CLAIM_DEADLINE_PASSED_MSG = ugettext(
      'The task claim deadline has passed. You cannot claim any more '
      'tasks now.'
      )

  DEF_MAX_TASK_LIMIT_MSG_FMT = ugettext(
      'The task is open but you cannot claim this task since you '
      'have already claimed %d task(s).')

  DEF_NO_TASKS_MSG = ugettext(
      'There are no tasks under your organization. Please create tasks.')

  DEF_STOP_WORK_DEADLINE_MSG = ugettext(
      'The %(program_name)s has ended and no more actions can be performed '
      'on this task.')

  DEF_STUDENT_SIGNUP_MSG = ugettext(
      'You have successfully completed this task. <a href=" '
      '%(student_signup_redirect)s">Click here</a> to sign up as a '
      'student before you proceed further.')

  DEF_TASK_ACTION_NEEDED_MSG = ugettext(
      'The initial deadline for this task has passed. You have been granted '
      'an additional 24 hours to complete this task.')

  DEF_TASK_CLAIMED_BY_YOU_MSG = ugettext(
      'You have claimed this task!')

  DEF_TASK_CLAIMED_BY_STUDENT_MSG = ugettext(
      'This task has been claimed by a student!')

  DEF_TASK_CLAIMED_REQUESTED_MSG = ugettext(
      'A student has requested to claim this task and the request is pending.')

  DEF_TASK_CLAIMED_MSG = ugettext(
      'The task is already claimed and the work is in progress.')

  DEF_TASK_CLAIM_REQUESTED_MSG = ugettext(
      'A student has requested to claim this task. Accept or '
      'reject the request.')

  DEF_TASK_CLOSED_MSG = ugettext('This task is closed.')

  DEF_TASK_CMPLTD_BY_YOU_MSG = ugettext(
      'You have successfully completed this task!')

  DEF_TASKS_LIST_CLAIM_MSG = ugettext(
       'List of claimed tasks.')

  DEF_TASKS_LIST_CLOSE_MSG = ugettext(
       'List of closed tasks.')

  DEF_TASKS_LIST_INVALID_MSG = ugettext(
       'List of Invalid/deleted tasks.')

  DEF_TASKS_LIST_OPEN_MSG = ugettext(
       'List of open tasks.')

  DEF_TASKS_LIST_UNAPPROVED_MSG = ugettext(
       'List of non-public tasks.')

  DEF_TASK_NO_MORE_SUBMIT_MSG = ugettext(
      'You have submitted the work to this task, but the deadline has passed. '
      'You cannot submit any more work until your mentor extends the '
      'deadline.')

  DEF_TASK_MENTOR_REOPENED_MSG = ugettext(
      'The task has been reopened.')

  DEF_TASK_MENTOR_FIX_MSG = ugettext(
      'Through no fault of your own, the current difficulty of this task is '
      'set to a value which is worth 0 points. Please fix this.')

  DEF_TASK_MENTOR_ACTION_NEEDED_MSG = ugettext(
      'The initial deadline for the task has passed. The student has been '
      'notified and the deadline has been extended by 24 hours. No action is '
      'required from you.')

  DEF_TASK_NEEDS_REVIEW_MSG = ugettext(
      'Student has submitted his work for this task! It needs review.')

  DEF_TASK_OPEN_MSG = ugettext(
      'This task is open. If you are a GCI student, you can claim it!')

  DEF_TASK_REOPENED_MSG = ugettext(
      'This task has been reopened. If you are a GCI student, '
      'you can claim it!')

  DEF_TASK_REQ_CLAIMED_BY_YOU_MSG = ugettext(
      "You have requested to claim this task and the request is pending. "
      "Please don't submit any work until the request is approved.")

  DEF_TASK_UNPUBLISHED_MSG = ugettext(
      'The task is not yet published. It can be edited by clicking on '
      'the edit link next to the title above.')

  DEF_TASK_INVALID_MSG = ugettext(
      'This task has been marked as Invalid by an administrator.')

  DEF_WS_MSG_FMT = ugettext(
      '(To see the work submitted <a href=#ws%d>click here</a>.)')

  def __init__(self, params=None):
    """Defines the fields and methods required for the task View class
    to provide the user with the necessary views.

    Params:
      params: a dict with params for this View
    """
    rights = access.GCIChecker(params)
    # TODO: create and suggest_task don't need access checks which use state
    # also feels like roles are being checked twice?
    rights['any_access'] = ['allow']
    rights['bulk_create'] = [
        ('checkHasRoleForScope', gci_org_admin_logic.logic),
        ('checkTimelineFromTaskScope', ['before', 'task_claim_deadline'])]
    rights['create'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', True]),
        ('checkRoleAndStatusForTask',
            [['gci/org_admin'], ['active'],
            []]),
        ('checkTimelineFromTaskScope', ['before', 'task_claim_deadline'])]
    rights['edit'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', False]),
        ('checkRoleAndStatusForTask',
            [['gci/org_admin'], ['active'],
            ['Unapproved', 'Unpublished', 'Open',
             'ClaimRequested', 'Reopened']]),
        ('checkTimelineFromTaskScope', ['before', 'task_claim_deadline'])]
    rights['delete'] = [
        ('checkRoleAndStatusForTask', 
            [['gci/org_admin'], ['active'],
            ['Unapproved', 'Unpublished', 'Open',
             'ClaimRequested', 'Reopened']])]
    rights['show'] = ['checkStatusForTask']
    rights['list_org_tasks'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', False])]
    rights['suggest_task'] = [
        ('checkCanOrgAdminOrMentorEdit', ['scope_path', True]),
        ('checkRoleAndStatusForTask',
            [['gci/org_admin', 'gci/mentor'], ['active'],
            ['Unapproved', 'Unpublished', 'Open',
             'ClaimRequested', 'Reopened']]),
        ('checkTimelineFromTaskScope', ['before', 'task_claim_deadline'])]

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.task.logic
    new_params['rights'] = rights

    new_params['name'] = "Task"
    new_params['module_name'] = "task"
    new_params['sidebar_grouping'] = 'Tasks'

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/task'

    new_params['scope_view'] = gci_org_view
    new_params['scope_redirect'] = redirects.getCreateRedirect

    new_params['extra_dynaexclude'] = ['task_type', 'time_to_complete',
                                       'mentors', 'user', 'student',
                                       'program', 'status', 'deadline',
                                       'created_by', 'created_on',
                                       'modified_by', 'modified_on',
                                       'history', 'link_id', 'difficulty',
                                       'closed_on']

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>bulk_create)/%(scope)s$',
        '%(module_package)s.%(module_name)s.bulk_create',
        'Bulk Create %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>suggest_task)/%(scope)s$',
        '%(module_package)s.%(module_name)s.suggest_task',
        'Mentors suggest %(name)s'),
        (r'^%(url_name)s/(?P<access_type>suggest_task)/%(key_fields)s$',
        '%(module_package)s.%(module_name)s.suggest_task',
        'Mentors edit a %(name)s'),
        (r'^%(url_name)s/(?P<access_type>list_org_tasks)/%(scope)s$',
        '%(module_package)s.%(module_name)s.list_org_tasks',
        'Organization %(name)s List'),
        ]

    new_params['extra_django_patterns'] = patterns

    new_params['create_dynafields'] = [
        {'name': 'arbit_tags',
         'base': forms.fields.CharField,
         'label': 'Arbitrary Tags',
         'required': False,
         'group': ugettext('Tags'),
         'help_text': ugettext(
             'Enter arbitrary Tags for this task separated by comma.\n'
             '<b>Note:</b> Tag names are case sensitive. If the tag is same '
             'as the program mandated tag, it will be considered as a '
             'mandatory tag.')
         },
        ]

    new_params['create_extra_dynaproperties'] = {
        'description': forms.fields.CharField(required=True,
            widget=widgets.FullTinyMCE(attrs={'rows': 25, 'cols': 100})),
        'scope_path': forms.CharField(widget=forms.HiddenInput,
            required=True),
        'task_status': forms.CharField(widget=widgets.PlainTextWidget(),
                                       required=False),
        'time_to_complete_days': forms.IntegerField(
            min_value=0, required=True, initial=0,
            label='Time to complete (in days)',
            help_text=ugettext('If the task requires, say 84 hours in '
            'total to complete, enter 3 in days field and 12 in hours '
            'field.')),
        'time_to_complete_hours': forms.IntegerField(
            min_value=0, required=True, initial=1,
            label='Time to complete (in hours)',
            help_text=ugettext('If you enter the total amount of time in '
            'hours, say 84, it will be converted to days and hours format.')),
        'clean_description': cleaning.clean_html_content('description'),
        'clean_arbit_tags': cleaning.str2set('arbit_tags'),
        }

    new_params['edit_extra_dynaproperties'] = {
        'link_id': forms.CharField(widget=forms.HiddenInput)
        }

    new_params['public_template'] = 'modules/gci/task/public.html'
    new_params['bulk_create_template'] = 'modules/gci/task/bulk_create.html'

    def render(entities):
      two = [i.name() for i in entities[:2]]
      result = ", ".join(two)
      size = len(entities) - 2
      return result if size < 2 else "%s + %d" % (result, size)

    # TODO (Madhu) Add mentors to prefetch of both public and home
    # once prefetch for list of references is fixed
    new_params['public_field_extra'] = lambda entity, all_d, all_t: {
        "org": entity.scope.name,
        "points_difficulty": entity.taskDifficultyValue(all_d),
        "task_type": entity.taskType(all_t),
        # TODO(SRabbelier): change back to 'render(db.get(entity.mentors))'
        "mentors": str(len(entity.mentors)),
        "arbit_tag": entity.taskArbitTag(),
        "days_hours": entity.taskTimeToComplete(),
    }
    new_params['public_field_prefetch'] = ["scope"]
    new_params['public_field_keys'] = [
        "title", "org", "points_difficulty", "task_type",
        "arbit_tag", "time_to_complete", "days_hours", "status", "mentors",
    ]
    new_params['public_field_names'] = [
        "Title", "Organization", "Points (Difficulty)", "Type", "Tags",
        "Total Hours To Complete", "Time To Complete", "Status", "Mentors",
    ]
    new_params['public_field_props'] = new_params['home_field_props'] = {
        'time_to_complete': {
            'sorttype': 'integer',
        },
    }

    # parameters to list the task on the organization home page
    new_params['home_field_extra'] = lambda entity, all_d, all_t: {
        "points_difficulty": entity.taskDifficultyValue(all_d),
        "task_type": entity.taskType(all_t),
        "arbit_tag": entity.taskArbitTag(),
        "mentors": render(db.get(entity.mentors)),
        "days_hours": entity.taskTimeToComplete(),
    }

    new_params['home_field_keys'] = ["title", "points_difficulty", "task_type",
                                     "arbit_tag", "time_to_complete", "days_hours",
                                     "mentors", "modified_on"]
    new_params['home_field_hidden'] = ["modified_on"]
    new_params['home_field_names'] = ["Title", "Points (Difficulty)", "Type",
                                     "Tags", "Total Hours To Complete",
                                     "Time To Complete", "Mentors",
                                     "Modified On"]

    new_params['public_row_action'] = new_params['home_row_action'] = {
          "type": "redirect_custom",
          "parameters": dict(new_window=True),
    }
    new_params['public_row_extra'] = new_params['home_row_extra'] = \
        lambda entity, *args: {
            'link': redirects.getPublicRedirect(
                entity, {'url_name': new_params['url_name']})
    }

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

    self._params['save_message'].append(ugettext(
        'Successfully started processing your tasks, they should show up '
        'shortly. Feel free to submit more.'))
    self._params['bulk_create_message_idx'] = len(self._params['save_message']) - 1

    # holds the base form for the task creation and editing
    self._params['base_create_form'] = self._params['create_form']
    self._params['base_edit_form'] = self._params['edit_form']

    # extend create and edit form for org admins
    dynafields = [
        {'name': 'mentors_list',
         'required': True,
         'base': forms.fields.CharField,
         'label': 'Assign mentors',
         'help_text': 'Assign mentors to this task by '
             'giving their link_ids separated by comma.',
         },
        ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    dynaproperties['clean_mentors_list'] = gci_cleaning.cleanMentorsList(
        'mentors_list')

    create_form = dynaform.extendDynaForm(
        dynaform=self._params['create_form'],
        dynaproperties=dynaproperties)

    self._params['create_form'] = create_form

    edit_form = dynaform.extendDynaForm(
        dynaform=self._params['edit_form'],
        dynaproperties=dynaproperties)

    self._params['edit_form'] = edit_form

    # create the comment form TODO(LJ) Cleaning check CSV structure?
    dynafields = [
        {'name': 'comment',
         'base': forms.CharField,
         'widget': widgets.FullTinyMCE(attrs={'rows': 10, 'cols': 40}),
         'label': 'Comment',
         'required': False,
         'example_text': 'Comment is optional.<br/>'
             'Choose an appropriate Action below and Save your '
             'changes.<br /><br />Caution, you will not be able '
             'to edit your comment!',
         },
         ]

    dynaproperties = params_helper.getDynaFields(dynafields)
    dynaproperties['clean_comment'] = cleaning.clean_html_content('comment')
    dynaproperties['clean'] = gci_cleaning.cleanTaskComment(
        'comment', 'action', 'work_submission_external',
        'work_submission_upload', 'extended_deadline')

    comment_form = dynaform.newDynaForm(dynamodel=None,
        dynabase=helper.forms.BaseForm, dynainclude=None,
        dynaexclude=None, dynaproperties=dynaproperties)
    self._params['comment_form'] = comment_form

    # create the bulk create form
    dynafields = [
        {'name': 'data',
         'base': forms.CharField,
         'widget': forms.widgets.Textarea(attrs={'rows': 10, 'cols': 40}),
         'label': 'Tasks',
         'required': True,
         'example_text': 'The tasks in CSV format',
         },
         ]
    dynaproperties = params_helper.getDynaFields(dynafields)
    bulk_form = dynaform.newDynaForm(dynamodel=None,
        dynabase=helper.forms.BaseForm, dynainclude=None,
        dynaexclude=None, dynaproperties=dynaproperties)
    self._params['bulk_create_form'] = bulk_form

  def _getTagsForProgram(self, form_name, params, **kwargs):
    """Extends form dynamically from difficulty levels in program entity.

    Args:
     form_name: the Form entry in params to extend
     params: the params for the view
    """
    # obtain program_entity using scope_path which holds
    # the org_entity key_name
    org_entity = gci_org_logic.logic.getFromKeyName(kwargs['scope_path'])

    # get a list difficulty levels stored for the program entity
    tds = gci_task_model.TaskDifficultyTag.get_by_scope(org_entity.scope)

    difficulties = []
    for td in tds:
      difficulties.append((td.tag, td.tag))

    # get a list of task type tags stored for the program entity
    tts = gci_task_model.TaskTypeTag.get_by_scope(org_entity.scope)

    type_tags = []
    for tt in tts:
      type_tags.append((tt.tag, tt.tag))

    # create the difficultly level field containing the choices
    # defined in the program entity
    dynafields = [
        {'name': 'difficulty',
         'base': forms.ChoiceField,
         'label': 'Difficulty level',
         'required': True,
         'passthrough': ['initial', 'required', 'choices',
                         'label', 'help_text'],
         'choices': difficulties,
         'group': ugettext('Tags'),
         'help_text': ugettext('Difficulty Level of this task.'),
         },
         {'name': 'type_tags',
         'base': forms.MultipleChoiceField,
         'label': 'Task Types',
         'required': True,
         'passthrough': ['initial', 'required', 'choices',
                         'label', 'help_text'],
         'choices': type_tags,
         'group': ugettext('Tags'),
         'help_text': ugettext('Task Type tags mandated by the program. You '
                               'must select one or more of them.'),
         },
       ]

    dynaproperties = params_helper.getDynaFields(dynafields)

    extended_form = dynaform.extendDynaForm(
        dynaform=params[form_name],
        dynaproperties=dynaproperties)

    return extended_form

  @decorators.check_access
  def create(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Replaces the create Form with the dynamic one.

    For args see base.View.create().
    """
    params = dicts.merge(params, self._params)

    # redirect to scope selection view
    if ('scope_view' in params) and ('scope_path' not in kwargs):
      view = params['scope_view'].view
      redirect = params['scope_redirect']
      return self.select(request, view, redirect,
                         params=params, page_name=page_name, **kwargs)

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    # extend create_form to include difficulty levels
    params['create_form'] = self._getTagsForProgram(
        'create_form', params, **kwargs)

    if request.method == 'POST':
      return self.createPost(request, context, params)
    else:
      return self.createGet(request, context, params, kwargs)

  @decorators.merge_params
  @decorators.check_access
  def edit(self, request, access_type,
           page_name=None, params=None, seed=None, **kwargs):
    """See base.View.edit().
    """
    logic = params['logic']

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    try:
      entity = logic.getFromKeyFieldsOr404(kwargs)
    except out_of_band.Error, error:
      msg = self.DEF_CREATE_NEW_ENTITY_MSG_FMT % {
          'entity_type_lower' : params['name'].lower(),
          'entity_type' : params['name'],
          'create' : params['missing_redirect']
          }
      error.message_fmt = error.message_fmt + msg
      return helper.responses.errorResponse(
          error, request, context=context)

    params = params.copy()

    # extend edit_form to include difficulty levels
    params['edit_form'] = self._getTagsForProgram(
        'edit_form', params, **kwargs)

    params['edit_template'] = 'modules/gci/task/edit.html'

    buttons = [
        ('Publish Task', 'publish', 'Open', ['Unapproved', 'Unpublished']),
        ('Approve Task', 'approve', 'Unpublished', ['Unapproved']),
        ('Unpublish Task', 'unpublish', 'Unpublished', ['Open', 'Reopened']),
        ('Unapprove Task', 'unapprove', 'Unapproved', ['Unpublished']),
    ]

    context['buttons'] = []

    for (text, action, next_state, states) in buttons:
      if entity.status not in states:
        if request.method != 'POST':
          continue

      if request.POST.get(action):
        if entity.status not in states:
          # request is no longer valid, redirect to current page
          return http.HttpResponseRedirect('')

        entity.status = next_state
        entity.put()
        return http.HttpResponseRedirect(request.path + '?s=0')

      item = (text, action)
      context['buttons'].append(item)

    if request.method == 'POST':
      return self.editPost(request, entity, context, params=params)
    else:
      return self.editGet(request, entity, context, params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """
    if entity.task_type:
      form.fields['type_tags'].initial = entity.taskType(ret_list=True)
    if entity.arbit_tag:
      form.fields['arbit_tags'].initial = entity.taskArbitTag()

    if entity.difficulty:
      form.fields['difficulty'].initial = entity.taskDifficulty()

    if entity.mentors and 'mentors_list' in form.fields:
      mentor_entities = db.get(entity.mentors)
      mentors_list = []
      for mentor in mentor_entities:
        mentors_list.append(mentor.link_id)
      form.fields['mentors_list'].initial = ', '.join(mentors_list)

    # time_to_complete is normalized to hours in datastore, so
    # while presenting it on the form we are converting it to
    # days and hours format
    form.fields['time_to_complete_days'].initial = \
        entity.time_to_complete / 24
    form.fields['time_to_complete_hours'].initial = \
        entity.time_to_complete % 24

    form.fields['task_status'].initial = entity.status
    form.fields['link_id'].initial = entity.link_id

    return super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base._editPost().
    """
    # set the scope field
    super(View, self)._editPost(request, entity, fields)

    # TODO: this method can be made more clear, it seems a bit of a mess

    if not entity:
      program_entity = fields['scope'].scope
      fields['program'] = program_entity
    else:
      program_entity = entity.program

    user_account = user_logic.logic.getCurrentUser()

    filter = {
        'user': user_account,
        'status': 'active'
        }

    # get the host entity if the current user is host
    role_entity = host_logic.logic.getForFields(filter, unique=True)

    if not entity:
      filter['scope'] = fields['scope']
    else:
      filter['scope'] = entity.scope

    if not role_entity:
      # get the entity if the current user is org admin
      role_entity = gci_org_admin_logic.logic.getForFields(
          filter, unique=True)

    if role_entity:
      fields['mentors'] = fields.get('mentors_list', [])
    else:
      role_entity = gci_mentor_logic.logic.getForFields(filter, unique=True)

    if not entity:
      # creating a new task
      fields['status'] = 'Unapproved'

    # explicitly change the last_modified_on since the content has been edited
    fields['modified_on'] = datetime.datetime.now()

    # normalize days and hours for time to complete to hours
    ttc_days = fields['time_to_complete_days']
    ttc_hours = fields['time_to_complete_hours']
    fields['time_to_complete'] =  (ttc_days * 24) + ttc_hours

    if not entity:
      fields['link_id'] = 't%i' % (int(time.time()*100))
      fields['modified_by'] = role_entity
      fields['created_by'] = role_entity
      fields['created_on'] = datetime.datetime.now()
    else:
      fields['link_id'] = entity.link_id
      fields['modified_by'] = role_entity
      if 'status' not in fields:
        fields['status'] = entity.status

    fields['difficulty'] = {
        'tags': fields['difficulty'],
        'scope': program_entity
        }

    fields['task_type'] = {
        'tags': fields['type_tags'],
        'scope': program_entity
        }

    fields['arbit_tag'] = {
        'tags': fields['arbit_tags'],
        'scope': program_entity
        }

    return

  @decorators.merge_params
  @decorators.check_access
  def bulkCreate(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """View used to allow Org Admins to bulk create tasks.

    For args see base.View.create().
    """
    template = params['bulk_create_template']

    # get the context for this webpage
    context = responses.getUniversalContext(request)
    responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    org_entity = gci_org_logic.logic.getFromKeyName(kwargs['scope_path'])

    # get a list difficulty levels stored for the program entity
    tds = gci_task_model.TaskDifficultyTag.get_by_scope(org_entity.scope)
    context['difficulties'] = ', '.join([str(x) for x in tds])

    # get a list of task type tags stored for the program entity
    tts = gci_task_model.TaskTypeTag.get_by_scope(org_entity.scope)
    context['types'] = ', '.join([str(x) for x in tts])

    if request.POST:
      return self._bulkCreatePost(request, params, template, context, **kwargs)
    else:
      return self._bulkCreateGet(request, params, template, context, **kwargs)

  def _bulkCreateGet(self, request, params, template, context, **kwargs):
    """Handles GET requests for the bulk create page.
    """
    context['bulk_create_form'] = params['bulk_create_form']()

    context['notice'] = requests.getSingleIndexedParamValue(
        request, params['submit_msg_param_name'],
        values=params['save_message'])

    return responses.respond(request, template, context)


  def _bulkCreatePost(self, request, params, template, context, **kwargs):
    """Handles POST requests for the bulk create page.
    """
    form = params['bulk_create_form'](request.POST)

    if not form.is_valid():
      # show the form errors
      context['bulk_create_form'] = form
      return self._constructResponse(request, entity=None, context=context,
                                     form=form, params=params,
                                     template=template)

    # retrieve the data from the form
    _, properties = helper.forms.collectCleanedFields(form)

    user_entity = user_logic.logic.getCurrentUser()
    fields = {'user': user_entity,
              'scope_path': kwargs['scope_path'],
              'status': 'active'}
    org_admin_entity = gci_org_admin_logic.logic.getForFields(
        fields, unique=True)

    bulk_create_tasks.spawnBulkCreateTasks(properties['data'],
                                           org_admin_entity)

    return http.HttpResponseRedirect(
        request.path + '?%s=%s' % (params['submit_msg_param_name'],
                                   params['bulk_create_message_idx']))

  @decorators.merge_params
  @decorators.check_access
  def suggestTask(self, request, access_type, page_name=None,
                  params=None, **kwargs):
    """View used to allow mentors to create or edit a task.

    Tasks created by mentors must be approved by org admins
    before they are published.
    """
    params = dicts.merge(params, self._params)

    if 'link_id' in kwargs:
      # extend create_form to include difficulty levels
      params['mentor_form'] = self._getTagsForProgram(
          'base_edit_form', params, **kwargs)
      try:
        entity = self._logic.getFromKeyFieldsOr404(kwargs)
      except out_of_band.Error, error:
        return helper.responses.errorResponse(
            error, request, template=params['error_public'])
    else:
      # extend create_form to include difficulty levels
      params['mentor_form'] = self._getTagsForProgram(
          'base_create_form', params, **kwargs)
      entity = None

    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    context['page_name'] = page_name

    if request.method == 'POST':
      return self.suggestTaskPost(request, context,
                                  params, entity)
    else:
      return self.suggestTaskGet(request, context,
                                 params, entity, kwargs)

  def suggestTaskPost(self, request, context, params, entity):
    """Handles the POST request for the suggest task view.
    """
    form = params['mentor_form'](request.POST)

    if not form.is_valid():
      return self._constructResponse(request, None, context, form, params)

    _, fields = helper.forms.collectCleanedFields(form)
    # TODO: this non-standard view shouldn't call _editPost but its own method
    self._editPost(request, entity, fields)

    logic = params['logic']
    if entity:
      entity = logic.updateEntityProperties(entity, fields)
    else:
      # TODO: Redirect to standard edit page which already has the ability to
      # hide certain fields.
      # get the mentor entity of the current user that is suggesting the task
      user_entity = user_logic.logic.getCurrentUser()

      filter = {'user': user_entity,
                'scope': fields['scope'],
                'status': 'active'}

      mentor_entity = gci_mentor_logic.logic.getForFields(filter, unique=True)

      # pylint: disable=E1103
      fields['mentors'] = [mentor_entity.key()]

      entity = logic.updateOrCreateFromFields(fields)

    page_params = params['edit_params']

    request.path = gci_redirects.getSuggestTaskRedirect(entity, params)

    return helper.responses.redirectToChangedSuffix(
        request, None, params=page_params)

  def suggestTaskGet(self, request, context, params, entity, seed):
    """Handles the GET request for the suggest task view.
    """
    if entity:
      # populate form with the existing entity
      form = params['mentor_form'](instance=entity)

      self._editGet(request, entity, form)
    elif seed:
      form = params['mentor_form'](initial=seed)
    else:
      form = params['mentor_form']()

    # message will be displayed when the task was saved
    context['notice'] = requests.getSingleIndexedParamValue(
        request, params['submit_msg_param_name'],
        values=params['save_message'])

    return self._constructResponse(request, entity, context, form, params)

  @decorators.merge_params
  @decorators.check_access
  def listOrgTasks(self, request, access_type,
                   page_name=None, params=None, **kwargs):
    """See base.View.list()
    """
    if request.method == 'POST':
      return self.listOrgTasksPost(request, params, **kwargs)
    else: # request.method == 'GET'
      return self.listOrgTasksGet(request, page_name, params, **kwargs)

  def listOrgTasksPost(self, request, params, **kwargs):
    """Handles the POST request for the list tasks view.
    """

    # get the org entity for which we are listing these tasks
    org_entity = gci_org_logic.logic.getFromKeyNameOr404(
        kwargs['scope_path'])

    post_dict = request.POST

    items = simplejson.loads(post_dict.get('data', '[]'))
    button_id = post_dict.get('button_id', '')

    if button_id == 'approve':
      changed_status = 'Unpublished'
    elif button_id == 'publish':
      changed_status = 'Open'
    elif button_id == 'unapprove':
      changed_status = 'Unapproved'

    task_keys = [item['key'] for item in items]

    tasks = []
    for key_name in task_keys:
      task_entity = gci_task_logic.logic.getFromKeyName(key_name)

      # Of course only the tasks from this organization and those with a valid
      # state can be updated.
      if task_entity and task_entity.scope.key() == org_entity.key() and \
          task_entity.status in ['Unapproved', 'Unpublished']:
        task_entity.status = changed_status

        tasks.append(task_entity)

    # bulk put the task_entities
    db.put(tasks)

    # return a 200 response to signal that all is okay
    return http.HttpResponseRedirect('')

  def getListTasksData(self, request, params_collection, org_entity):
    """Returns the list data for Organization Tasks list.

    Args:
      request: HTTPRequest object
      params_collection: List of list Params indexed with the idx of the list
      org_entity: GCIOrganization entity for which the lists are generated
    """

    idx = lists.getListIndex(request)

    # default list settings
    visibility = 'public'

    filter = {
        'scope': org_entity
        }

    if idx == 0:
      filter['status'] = ['Unapproved', 'Unpublished']
    elif idx == 1:
      filter['status'] = ['Open', 'Reopened']
    elif idx == 2:
      filter['status'] = ['ClaimRequested', 'Claimed', 'ActionNeeded',
                          'NeedsWork', 'NeedsReview']
    elif idx == 3:
      filter['status'] = ['Closed', 'AwaitingRegistration']
    elif idx == 4:
      filter['status'] = ['Invalid']
    else:
      return lists.getErrorResponse(request, "idx not valid")

    all_d = gci_task_model.TaskDifficultyTag.all().fetch(100)
    all_t = gci_task_model.TaskTypeTag.all().fetch(100)
    args = [all_d, all_t]

    params = params_collection[idx]
    contents = lists.getListData(request, params, filter,
                                 visibility=visibility, args=args)

    return lists.getResponse(request, contents)

  def listOrgTasksGet(self, request, page_name, params, **kwargs):
    """Handles the GET request for the list tasks view.
    """

    org_entity =  gci_org_logic.logic.getFromKeyNameOr404(
        kwargs['scope_path'])

    list_params = params.copy() if params else {}

    tuapp_params = list_params.copy()

    tuapp_params['list_description'] = self.DEF_TASKS_LIST_UNAPPROVED_MSG

    user_account = user_logic.logic.getCurrentUser()

    # give a suggest page redirect if the user is a mentor
    filter = {
      'user': user_account,
      'program': org_entity.scope
    }
    org_admin_entity = gci_org_admin_logic.logic.getForFields(
        filter, unique=True)
    mentor_entity = gci_mentor_logic.logic.getForFields(
        filter, unique=True)

    if org_admin_entity:
      tuapp_params['public_row_extra'] = lambda entity, *args: {
              'link': redirects.getEditRedirect(
                  entity, {'url_name': tuapp_params['url_name']})
      }
    elif mentor_entity:
      tuapp_params['public_row_extra'] = lambda entity, *args: {
              'link': gci_redirects.getSuggestTaskRedirect(
                  entity, {'url_name': tuapp_params['url_name']})
      }

    user_account = user_logic.logic.getCurrentUser()

    fields = {
        'user': user_account,
        'scope': org_entity,
        'status': 'active'
        }

    # give the capability to approve tasks for the org_admins
    if gci_org_admin_logic.logic.getForFields(fields, unique=True):
      tuapp_params['public_field_props'] = {
          'status': {
              'stype': 'select',
              'editoptions': {'value': ':All;^Unapproved$:Unapproved;'
                  '^Unpublished$:Approved but unpublished'}
          }
      }

      tuapp_params['public_conf_extra'] = {
          "multiselect": True,
      }

      tuapp_params['public_button_global'] = [
          {
          'bounds': [1,'all'],
          'id': 'approve',
          'caption': 'Approve',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
          },
          {
          'bounds': [1,'all'],
          'id': 'publish',
          'caption': 'Approve and/or Publish',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'all',
              }
          },
          {
          'bounds': [1,'all'],
          'id': 'unapprove',
          'caption': 'Unapprove',
          'type': 'post',
          'parameters': {
              'url': '',
              'keys': ['key'],
              'refresh': 'current',
              }
          }]

    topen_params = list_params.copy()
    topen_params['list_description'] = self.DEF_TASKS_LIST_OPEN_MSG

    tclaim_params = list_params.copy()
    tclaim_params['list_description'] = self.DEF_TASKS_LIST_CLAIM_MSG

    tclose_params = list_params.copy()
    tclose_params['list_description'] = self.DEF_TASKS_LIST_CLOSE_MSG

    tinvalid_params = list_params.copy()
    tinvalid_params['list_description'] = self.DEF_TASKS_LIST_INVALID_MSG

    if lists.isDataRequest(request):
      return self.getListTasksData(
          request, [tuapp_params, topen_params,
          tclaim_params, tclose_params, tinvalid_params], org_entity)

    contents = []
    order = ['modified_on']

    # add all non-public tasks to the list
    tuapp_list = lists.getListGenerator(request, tuapp_params,
                                        order=order, idx=0)
    contents.append(tuapp_list)

    # add all open tasks to the list
    topen_list = lists.getListGenerator(request, topen_params,
                                        order=order, idx=1)
    contents.append(topen_list)

    # add all claimed tasks to the list
    tclaim_list = lists.getListGenerator(request, tclaim_params,
                                         order=order, idx=2)
    contents.append(tclaim_list)

    # add all closed tasks to the list
    tclose_list = lists.getListGenerator(request, tclose_params,
                                         order=order, idx=3)
    contents.append(tclose_list)

    # add all invalid tasks to the list
    tinvalid_list = lists.getListGenerator(request, tinvalid_params,
                                           order=order, idx=4)
    contents.append(tinvalid_list)

    return self._list(request, list_params, contents, page_name)

  @decorators.merge_params
  @decorators.check_access
  def public(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """See base.View.public().
    """

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    helper.responses.useJavaScript(context, params['js_uses_all'])
    entity = None
    logic = params['logic']

    try:
      entity, comment_entities, ws_entities = (
          logic.getFromKeyFieldsWithCWSOr404(kwargs))
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'], context=context)

    # because we are not sure if the Task API has called this for us we do it
    entity, comment_entity = gci_task_logic.logic.updateTaskStatus(entity)
    if comment_entity:
      comment_entities.append(comment_entity)

    context['entity'] = entity
    context['entity_key_name'] = entity.key().id_or_name()
    context['entity_type'] = params['name']
    context['entity_type_url'] = params['url_name']
    context['page_name'] = ugettext('GCI Task: %s' % (entity.title))

    if entity.user:
      context['entity_user'] = entity.user

    user_entity = user_logic.logic.getCurrentUser()

    # get some entity specific context
    self.updatePublicContext(context, entity, comment_entities,
                             ws_entities, params)

    validation = self._constructActionsList(context, entity,
                                            user_entity, params)

    context = dicts.merge(params['context'], context)

    if request.method == 'POST':
      return self.publicPost(request, context, params, entity,
                             user_entity, validation, **kwargs)
    else: # request.method == 'GET'
      return self.publicGet(request, context, params, entity,
                            user_entity, **kwargs)

  def publicPost(self, request, context, params, entity,
                 user_entity=None, validation=None, **kwargs):
    """Handles the POST request for the entity's public page.

    Args:
        entity: the task entity
        user_entity: The currently logged in user.
        rest: see base.View.public()
    """

    from soc.modules.gci.logic.models import student as gci_student_logic
    from soc.modules.gci.logic.models import task_subscription as \
        gci_ts_logic

    form = params['comment_form'](request.POST)

    # we request to upload only one file as of now
    # request.file_uploads is coming from the blobstore middleware
    # TODO: Fix this once the appengine blobstore problem mentioned
    # in issue in blobstore middleware is fixed.
    if request.file_uploads:
      form.data['work_submission_upload'] = request.file_uploads[0]

    if not form.is_valid():
      if request.file_uploads:
        # delete the blob
        for file_blob in request.file_uploads:
          file_blob.delete()

        # form_error variable is set as a get variable in the URL
        # because the blobstore API always expects a HttpResponseRedirect
        # and if we send a redirect we have no way of transmitting
        # what errors occured on the form.
        # TODO: Javascript validations.
        redirect_to = '%s?form_error=1' % (redirects.getPublicRedirect(
            entity, params))
        return http.HttpResponseRedirect(redirect_to)
      else:
        template = params['public_template']
        context['comment_form'] = form
        return self._constructResponse(request, entity, context,
                                       form, params, template=template)

    _, fields = helper.forms.collectCleanedFields(form)

    changes = []

    action = fields['action']

    properties = None
    ws_properties = None
    update_gae_task = False
    update_student_ranking = False

    # saving the current task status to check if it changed to
    # AwaitingRegistration after the update to shoot a mail if it updated
    cur_task_status = entity.status

    # TODO: this can be separated into several methods that handle the changes
    if validation == 'claim_request' and action == 'request':
      st_filter = {
        'user': user_entity,
        'scope': entity.program,
        'status': 'active'
        }
      # Can be None
      student_entity = gci_student_logic.logic.getForFields(
          st_filter, unique=True)

      properties = {
          'status': 'ClaimRequested',
          'user': user_entity,
          'student': student_entity
          }

      # automatically subscribing the student to the task once he requests
      # his claim for the task
      gci_ts_logic.logic.subscribeUser(entity, user_entity)

      changes.extend([ugettext('User-Student'),
                      ugettext('Action-Claim Requested'),
                      ugettext('Status-%s' % (properties['status']))
                      ])
    elif (validation == 'claim_withdraw' or
        validation == 'needs_review') and action == 'withdraw':
      properties = {
          'user': None,
          'student': None,
          'status': 'Reopened',
          'deadline': None,
          }

      changes.extend([ugettext('User-Student'),
                      ugettext('Action-Withdrawn'),
                      ugettext('Status-%s' % (properties['status']))
                      ])
    elif validation == 'needs_review' and action == 'needs_review':
      properties = {
          'status': 'NeedsReview',
          }

      changes.extend([
          ugettext('User-Student'),
          ugettext('Action-Submitted work'),
          ugettext('Status-%s' % (properties['status']))])

      ws_properties = {
          'parent': entity,
          'program': entity.program,
          'org': entity.scope,
          'user': user_entity,
          'information': fields['comment'],
          'url_to_work': fields['work_submission_external'],

          # TODO (madhu): Fix it with BlobInfo
          'upload_of_work': fields['work_submission_upload'],
          'submitted_on': datetime.datetime.now(),
          }
    elif validation == 'accept_claim':
      if action == 'accept':
        deadline = datetime.datetime.now() + datetime.timedelta(
            hours=entity.time_to_complete)

        properties = {
            'status': 'Claimed',
            'deadline': deadline,
            }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Claim Accepted'),
                        ugettext('Status-%s' % (properties['status']))
                        ])

        update_gae_task = True
      if action == 'reject':
        properties = {
            'user': None,
            'student': None,
            'status': 'Reopened',
            'deadline': None,
            }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Claim Rejected'),
                        ugettext('Status-%s' % (properties['status']))
                        ])
    elif validation == 'close':
      if action == 'needs_work':
        properties = {
            'status': 'NeedsWork',
            }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Requested more work'),
                        ugettext('Status-%s' % (properties['status']))
                        ])

        if fields['extended_deadline'] > 0:
          current_deadline = entity.deadline if entity.deadline \
              else datetime.datetime.now()
          deadline = current_deadline + datetime.timedelta(
              hours=fields['extended_deadline'])

          properties['deadline'] = deadline

          changes.append(ugettext('DeadlineExtendedBy-%d hrs to %s' % (
              fields['extended_deadline'], deadline.strftime(
                  '%d %B %Y, %H :%M'))))

          update_gae_task = True
        else:
          changes.append(ugettext('NoDeadlineExtensionGiven'))
      elif action == 'reopened':
        properties = {
          'user': None,
          'student': None,
          'status': 'Reopened',
          'deadline': None,
          }

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Reopened'),
                        ugettext('Status-%s' % (properties['status']))
                        ])
      elif action == 'closed':
        properties = {
            'deadline': None,
            }

        if entity.student:
          properties['status'] = 'Closed'
          properties['closed_on'] = datetime.datetime.utcnow()
          update_student_ranking = True
        else:
          properties['status'] = 'AwaitingRegistration'

        changes.extend([ugettext('User-Mentor'),
                        ugettext('Action-Closed the task'),
                        ugettext('Status-%s' % (properties['status']))
                        ])

    comment_properties = {
        'parent': entity,
        'scope_path': entity.key().name(),
        'created_by': user_entity,
        'changes': changes,
        }

    if ws_properties:
      comment_properties['content'] = self.DEF_WS_MSG_FMT
    else:
      comment_properties['content'] = fields['comment']

    entity, comment_entity, ws_entity = \
        gci_task_logic.logic.updateEntityPropertiesWithCWS(
            entity, properties, comment_properties, ws_properties)

    if update_gae_task:
      task_update.spawnUpdateTask(entity)

    if update_student_ranking:
      ranking_update.startUpdatingTask(entity)

    # send a notification to the student if he completed his first task
    # and the status of the task changed from some non completed state
    # to AwaitingRegistration
    if (cur_task_status != 'AwaitingRegistration' and
        entity.status == 'AwaitingRegistration'):
      gci_notifications.sendParentalConsentFormRequired(
          entity.user, entity.program)

    # redirect to the same page
    return http.HttpResponseRedirect('')

  def publicGet(self, request, context, params, entity,
                user_account, **kwargs):
    """Handles the GET request for the entity's public page.

    Args:
        entity: the task entity
        rest see base.View.public()
    """

    form_error = request.GET.get('form_error')

    context['comment_form'] = params['comment_form']()

    if form_error:
      context['file_upload_errors'] = True

    template = params['public_template']

    return responses.respond(request, template, context=context)

  def updatePublicContext(self, context, entity, comment_entities,
                          ws_entities, params):
    """Updates the context for the public page with information.

    Args:
      context: the context that should be updated
      entity: a task used to set context
      params: dict with params for the view using this context
    """

    mentor_entities = db.get(entity.mentors)
    mentors_str = ""
    for mentor in mentor_entities:
      mentors_str += mentor.name() + ", "

    if mentors_str:
      context['mentors_str'] = mentors_str[:-2]
    else:
      context['mentors_str'] = "Not Assigned"

    context['difficulty_str'] = entity.taskDifficulty()

    context['task_type_str'] = entity.taskType()

    if entity.deadline:
      stop_dl = entity.program.timeline.stop_all_work_deadline
      context['time_to_complete'] = timeuntil(min(entity.deadline, stop_dl))
    else:
      if entity.status == 'NeedsReview':
        context['time_to_complete'] = 'No Time Left'
      else:
        context['time_to_complete'] = '%d hours' % (entity.time_to_complete)

    context['comments'] = comment_entities

    context['work_submissions'] = ws_entities

  def _constructActionsList(self, context, entity,
                            user_entity, params):
    """Constructs a list of actions for the task page and extends
    the comment form with this list.

    This method also returns the validation used by POST method to
    validate the user input data.

    Args:
      context: the context that should be updated
      entity: a task used to set context
      user_entity: user entity of the logged in user
      params: dict with params for the view using this context
    """

    # variable that holds what kind of validation this user
    # and task combination pass.
    validation = None

    # The following header messages are shown for non-logged in
    # general public, logged in public and the student.
    if entity.status is 'Closed':
      context['header_msg'] = self.DEF_TASK_CLOSED_MSG
      validation = 'closed'

    if entity.status == 'Open':
      context['header_msg'] = self.DEF_TASK_OPEN_MSG
    elif entity.status == 'Reopened':
      context['header_msg'] = self.DEF_TASK_REOPENED_MSG

    if user_entity:
      actions = [('noaction', 'Comment without action')]

      # if the user is logged give him the permission to claim
      # the task only if he none of program host, org admin or mentor
      filter = {
          'user': user_entity,
          }

      host_entity = host_logic.logic.getForFields(filter, unique=True)
      is_host = host_entity or user_logic.logic.isDeveloper(user=user_entity)

      filter['program'] = entity.program
      org_admin_entity = gci_org_admin_logic.logic.getForFields(
          filter, unique=True)
      mentor_entity = gci_mentor_logic.logic.getForFields(
          filter, unique=True)

      if host_entity or org_admin_entity or mentor_entity:
        validation, mentor_actions = self._constructMentorActions(
            context, entity, is_host)
        actions += mentor_actions
        if entity.status in ['Unapproved', 'Unpublished',
            'Open', 'ClaimRequested', 'Reopened']:
          if is_host or org_admin_entity:
            context['edit_link'] = redirects.getEditRedirect(entity, params)
          elif mentor_entity:
            context['suggest_link'] = gci_redirects.getSuggestTaskRedirect(
                entity, params)
      else:
        validation, student_actions = self._constructStudentActions(
            context, entity, user_entity)
        actions += student_actions

      # create the difficultly level field containing the choices
      # defined in the program entity
      dynafields = [
          {'name': 'action',
           'base': forms.ChoiceField,
           'label': 'Action',
           'required': False,
           'passthrough': ['initial', 'required', 'choices'],
           'choices': actions,
           },
         ]

      if validation == 'needs_review':
        try:
          context['blob_manage_url'] = blobstore.create_upload_url(
              redirects.getPublicRedirect(entity, params))
        except apiproxy_errors.FeatureNotEnabledError, message:
          logging.error(message)
        except apiproxy_errors.OverQuotaError, message:
          logging.error(message)

        dynafields.extend([
            {'name': 'work_submission_external',
             'base': forms.URLField,
             'label': 'Submit URL',
             'required': False,
             'help_text': 'Provide a link to your work in this box. '
                 'Please use the comment box if you need to explain '
                 'of your work.',
             },
            {'name': 'work_submission_upload',
             'base': forms.FileField,
             'label': 'Submit Work',
             'required': False,
             'help_text': 'Directly upload your work. It should be a single '
                 'file. In case you have multiple files create an archive '
                 'containing those files upload them.',
              }])

      if validation == 'close':
        dynafields.append(
            {'name': 'extended_deadline',
             'base': forms.IntegerField,
             'min_value': 1,
             'max_value': 7*24,
             'label': 'Extend deadline by',
             'required': False,
             'passthrough': ['min_value', 'max_value', 'required', 'help_text'],
             'help_text': 'Optional: Specify the number of hours by '
                 'which you want to extend the deadline for the task '
                 'for this student. ',
             })

      dynaproperties = params_helper.getDynaFields(dynafields)
      if validation == 'needs_review':
        dynaproperties['clean_work_submission_external'] = cleaning.clean_url(
            'work_submission_external')

      extended_comment_form = dynaform.extendDynaForm(
          dynaform=params['comment_form'],
          dynaproperties=dynaproperties)

      params['comment_form'] = extended_comment_form
    else:
      # list of statuses a task can be in after it is requested to be
      # claimed before closing or re-opening
      if entity.status == 'ClaimRequested':
        context['header_msg'] = self.DEF_TASK_CLAIMED_REQUESTED_MSG
      claim_status = [ 'Claimed', 'ActionNeeded',
                      'NeedsWork', 'NeedsReview']
      if entity.status in claim_status:
        context['header_msg'] = self.DEF_TASK_CLAIMED_MSG
      elif entity.status in ['AwaitingRegistration', 'Closed']:
        context['header_msg'] = self.DEF_TASK_CLOSED_MSG

      if accounts.getCurrentAccount():
        context['create_profile_url'] = redirects.getCreateProfileRedirect(
            {'url_name': 'user'})

    return validation

  def _constructMentorActions(self, context, entity, is_host=False):
    """Constructs the list of actions for mentors, org admins and
    hosts.
    """

    # variable that holds what kind of validation this user
    # and task combination pass.
    validation = None

    actions = []

    if is_host and entity.status in [
        'ClaimRequested', 'Claimed', 'ActionNeeded',
        'NeedsWork', 'Invalid']:
      actions.extend([('closed', 'Mark the task as complete')])
      validation = 'close'
    if entity.status == 'NeedsReview':
      context['header_msg'] = self.DEF_TASK_NEEDS_REVIEW_MSG
      actions.extend([('needs_work', 'Needs More Work'),
                      ('reopened', 'Reopen the task'),
                      ('closed', 'Mark the task as complete')])
      validation = 'close'
    elif entity.status == 'Claimed':
      context['header_msg'] = self.DEF_TASK_CLAIMED_BY_STUDENT_MSG
    elif entity.taskDifficulty().value == 0:
      # Prevent any action from being taken if the task difficulty is
      # not set properly, with the exception of 'NeedsReview' and the
      # 'Claimed' state, since the task cannot be edited then anyway.
      context['header_msg'] = self.DEF_TASK_MENTOR_FIX_MSG
    elif entity.status in ['Unapproved', 'Unpublished']:
      context['header_msg'] = self.DEF_TASK_UNPUBLISHED_MSG
      context['comment_disabled'] = True
    elif entity.status == 'Open':
      context['header_msg'] = self.DEF_CAN_EDIT_TASK_MSG
    elif entity.status == 'Reopened':
      context['header_msg'] = self.DEF_TASK_MENTOR_REOPENED_MSG
    elif entity.status == 'ClaimRequested':
      actions.extend([('accept', 'Accept claim request'),
                      ('reject', 'Reject claim request')])
      context['header_msg'] = self.DEF_TASK_CLAIM_REQUESTED_MSG
      validation = 'accept_claim'
    elif entity.status in ['AwaitingRegistration', 'Closed']:
      context['header_msg'] = self.DEF_TASK_CLOSED_MSG
    elif entity.status == 'ActionNeeded':
      context['header_msg'] = self.DEF_TASK_MENTOR_ACTION_NEEDED_MSG
    elif entity.status == 'Invalid':
      context['header_msg'] = self.DEF_TASK_INVALID_MSG

    return validation, actions

  def _constructStudentActions(self, context, entity, user_account):
    """Constructs the list of actions for students.
    """

    # variable that holds what kind of validation this user
    # and task combination pass.
    validation = None

    actions = []

    program_timeline = entity.program.timeline

    if timeline_helper.isBeforeEvent(program_timeline, 'task_claim_deadline'):
      if entity.status in ['Open', 'Reopened']:
        task_filter = {
            'user': user_account,
            'status': ['ClaimRequested', 'Claimed', 'ActionNeeded',
                       'NeedsWork', 'NeedsReview']
            }
        task_entities = gci_task_logic.logic.getForFields(task_filter)

        if len(task_entities) >= entity.program.nr_simultaneous_tasks:
          context['header_msg'] = self.DEF_MAX_TASK_LIMIT_MSG_FMT % (
              entity.program.nr_simultaneous_tasks)
          validation = 'claim_ineligible'
          return validation, actions

        task_filter['status'] = 'AwaitingRegistration'
        task_entities = gci_task_logic.logic.getForFields(task_filter)

        if task_entities:
          context['header_msg'] = self.DEF_AWAITING_REG_MSG
          validation = 'claim_ineligible'
        else:
          actions.append(('request', 'Request to claim the task'))
          validation = 'claim_request'
    else:
      context['header_msg'] = self.DEF_CLAIM_DEADLINE_PASSED_MSG

    # TODO: lot of double information here that can be simplified
    if timeline_helper.isBeforeEvent(program_timeline,
                                     'stop_all_work_deadline'):
      if entity.user and user_account.key() == entity.user.key():
        if entity.status  == 'ClaimRequested':
          context['header_msg'] = self.DEF_TASK_REQ_CLAIMED_BY_YOU_MSG
          context['pageheaderalert'] = True
          actions.append(('withdraw', 'Withdraw from the task'))
          validation = 'claim_withdraw'
        elif entity.deadline and entity.status in [
            'Claimed', 'NeedsWork', 'NeedsReview', 'ActionNeeded']:
          if entity.status == 'ActionNeeded':
            context['header_msg'] = self.DEF_TASK_ACTION_NEEDED_MSG
          else:
            context['header_msg'] = self.DEF_TASK_CLAIMED_BY_YOU_MSG
          actions.extend([
              ('withdraw', 'Withdraw from the task'),
              ('needs_review', 'Submit work and Request for review')])
          validation = 'needs_review'
        elif entity.status == 'NeedsReview':
          context['header_msg'] = self.DEF_TASK_NO_MORE_SUBMIT_MSG
          context['pageheaderalert'] = True
          actions.append(('withdraw', 'Withdraw from the task'))
          if entity.deadline and datetime.datetime.now() < entity.deadline:
            actions.append(
                ('needs_review', 'Submit work and Request for review'))
          validation = 'needs_review'
        elif entity.status == 'AwaitingRegistration':
          context['header_msg'] = self.DEF_STUDENT_SIGNUP_MSG % {
              'student_signup_redirect': redirects.getStudentApplyRedirect(
                  entity.program, {'url_name': 'gci/student'})}
        elif entity.status == 'Closed':
          context['header_msg'] = self.DEF_TASK_CMPLTD_BY_YOU_MSG
      else:
        if entity.status == 'ClaimRequested':
          context['header_msg'] = self.DEF_TASK_CLAIMED_REQUESTED_MSG
        if entity.status in ['Claimed', 'ActionNeeded', 'NeedsWork',
                             'NeedsReview']:
          context['header_msg'] = self.DEF_TASK_CLAIMED_MSG
        if entity.status in ['AwaitingRegistration', 'Closed']:
          context['header_msg'] = self.DEF_TASK_CLOSED_MSG
    else:
      context['header_msg'] = self.DEF_STOP_WORK_DEADLINE_MSG % {
          'program_name': entity.program.name}

    return validation, actions

  @decorators.merge_params
  @decorators.check_access
  def delete(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Shows the delete page for the entity specified by **kwargs.

    Args:
      request: the standard Django HTTP request object
      access_type : the name of the access type which should be checked
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
      kwargs: the Key Fields for the specified entity
    """

    params = params.copy()

    params['delete_redirect'] = '/%s/list_org_tasks/%s' % (
        params['url_name'], kwargs['scope_path'])

    return super(View, self).delete(request, access_type, page_name=page_name,
        params=params, **kwargs)


view = View()

bulk_create = decorators.view(view.bulkCreate)
create = decorators.view(view.create)
delete = decorators.view(view.delete)
edit = decorators.view(view.edit)
list = decorators.view(view.list)
list_org_tasks = decorators.view(view.listOrgTasks)
suggest_task = decorators.view(view.suggestTask)
public = decorators.view(view.public)
