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

"""Version update Tasks runner.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import http
from django.template import loader
from django.utils.translation import ugettext

from soc.tasks.helper import error_handler
from soc.tasks.updates import student_school_type
from soc.views.helper import responses


def getDjangoURLPatterns():
  """Returns the URL patterns for the views in this module.
  """

  patterns = [
      (r'tasks/update/start$', 'soc.tasks.updates.start_update.startTasks'),
      (r'tasks/update/start/([0-9_a-z]+)$',
       'soc.tasks.updates.start_update.start_task'),
      (r'tasks/update/run/([0-9_a-z]+)$',
       'soc.tasks.updates.start_update.run_task')]

  return patterns


def startTasks(request):
  """Presents a view that allows the user to start update tasks.
  """

  template = 'soc/tasks/start_update.html'

  context = responses.getUniversalContext(request)

  options = task_runner.getOptions()

  sorted_keys = []
  for key, option in options.iteritems():
    option['name'] = key
    sorted_keys.append(
        (option['from_version'], option['in_version_order'], key))

  # sort the keys
  sorted_keys.sort()

  # store only the true option
  sorted_options = []

  for key_tuple in sorted_keys:
    option_key = key_tuple[2]
    sorted_options.append(options[option_key])

  context.update(
      page_name='Update Tasks starter',
      options=sorted_options,
      )

  content = loader.render_to_string(template, dictionary=context)
  return http.HttpResponse(content)


class TaskRunner(object):
  """Runs one of the supported tasks.
  """

  STUDENT_SCHOOL_TYPE = {
      'from_version': '0-5-20090914',
      'in_version_order': 1,
      'description': ugettext(
          'Updates due to changes in the Student model. Sets all school_type '
          'entries to University since that was the first type of Student that '
          'was supported.'),
      'starter': student_school_type.startSchoolTypeUpdate,
      'runner': student_school_type.runSchoolTypeUpdate,
      }


  def __init__(self):
    """Initializes the TaskRunner.
    """

    self.options = {
        'student_school_type': self.STUDENT_SCHOOL_TYPE,
    }

  def getOptions(self):
    """Returns the supported options.
    """

    return self.options

  def startTask(self, request, option_name):
    """Starts the specified Task for the given option.
    """

    context = responses.getUniversalContext(request)
    context['page_name'] = 'Start Update Task'

    option = self.options.get(option_name)
    if not option:
      template = 'soc/error.html'
      context['message'] = 'Uknown option "%s".' % option_name
    else:
      template = 'soc/tasks/run_update.html'
      context['option'] = option
      context['success'] = option['starter'](request,
                                             self._getRunUpdateURL(option_name))

    content = loader.render_to_string(template, dictionary=context)
    return http.HttpResponse(content)

  def _getRunUpdateURL(self, option):
    """Returns the URL to run a specific update.

    Args:
      option: the update option for which the URL should returned
    """
    return '/tasks/update/run/%s' % option

  def runTask(self, request, option_name, **kwargs):
    """Runs the specified Task for the given option.
    """

    option = self.options.get(option_name)

    if not option:
      error_handler('Uknown Updater option "%s".' % option_name)
    else:
      return option['runner'](request, **kwargs)


task_runner = TaskRunner()
start_task = task_runner.startTask
run_task = task_runner.runTask
