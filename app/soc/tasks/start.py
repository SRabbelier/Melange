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

from soc.tasks import convert


def getDjangoURLPatterns():
  """Returns the URL patterns for the view in this module.
  """

  patterns = [(r'tasks/start$',
               'soc.tasks.start.startTasks')]

  return patterns


def startTasks(request):
  """Presents a view that allows the user to start conversion tasks.
  """

  template = 'soc/tasks/start.html'

  context = {
      'page_name': 'Task starter',
      'options': convert.runner.getOptions(),
    }

  content = loader.render_to_string(template, dictionary=context)
  return http.HttpResponse(content)
