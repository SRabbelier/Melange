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

"""Params related methods.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.models import linkable
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import dynaform
from soc.views.helper import redirects


DEF_LIST_DESCRIPTION_FMT = ugettext(
    'List of %(name_plural)s in Google Open Source Programs.')

DEF_CREATE_INSTRUCTION_MSG_FMT = ugettext(
      'Please use this form to select a %(name).')

DEF_SUBMIT_MSG_PARAM_NAME = 's'
DEF_SUBMIT_MSG_PROFILE_SAVED = 0


def constructParams(params):
  """Constructs a new params dictionary based on params.

  Params usage:
    The params dictionary is passed to getCreateForm and getEditForm,
    see their docstring on how they use it.

    rights: The rights value is merged with a default rights
      dictionary and then used as rights value.
    url_name: The url_name value is used in constructing several
      redirects as the first part of the url.
    module_name: The module_name value is used in constructing the
      location of several templates. It is expected that it matches
      the part after "/templates/soc/" for this View.
    name_plural: The name_plural argument is provided to the
      LIST_DESCRIPTION when constructing the list_description field.
    extra_dynainclude: The extra_dynainclude value is used when
      constructing the create_dynainclude value.
    extra_dynaexclude: The extra_dynaexclude value is used when
      constructing the create_dynaexclude value.
    logic: The logic value is used as argument to save the scope_logic
      and create a create form.
  """

  logic = params['logic']

  rights = access.Checker(params)
  rights['unspecified'] = []
  rights['any_access'] = ['checkIsLoggedIn']
  rights['show'] = ['checkIsUser']
  rights['create'] = ['checkIsDeveloper']
  rights['edit'] = ['checkIsDeveloper']
  rights['delete'] = ['checkIsDeveloper']
  rights['list'] = ['checkIsDeveloper']
  rights['pick'] = ['checkHasPickGetArgs']

  new_params = {}
  new_params['scope_logic'] = logic.getScopeLogic()

  if 'name_short' not in params:
    params['name_short'] = params['name']

  if 'name_plural' not in params:
    params['name_plural'] = params['name'] + 's'

  if 'module_name' not in params:
    params['module_name'] = params['name_short'].replace(' ', '_').lower()

  if 'url_name' not in params:
    params['url_name'] = params['module_name']

  # Do not expand edit_redirect to allow it to be overriden without suffix
  new_params['edit_redirect'] = '/%(url_name)s/edit/%(suffix)s'
  new_params['missing_redirect'] = '/%(url_name)s/create' % params
  new_params['delete_redirect'] = '/%(url_name)s/list' % params
  new_params['invite_redirect'] = '/request/list'
  new_params['edit_cancel_redirect'] = '/%(url_name)s/list' % params

  new_params['sidebar'] = None
  new_params['sidebar_grouping'] = 'main'
  new_params['sidebar_defaults'] = [
      ('/%s/create', 'New %(name)s', 'create'),
      ('/%s/list', 'List %(name_plural)s', 'list'),
      ]
  new_params['sidebar_additional'] = []

  new_params['link_id_arg_pattern'] = linkable.LINK_ID_ARG_PATTERN
  new_params['link_id_pattern_core'] = linkable.LINK_ID_PATTERN_CORE
  new_params['scope_path_pattern'] = getScopePattern(params)

  new_params['django_patterns'] = None
  new_params['extra_django_patterns'] = []
  new_params['django_patterns_defaults'] = [
      (r'^%(url_name)s/(?P<access_type>show)/%(key_fields)s$',
          'soc.views.models.%(module_name)s.public', 'Show %(name_short)s'),
      (r'^%(url_name)s/(?P<access_type>export)/%(key_fields)s$',
          'soc.views.models.%(module_name)s.export', 'Export %(name_short)s'),
      (r'^%(url_name)s/(?P<access_type>create)$',
          'soc.views.models.%(module_name)s.create', 'Create %(name_short)s'),
      (r'^%(url_name)s/(?P<access_type>delete)/%(key_fields)s$',
          'soc.views.models.%(module_name)s.delete', 'Delete %(name_short)s'),
      (r'^%(url_name)s/(?P<access_type>edit)/%(key_fields)s$',
          'soc.views.models.%(module_name)s.edit', 'Edit %(name_short)s'),
      (r'^%(url_name)s/(?P<access_type>list)$',
          'soc.views.models.%(module_name)s.list', 'List %(name_plural)s'),
      (r'^%(url_name)s/(?P<access_type>pick)$',
          'soc.views.models.%(module_name)s.pick', 'Pick %(name_short)s'),
      ]

  if not params.get('no_create_with_scope'):
    new_params['django_patterns_defaults'] += [
        (r'^%(url_name)s/(?P<access_type>create)/%(scope)s$',
        'soc.views.models.%(module_name)s.create', 'Create %(name_short)s')]

  if not params.get('no_create_with_key_fields'):
    new_params['django_patterns_defaults'] += [
        (r'^%(url_name)s/(?P<access_type>create)/%(key_fields)s$',
        'soc.views.models.%(module_name)s.create', 'Create %(name_short)s')]

  new_params['public_template'] = 'soc/%(module_name)s/public.html' % params
  new_params['export_template'] = 'soc/%(module_name)s/export.html' % params
  new_params['create_template'] = 'soc/models/edit.html'
  new_params['edit_template'] = 'soc/models/edit.html'
  new_params['list_template'] = 'soc/models/list.html'
  new_params['invite_template'] = 'soc/models/invite.html'

  new_params['export_content_type'] = None

  new_params['error_public'] = 'soc/%(module_name)s/error.html' % params
  new_params['error_export'] = new_params['error_public']
  new_params['error_edit'] = new_params['error_public']

  new_params['list_main'] = 'soc/list/main.html'
  new_params['list_pagination'] = 'soc/list/pagination.html'
  new_params['list_row'] = 'soc/%(module_name)s/list/row.html' % params
  new_params['list_heading'] = 'soc/%(module_name)s/list/heading.html' % params

  new_params['list_action'] = (redirects.getEditRedirect, params)
  new_params['list_params'] = {
      'list_action': 'action',
      'list_description': 'description',
      'list_main': 'main',
      'list_pagination': 'pagination',
      'list_row': 'row',
      'list_heading': 'heading',
      }

  new_params['list_description'] = DEF_LIST_DESCRIPTION_FMT % params
  new_params['save_message'] = [ugettext('%(name)s saved.' % params)]
  new_params['submit_msg_param_name'] = DEF_SUBMIT_MSG_PARAM_NAME
  new_params['edit_params'] = {
      DEF_SUBMIT_MSG_PARAM_NAME: DEF_SUBMIT_MSG_PROFILE_SAVED,
      }

  new_params['dynabase'] = helper.forms.BaseForm

  create_dynafields = {
      'clean_link_id': cleaning.clean_link_id('link_id'),
      'clean_feed_url': cleaning.clean_feed_url,
      }
  create_dynafields.update(params.get('create_extra_dynafields', {}))

  new_params['create_dynainclude'] = [] + params.get('extra_dynainclude', [])
  new_params['create_dynaexclude'] = ['scope', 'scope_path'] + \
      params.get('extra_dynaexclude', [])
  new_params['create_dynafields'] = create_dynafields

  edit_dynafields = {
      'clean_link_id': cleaning.clean_link_id('link_id'),
      'link_id': forms.CharField(widget=helper.widgets.ReadOnlyInput()),
      }
  edit_dynafields.update(params.get('edit_extra_dynafields', {}))

  new_params['edit_dynainclude'] = None
  new_params['edit_dynaexclude'] = None
  new_params['edit_dynafields'] = edit_dynafields

  params = dicts.merge(params, new_params)

  # These need to be constructed separately, because they require
  # parameters that can be defined either in params, or new_params.
  if not 'create_form' in params:
    params['create_form'] = getCreateForm(params, logic.getModel())

  if not 'edit_form' in params:
    params['edit_form'] = getEditForm(params, params['create_form'])

  if not 'key_fields_pattern' in params:
    params['key_fields_pattern'] = getKeyFieldsPattern(params)

  # merge already done by access.Checker
  params['rights'] = rights

  return params


def getCreateForm(params, model):
  """Constructs a new CreateForm using params.

  Params usage:
    dynabase: The dynabase value is used as the base argument to
      dynaform.newDynaForm.
    logic: The logic value is used to get the model argument to newDynaForm.
    create_dynainclude: same as dynabase, but as dynainclude argument
    create_dynaexclude: same as dynabase, but as dynaexclude argument
    create_dynafields: same as dynabase, but as dynafields argument
  """

  create_form = dynaform.newDynaForm(
    dynabase = params['dynabase'],
    dynamodel = model,
    dynainclude = params['create_dynainclude'],
    dynaexclude = params['create_dynaexclude'],
    dynafields = params['create_dynafields'],
    )

  return create_form


def getEditForm(params, base_form):
  """Constructs a new EditForm using params.

  Params usage:
    create_form: The dynabase value is used as the dynaform argument
      to dyanform.extendDynaForm.
    edit_dynainclude: same as create_form, but as dynainclude argument
    edit_dynaexclude: same as create_form, but as dynaexclude argument
    edit_dynafields: same as create_form, but as dynafields argument
  """

  edit_form = dynaform.extendDynaForm(
    dynaform = base_form,
    dynainclude = params['edit_dynainclude'],
    dynaexclude = params['edit_dynaexclude'],
    dynafields = params['edit_dynafields'],
    )

  return edit_form


def getKeyFieldsPattern(params):
  """Returns the Django pattern for this View's entity.
  """

  names = params['logic'].getKeyFieldNames()
  patterns = []

  for name in names:
    if name == 'scope_path':
      pattern = params['scope_path_pattern']
    else:
      pattern = r'(?P<%s>%s)' % (name, linkable.LINK_ID_PATTERN_CORE)
    patterns.append(pattern)

  result = '/'.join(patterns)
  return result


def getScopePattern(params):
  """Returns the Scope pattern for this entity.
  """

  logic = params['logic']
  depth = logic.getScopeDepth()
  if depth is None:
    return linkable.SCOPE_PATH_ARG_PATTERN

  regexps = [linkable.LINK_ID_PATTERN_CORE for i in range(depth)]
  regexp = '/'.join(regexps)
  return r'(?P<scope_path>%s)' % regexp
