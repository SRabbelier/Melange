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
from soc.views.helper import responses


def getDjangoURLPatterns():
  """Returns the URL patterns for the views in this module.
  """

  patterns = [
      (r'tasks/update/start$', 'soc.tasks.updates.start_update.startTasks'),
      (r'tasks/update/start/([a-z]+)$',
       'soc.tasks.updates.start_update.start_task'),
      (r'tasks/update/run/([a-z]+)$',
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

  ORG_CONVERSION = {
      'from_version': 'V-2',
      'in_version_order': 1,
      'description': ugettext('This converts the Organization models to contain X,Y,Z.'),
      'starter': lambda x:False,
      'runner': lambda x,**kwargs:http.HttpResponse('TEST OK'),
      }


  def __init__(self):
    """Initializes the TaskRunner.
    """

    self.options = {
        'organization': self.ORG_CONVERSION,
    }

  def getOptions(self):
    """Returns the supported options.
    """

    return self.options

  def startTask(self, request, option):
    """Starts the specified Task for the given option.
    """

    context = responses.getUniversalContext(request)
    context['page_name'] = 'Start Update Task'

    option = self.options.get(option)
    if not option:
      template = 'soc/error.html'
      context['message'] = 'Uknown option "%s".' % option
    else:
      template = 'soc/tasks/run_update.html'
      context['option'] = option
      context['success'] = option['starter'](request)

    content = loader.render_to_string(template, dictionary=context)
    return http.HttpResponse(content)

  def runTask(self, request, option, **kwargs):
    """Runs the specified Task for the given option.
    """

    option = self.options.get(option)

    if not option:
      error_handler('Uknown Updater option "%s".' % option)
    else:
      return option['runner'](request, **kwargs)


task_runner = TaskRunner()
start_task = task_runner.startTask
run_task = task_runner.runTask
