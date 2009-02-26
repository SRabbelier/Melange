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

"""Views for Club App profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms

from soc.logic import cleaning
from soc.logic import dicts
from soc.logic import models as model_logic
from soc.logic.models import host as host_logic
from soc.logic.models import club_app as club_app_logic
from soc.views.helper import access
from soc.views.models import group_app

import soc.logic.dicts


class View(group_app.View):
  """View methods for the Club Application model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.Checker(params)
    rights['create'] = ['checkIsUser']
    rights['delete'] = [('checkCanEditGroupApp',
                         [club_app_logic.logic])]
    rights['edit'] = [('checkCanEditGroupApp',
                       [club_app_logic.logic])]
    rights['list'] = ['checkIsDeveloper']
    rights['list_self'] = ['checkIsUser']
    rights['public'] = [('checkCanEditGroupApp',
                         [club_app_logic.logic])]
    # TODO(ljvderijk) make sure host role check is fixed
    rights['review'] = [('checkHasActiveRoleForScope', host_logic.logic),
                        ('checkCanReviewGroupApp', [club_app_logic.logic])]
    rights['review_overview'] = [('checkHasActiveRoleForScope', host_logic.logic)]

    new_params = {}

    new_params['rights'] = rights
    new_params['logic'] = club_app_logic.logic

    new_params['sidebar_grouping'] = 'Clubs'

    new_params['create_extra_dynaproperties'] = {
        'clean': cleaning.validate_new_group('link_id', 'scope_path',
            model_logic.club, club_app_logic)}

    # get rid of the clean method
    new_params['edit_extra_dynaproperties'] = {
        'clean': (lambda x: x.cleaned_data)}

    new_params['name'] = "Club Application"
    new_params['name_plural'] = "Club Applications"
    new_params['name_short'] = "Club App"
    new_params['url_name'] = "club_app"
    new_params['group_name'] = "Club"
    new_params['group_url_name'] = 'club'

    new_params['review_template'] = 'soc/club_app/review.html'

    new_params['sidebar_additional'] = [
        ('/%(url_name)s/list_self/' % new_params,
         'List all my %(name_plural)s' % new_params, 'list_self'),
        ('/%(url_name)s/review_overview/' % new_params,
         'Review %(name_plural)s' % new_params, 'review_overview')]

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)


view = View()

admin = view.admin
create = view.create
delete = view.delete
edit = view.edit
list = view.list
list_self = view.listSelf
public = view.public
export = view.export
review = view.review
review_overview = view.reviewOverview

