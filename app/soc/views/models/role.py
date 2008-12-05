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

"""Views for Sponsor profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.models import base
from soc.views.models import sponsor as sponsor_view
from soc.views.models import user as user_view

import soc.models.request
import soc.views.helper.lists
import soc.views.helper.responses
import soc.views.helper.widgets


class RequestForm(helper.forms.BaseForm):
  """Django form displayed when creating a new invititation/request.
  """

  class Meta:
    """Inner Meta class that defines some behavior for the form.
    """

    #: db.Model subclass for which the form will gather information
    model = soc.models.request.Request

    #: Exclude pretty much everything, model=None would 
    #: also remove the help text etc. 
    exclude = ['requester', 'to', 'role', 
        'accepted', 'declined']

  requester = forms.CharField(widget=helper.widgets.ReadOnlyInput())

  role = forms.CharField(widget=helper.widgets.ReadOnlyInput())

  to = forms.CharField(widget=helper.widgets.ReadOnlyInput())


class View(base.View):
  """Views for all entities that inherit from Role.

  All views that only Role entities have are defined in this subclass.
  """
  
  DEF_INVITE_INSTRUCTION_MSG_FMT = ugettext_lazy(
      'Please use this form to invite someone to become a %(name)s.')

  def __init__(self, params=None):
    """

    Args:
      params: This dictionary should be filled with the parameters
    """

    new_params = {}

    patterns = [(r'^%(url_name)s/invite/%(lnp)s$',
        'soc.views.models.%(module_name)s.invite',
        'Invite %(name_short)s')]

    new_params['extra_django_patterns'] = patterns
    new_params['scope_redirect'] = redirects.getInviteRedirect

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def invite(self, request, page_name=None, params=None, **kwargs):
    """Displays the request promotion to Role page.
    """

    if not params:
      params = {}
    new_params = {}
    group_scope = kwargs['link_id']

    new_params['list_action'] = (redirects.getCreateRequestRedirect, 
        {'group_scope' : group_scope,
        'url_name' : self._params['url_name'] })
    new_params['list_description'] = \
        self.DEF_INVITE_INSTRUCTION_MSG_FMT % self._params

    new_params = dicts.merge(new_params, params)
    params = dicts.merge(new_params, user_view.view._params)
    params['logic'] = user_logic.logic

    try:
      access.checkAccess('invite', request, rights=params['rights'])
    except out_of_band.Error, error:
      return helper.responses.errorResponse(error, request)

    content = helper.lists.getListContent(request, params)
    contents = [content]

    return self._list(request, params, contents, page_name)
