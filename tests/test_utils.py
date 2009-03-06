#!/usr/bin/python2.5
#
# Copyright 2008 the Melange authors.
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
"""Common testing utilities.
"""

__authors__ = [
  '"Augie Fackler" <durin42@gmail.com>',
  ]

class MockRequest(object):
  """Shared dummy request object to mock common aspects of a request.
  """
  def __init__(self, path=None):
    self.REQUEST = self.GET = self.POST = {}
    self.path = path
