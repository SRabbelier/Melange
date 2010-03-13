#!/usr/bin/python2.5
#
# Copyright 2010 the Melange authors.
# Copyright 2009 Jake McGuire.
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

"""Middleware to start the profiler and store results.
"""

__authors__ = [
  '"Jake McGuire" <jaekmcguire@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


import soc.profiling.profiler


class ProfileMiddleware(object):
  """Middleware class to handle the profiler.
  """

  def __init__(self):
    """Initializes with no profiler set.
    """

    self.profiler = None

  def process_request(self, request):
    """Called when a request is made.

    See the Django middleware documentation for an explanation of
    the method signature.
    """

    self.profiler = soc.profiling.profiler.get_global_profiler()

  def process_view(self, request, callback, callback_args, callback_kwargs):
    """Called when a request is made.

    See the Django middleware documentation for an explanation of
    the method signature.
    """

    if self.profiler.is_profiling:
      return self.profiler.runcall(callback, request, *callback_args, **callback_kwargs)
