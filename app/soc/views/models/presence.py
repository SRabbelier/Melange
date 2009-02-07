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

"""Views for Models with a "presence" on a Melange site.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from google.appengine.ext import db

from django import forms
from django.utils.translation import ugettext

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import validate
from soc.logic.models import document as document_logic
from soc.views import helper
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import widgets
from soc.views.models import base

import soc.models.presence
import soc.logic.models.presence
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


class View(base.View):
  """View methods for the Presence model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['home'] = ['allow']

    new_params = {}
    new_params['rights'] = rights

    new_params['extra_dynaexclude'] = ['home', 'tos']
    new_params['home_template'] = 'soc/presence/home.html'

    new_params['create_extra_dynafields'] = {
        # add cleaning of the link id and feed url
        'clean_link_id': cleaning.clean_link_id('link_id'),
        'clean_feed_url': cleaning.clean_feed_url,
        }

    new_params['edit_extra_dynafields'] = {
        'home_link_id': widgets.ReferenceField(
            reference_url='document', filter=['scope_path'],
            required=False, label=ugettext('Home page Document link ID'),
            help_text=soc.models.work.Work.link_id.help_text),
    }

    patterns = []

    page_name = "Home"
    patterns += [(r'^%(url_name)s/(?P<access_type>home)/%(key_fields)s$',
                  'soc.views.models.%(module_name)s.home',
                  page_name)]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.check_access
  def home(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """See base.View.public().

    Overrides public_template to point at 'home_template'.
    """

    new_params = {}
    new_params['public_template'] = self._params['home_template']

    params = dicts.merge(params, new_params)

    return self.public(request, access_type,
                       page_name=page_name, params=params, **kwargs)

  def _public(self, request, entity, context):
    """See base.View._public().
    """

    if not entity:
      return

    try:
      home_doc = entity.home
    except db.Error:
      home_doc = None

    if home_doc:
      home_doc.content = helper.templates.unescape(home_doc.content)
      context['home_document'] = home_doc

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    try:
      if entity.home:
        form.fields['home_link_id'].initial = entity.home.link_id
    except db.Error:
      pass

    super(View, self)._editGet(request, entity, form)

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    if 'home_link_id' not in fields:
      return super(View, self)._editPost(request, entity, fields)

    scope_path = self._logic.getKeyNameFromFields(fields)

    key_fields = {
        'scope_path': scope_path,
        'link_id': fields['home_link_id'],
        'prefix': self._params['document_prefix'],
        }

    # TODO notify the user if home_doc is not found
    home_doc = document_logic.logic.getFromKeyFields(key_fields)

    fields['home'] = home_doc

    super(View, self)._editPost(request, entity, fields)
