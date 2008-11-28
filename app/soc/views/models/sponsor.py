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
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
    '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from google.appengine.api import users

from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import dicts
from soc.logic import cleaning
from soc.logic import models
from soc.views import helper
from soc.views.helper import dynaform
from soc.views.helper import widgets
from soc.views.models import base

import soc.models.sponsor
import soc.logic.models.sponsor
import soc.logic.dicts
import soc.views.helper
import soc.views.helper.widgets


CreateForm = dynaform.newDynaForm(
    dynabase = helper.forms.BaseForm,
    dynamodel = soc.models.sponsor.Sponsor,
    dynaexclude = ['scope', 'scope_path', 'founder', 'home'],
    dynafields = {
        'clean_link_id': cleaning.clean_new_link_id(models.sponsor.logic),
        'clean_feed_url': cleaning.clean_feed_url,
        },
    )


EditForm = dynaform.extendDynaForm(
    dynaform = CreateForm,
    dynafields = {
         'clean_link_id': cleaning.clean_link_id,
        'link_id': forms.CharField(widget=helper.widgets.ReadOnlyInput()),
        'founded_by': forms.CharField(widget=helper.widgets.ReadOnlyInput(),
                               required=False),
        },
    )


class View(base.View):
  """View methods for the Sponsor model.
  """

  def __init__(self, original_params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      original_params: a dict with params for this View 
    """    

    self._logic = soc.logic.models.sponsor.logic
    
    params = {}

    params['name'] = "Sponsor"
    params['name_short'] = "Sponsor"
    params['name_plural'] = "Sponsors"
    # TODO(pawel.solyga): create url_name and module_name automatically 
    # from name. Make that work for all other Views too. Hopefully 
    # solution that will be implemented in base View.
    params['url_name'] = "sponsor"
    params['module_name'] = "sponsor"
       
    params['edit_form'] = EditForm
    params['create_form'] = CreateForm

    # TODO(tlarsen): Add support for Django style template lookup
    params['edit_template'] = 'soc/sponsor/edit.html'
    params['public_template'] = 'soc/group/public.html'

    params['list_row'] = 'soc/group/list/row.html'
    params['list_heading'] = 'soc/group/list/heading.html'

    params = dicts.merge(original_params, params)
    
    base.View.__init__(self, params=params)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """
    
    # fill in the founded_by with data from the entity
    form.fields['founded_by'].initial = entity.founder.name

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    account = users.get_current_user()
    user = soc.logic.models.user.logic.getForFields({'account': account},
                                                    unique=True)
    if not entity:
      # only if we are creating a new entity we should fill in founder
      fields['founder'] = user


view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
