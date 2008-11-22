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


from google.appengine.api import users

from django import forms
from django import http
from django.utils.translation import ugettext_lazy

from soc.models import request as request_model
from soc.logic import dicts
from soc.logic.models import request as request_logic
from soc.logic.models import user as user_logic
from soc.views import helper
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
    exclude = ['inheritance_line', 'requester', 'to', 'role', 
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

  def __init__(self, original_params=None):
    """

    Args:
      original_params: This dictionary should be filled with the parameters
    """

    params = {}
    params = dicts.merge(original_params, params)

    base.View.__init__(self, params=params)

  def invite(self, request, page_name=None, params=None, **kwargs):
    """Displays the request promotion to Role page.
    """

    new_params = {}

    new_params['list_template'] = 'soc/models/list.html'
    new_params['list_redirect_action'] = '/request/create/%s/%s' % (
        self._params['url_name'], kwargs['link_id'])
    new_params['name'] = self._params['name']
    new_params['name_short'] = self._params['name_short']
    new_params['name_plural'] = self._params['name_plural']
    new_params['instruction_text'] = \
        self.DEF_INVITE_INSTRUCTION_MSG_FMT % self._params

    params = dicts.merge(params, new_params)

    try:
      self.checkAccess('invite', request)
    except soc.views.out_of_band.AccessViolationResponse, alt_response:
      return alt_response.response()

    return user_view.list(request, page_name=page_name, params=params)

  def promote(self, request, page_name=None, **kwargs):
    """Displays the promote to Role page.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      kwargs: the Key Fields for the specified entity
    """

    properties = {
        'accepted': True,
        }

    entity = request_logic.logic.updateOrCreateFromFields(properties, **kwargs)

    # TODO(SRabbelier) finish this

  def accept(self, request, page_name=None, params=None, **kwargs):
    """Displays the accept a Role request page.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      kwargs: the Key Fields for the specified entity
    """

    entity = request_logic.logic.getFromFields(**kwargs)

    if entity.declined:
      properties = {
          'declined': False,
          }

      request_logic.logic.updateModelProperties(entity, **properties)

    if not entity.accepted:
      raise Error("The request has not yet been accepted")

    id = users.get_current_user()
    user = models.user.logic.getFromFields(email=id.email())

    if entity.user != user:
      raise Error("The request is being accepted by the wrong person")

    if entity.role != params['name'].lower():
      raise Error("The wrong module is handling the request")

    redirect = params['accept_redirect']
    suffix = self._logic.getKeySuffix(entity)

    return helper.responses.redirectToChangedSuffix(
        request, suffix, suffix)

  def decline(self, request, page_name=None, **kwargs):
    """Displays the decline a Role request page.

    Args:
      request: the standard Django HTTP request object
      page_name: the page name displayed in templates as page and header title
      kwargs: the Key Fields for the specified entity
    """

    properties = {
        'declined': True,
        }

    request_logic.logic.updateOrCreateFromFields(properties, **kwargs)

    redirect = self._params['decline_redirect']
    suffix = self._logic.getKeySuffix(entity)

    return helper.responses.redirectToChangedSuffix(
        request, suffix, suffix)

  def getDjangoURLPatterns(self):
    """See base.View.getDjangoURLPatterns().
    """

    params = {}
    default_patterns = self._params['django_patterns_defaults']
    default_patterns += [
        (r'^%(url_name)s/invite/%(lnp)s$',
            'soc.views.models.%s.invite', 'Invite %(name_short)s')]

    params['django_patterns_defaults'] = default_patterns
    patterns = super(RoleView, self).getDjangoURLPatterns(params)

    return patterns

