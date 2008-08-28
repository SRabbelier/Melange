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

"""Basic system information functions.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


import settings


def isDebug():
  """Returns True if Melange application is running in "debug mode".
  
  "Debug mode" is currently determined from settings.DEBUG but may become
  more sophisticated in the future.
  """
  return settings.DEBUG
