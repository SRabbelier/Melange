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
from soc.views.models import user as user_view

import soc.models.request
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


class RoleView(base.View):
  """Views for all entities that inherit from Role.

  All views that only Role entities have are defined in this subclass.
  """
  
  DEF_INVITE_INSTRUCTION_MSG_FMT = ugettext_lazy(
      'Please use this form to invite someone to become a %(name)s.')

  def __init__(self, params=None):
    """

    Args:
      original_params: This dictionary should be filled with the parameters
    """

    base.View.__init__(self, params=params)

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
    new_params['instruction_text'] = \
        self.DEF_INVITE_INSTRUCTION_MSG_FMT % self._params

    new_params = dicts.merge(new_params, params)
    params = dicts.merge(new_params, user_view.view._params)

    try:
      access.checkAccess('invite', request, rights=params['rights'])
    except out_of_band.Error, error:
      return error.response(request)

    content = helper.lists.getListContent(request, params, user_logic.logic)
    contents = [content]

    return self._list(request, params, contents, page_name)

  def getDjangoURLPatterns(self, params=None):
    """See base.View.getDjangoURLPatterns().
    """

    default_patterns = self._params['django_patterns_defaults']
    default_patterns += [
        (r'^%(url_name)s/invite/%(lnp)s$',
            'soc.views.models.%s.invite', 'Invite %(name_short)s')]

    params = {}
    params['django_patterns_defaults'] = default_patterns

    params = dicts.merge(params, self._params)
    patterns = super(RoleView, self).getDjangoURLPatterns(params)

    return patterns

