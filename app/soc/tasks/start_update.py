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

"""Version update Tasks starters.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import http
from django.template import loader
from django.utils.translation import ugettext

from soc.views.helper import responses


def getDjangoURLPatterns():
  """Returns the URL patterns for the views in this module.
  """

  patterns = [(r'tasks/update/start$', 'soc.tasks.start_update.startTasks'),
              (r'tasks/update/([a-z]+)$', 'soc.tasks.start_update.runner')]

  return patterns


def startTasks(request):
  """Presents a view that allows the user to start update tasks.
  """

  template = 'soc/tasks/start_update.html'

  context = responses.getUniversalContext(request)

  options = runner.getOptions()

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
  """Runs one of the supported task starters.
  """

  def __init__(self):
    """Initializes the TaskRunner.
    """

    self.options = {
        'program': self.programConversion(),
        'student': self.studentConversion(),
        'organization': self.orgConversion(),
    }

  def getOptions(self):
    """Returns the supported options.
    """

    return self.options

  def __call__(self, request, option):
    """Starts the specified task.
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
      context['success'] = option['updater'](request)

    content = loader.render_to_string(template, dictionary=context)
    return http.HttpResponse(content)

  def programConversion(self):
    """
    """

    description = ugettext('This converts the Program models to contain X,Y,Z. '
                           'Note that this conversion will only work after Q')

    # TODO(ljvderijk): implement this
    updater = lambda x:False

    conversion_information = {'from_version': 'V-1',
                              'in_version_order': 2,
                              'description': description,
                              'updater': updater}

    return conversion_information

  def studentConversion(self):
    """
    """

    description = ugettext('This converts the Student models to contain X,Y,Z.')

    # TODO(ljvderijk): implement this
    updater = lambda x:False

    conversion_information = {'from_version': 'V-1',
                              'in_version_order': 1,
                              'description': description,
                              'updater': updater}

    return conversion_information

  def orgConversion(self):
    """
    """

    description = ugettext('This converts the Organization models to contain X,Y,Z.')

    # TODO(ljvderijk): implement this
    updater = lambda x:False

    conversion_information = {'from_version': 'V-2',
                              'in_version_order': 1,
                              'description': description,
                              'updater': updater}

    return conversion_information

runner = TaskRunner()
