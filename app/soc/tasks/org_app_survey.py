#!/usr/bin/python2.5
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


def bulkProcess(program_logic, org_app_logic):
  """Returns a HTTPRequest handler that uses the POST data to process 
  OrgAppSurveyRecords.

  Args:
    program_logic: Program Logic instance
    org_app_logic: OrgApplication Logic instance used to find the
        OrgApplication and the records associated with it.
  """
  def wrapped(request, *args, **kwargs):
    """Processes all OrgAppSurveyRecords that are in the pre-accept or pre-reject
    state for the given program.

    Expects the following to be present in the POST dict:
      program_key: Specifies the program key name for which to loop o

    Args:
      request: Django Request object
    """

    from soc.modules.gsoc.logic.models.program import logic as program_logic
    from soc.modules.gsoc.logic.models.org_app_survey import logic as \
        org_app_logic


    # set default batch size
    batch_size = 10

    # retrieve the program_key from POST data
    post_dict = request.POST
    program_key = post_dict.get('program_key')

    if program_key:
      return error_handler.logErrorAndReturnOK(
          'Not all required fields are present in POST dict %s' % post_dict)

    program_entity = program_logic.getFromKeyName(program_key)

    if not program_entity:
      return error_handler.logErrorAndReturnOK(
          'No Program exists with keyname: %s' % program_key)

    org_app = org_app_logic.getForProgram(program)

    record_logic = org_app_logic.getRecordLogic()
    fields = {'survey': org_app,
              'status': ['pre-accepted', 'pre-rejected']}
    org_app_records = record_logic.getForFields(fields, limit=batch_size)

    for org_app_record in org_app_records:
      record_logic.processRecord(org_app_record)

    if len(org_app_records) == batch_size:
        # start a new task because we might not have exhausted all OrgAppRecords
        context = post_dict.copy()
        responses.startTask(request.path, context=context)

    # return OK
    return responses.terminateTask()
  return wrapped
