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

"""Tasks related to OrgAppSurveys.
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.tasks import responses
from soc.tasks.helper import error_handler


class BulkProcessing(object):
  """Class which controls the Task to bulk process OrgAppSurveysRecords.
  """

  def __init__(self, program_logic, org_app_logic, path):
    """Construct the BulkProcessing object.

    Args:
      program_logic: Program Logic instance
      org_app_logic: OrgAppSurveyLogic instance
      path: the URL to use for this 
    """

    self.program_logic = program_logic
    self.org_app_logic = org_app_logic
    self.path = path

  def start(self, program_entity):
    """Starts the Task to bulk process OrgAppSurveyRecords.
    """
    context = {'program_key': program_entity.key().id_or_name()}
    return responses.startTask(self.path, context=context)

  def run(self, request, *args, **kwargs):
    """Processes all OrgAppSurveyRecords that are in the pre-accept or
    pre-reject state for the given program.

    Expects the following to be present in the POST dict:
      program_key: Specifies the program key name for which to loop over all
          the OrgAppSurveyRecords for.

    Args:
      request: Django Request object
    """

    # set default batch size
    batch_size = 10

    # retrieve the program_key from POST data
    post_dict = request.POST
    program_key = post_dict.get('program_key')

    if not program_key:
      return error_handler.logErrorAndReturnOK(
          'Not all required fields are present in POST dict %s' % post_dict)

    program_entity = self.program_logic.getFromKeyName(program_key)

    if not program_entity:
      return error_handler.logErrorAndReturnOK(
          'No Program exists with keyname: %s' % program_key)

    org_app = self.org_app_logic.getForProgram(program_entity)

    record_logic = self.org_app_logic.getRecordLogic()
    fields = {'survey': org_app,
              'status': ['pre-accepted', 'pre-rejected']}
    org_app_records = record_logic.getForFields(fields, limit=batch_size)

    for org_app_record in org_app_records:
      record_logic.processRecord(org_app_record)

    if len(org_app_records) == batch_size:
        # start a new task because we might not have exhausted all OrgAppRecords
        context = post_dict.copy()
        responses.startTask(self.path, context=context)

    # return a 200 response that everything has been completed
    return responses.terminateTask()
