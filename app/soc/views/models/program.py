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

"""Views for Programs.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import cleaning
from soc.logic.models import sponsor as sponsor_logic
from soc.views.helper import redirects
from soc.views.models import base
from soc.views.models import sponsor as sponsor_view
from soc.views import helper

import soc.logic.models.program


class View(base.View):
  """View methods for the Sponsor model.
  """

  DEF_CREATE_INSTRUCTION_MSG_FMT = ugettext_lazy(
      'Please use this form to select a Sponsor for the new Program')

  def __init__(self, original_params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View 
    """    

    params = {}
    params['logic'] = soc.logic.models.program.logic

    params['name'] = "Program"
    params['name_short'] = "Program"
    params['name_plural'] = "Programs"
    params['url_name'] = "program"
    params['module_name'] = "program"

    params['extra_dynaexclude'] = ['home']
    params['create_extra_dynafields'] = {
        'scope_path': forms.CharField(widget=forms.HiddenInput,
                                   required=False),
         'clean_link_id': cleaning.clean_link_id,
        }

    params = dicts.merge(original_params, params)

    base.View.__init__(self, params=params)

  def create(self, request, page_name=None, params=None, **kwargs):
    """Specialized create view to enforce needing a scope_path

    This view simply gives control to the base.View.create if the
    scope_path is specified in kwargs. If it is not present, it
    instead displays the result of self.selectSponsor. Refer to the
    respective docstrings on what they do.

    Args: 
      see base.View.create
    """

    if 'scope_path' in kwargs:
      return super(View, self).create(request, page_name=page_name,
          params=params, **kwargs)

    params = dicts.merge(params, self._params)
    return self.selectSponsor(request, page_name, params)

  def selectSponsor(self, request, page_name, params):
    """Displays a list page allowing the user to select a Sponsor

    After having selected the Sponsor, the user is redirected to the
    'create a new program' page with the scope_path set appropriately.

    Params usage:
      The params dictionary is passed to getCreateProgramRedirect from
        the redirects module, please see the docstring for
        getCreateProgramRedirect on how it uses it.
      The params dictionary is also passed to getListContent from
        the helper.list module, please refer to its docstring also.
      The params dictionary is passed to self._list as well, refer
        to its docstring for details on how it uses it.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      params: a dict with params for this View
    """

    new_params = {}
    new_params['list_action'] = (redirects.getCreateProgramRedirect, params)
    new_params['instruction_text'] = \
        self.DEF_CREATE_INSTRUCTION_MSG_FMT % self._params

    params = dicts.merge(new_params, params)
    params = dicts.merge(params, sponsor_view.view._params)

    content = helper.lists.getListContent(request, params, sponsor_logic.logic)
    contents = [content]

    return self._list(request, params, contents, page_name)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    # fill in the email field with the data from the entity
    form.fields['scope_path'].initial = entity.scope_path

  def getDjangoURLPatterns(self, params=None):
    """See base.View.getDjangoURLPatterns().
    """

    default_patterns = self._params['django_patterns_defaults']
    default_patterns += [
        (r'^%(url_name)s/create/(?P<scope_path>%(ulnp)s)$',
            'soc.views.models.%s.create', 'Create %(name_short)s')]

    params = {}
    params['django_patterns_defaults'] = default_patterns

    params = dicts.merge(params, self._params)
    patterns = super(View, self).getDjangoURLPatterns(params)

    return patterns


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
