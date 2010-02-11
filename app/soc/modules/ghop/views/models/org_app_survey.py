#!/usr/bin/env python2.5
#
# Copyright 2010 the Melange authors.
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

"""Views for GHOPOrgAppSurveys.
"""


__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import org_app_survey

from soc.modules.ghop.logic.models.org_app_survey import logic as org_app_logic
from soc.modules.ghop.logic.models.program import logic as program_logic
from soc.modules.ghop.logic.models.student import logic as student_logic
from soc.modules.ghop.tasks import org_app_survey as org_app_survey_tasks
from soc.modules.ghop.views.helper import access
from soc.modules.ghop.views.models.program import view as program_view


class View(org_app_survey.View):
  """View methods for the GHOPOrgAppSurveys model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = access.GHOPChecker(params)
    rights['any_access'] = ['allow']
    rights['show'] = ['checkIsDeveloper']
    rights['create'] = [('checkIsHostForProgramInScope', program_logic)]
    rights['edit'] = [('checkIsHostForProgramInScope', program_logic)]
    rights['delete'] = ['checkIsDeveloper']
    rights['list'] = ['checkIsDeveloper']
    rights['list_self'] = ['checkIsUser']
    rights['record'] = [('checkHasAny', [
        [('checkCanViewOrgAppRecord', [org_app_logic]),
        ('checkIsSurveyReadable', [org_app_logic])]
        ])]
    rights['results'] = [('checkIsHostForProgramInScope', program_logic)]
    rights['review'] = [('checkIsHostForProgramInScope', program_logic),
                        ('checkCanReviewOrgAppRecord', [org_app_logic])]
    rights['review_overview'] = [('checkIsHostForProgramInScope',
                                  program_logic)]
    rights['take'] = [
        ('checkOrgAppRecordIfPresent', org_app_logic),
        ('checkIsActivePeriod',
            ['org_signup', 'scope_path', program_logic]),
        ('checkIsSurveyTakeable', org_app_logic),
        ('checkIsNotStudentForProgramInScope', [program_logic, student_logic])]

    new_params = {}
    new_params['logic'] = org_app_logic
    new_params['rights'] = rights

    new_params['scope_view'] = program_view

    new_params['name'] = "GHOP Org Application Survey"
    new_params['url_name'] = 'ghop/org_app'
    new_params['module_package'] = 'soc.modules.ghop.views.models'
    new_params['module_name'] = 'org_app_survey'

    new_params['bulk_process_task'] = org_app_survey_tasks.bulk_process

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)


view = View()

create = decorators.view(view.create)
edit = decorators.view(view.edit)
delete = decorators.view(view.delete)
list = decorators.view(view.list)
list_self = decorators.view(view.listSelf)
public = decorators.view(view.public)
record = decorators.view(view.viewRecord)
results = decorators.view(view.viewResults)
review = decorators.view(view.review)
review_overview = decorators.view(view.reviewOverview)
take = decorators.view(view.take)
