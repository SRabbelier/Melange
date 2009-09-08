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

"""Tasks conversion starter.
"""

__authors__ = [
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from django import http
from django.template import loader


def getDjangoURLPatterns():
  """Returns the URL patterns for the view in this module.
  """


  patterns = [(r'tasks/convert/([a-z]+)$', 'soc.tasks.convert.runner')]

  return patterns


class TaskRunner(object):
  """Runs one of the supported task starters.
  """

  def __init__(self):
    """Initializes the TaskRunner.
    """

    self.options = {
        'program': self.startProgramConversion,
        'organization': self.startOrganizationConversion,
        'student': self.startStudentConversion,
    }

  def getOptions(self):
    """Returns the supported option types.
    """

    return self.options.keys()

  def __call__(self, request, option):
    """Starts the specified task.
    """

    context = {
        'page_name': 'Start conversion job',
    }

    fun = self.options.get(option)
    if not fun:
      template = 'soc/error.html'
      context['message'] = 'Uknown option "%s".' % option
    else:
      template = 'soc/tasks/convert.html'
      context['option'] = option
      context['success'] = fun(request)

    content = loader.render_to_string(template, dictionary=context)
    return http.HttpResponse(content)

  def startProgramConversion(self, request):
    """
    """

    # TODO(ljvderijk): implement this

    return False

  def startOrganizationConversion(self, request):
    """
    """

    # TODO(ljvderijk): implement this

    return False

  def startStudentConversion(self, request):
    """
    """

    # TODO(ljvderijk): implement this

    return False


runner = TaskRunner()
