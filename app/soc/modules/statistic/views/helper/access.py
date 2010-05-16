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

"""Access control helper.

See soc.views.helper.access module.
"""

__authors__ = [
    '"Daniel Hans <daniel.m.hans@gmail.com>',
  ]


from soc.views.helper import access


class StatisticChecker(access.Checker):
  """See soc.views.helper.access.Checker.
  """

  @access.denySidebar
  @access.allowDeveloper
  def checkCanManageStatistic(self, django_args, access_types, program_logic):
    """Checks if the user can see a public page for a specified statistic.

    Args:
      django_args: a dictionary with django's arguments
      access_types: a list with stat access types that are sufficient
      program_logic: program logic instance
    """

    self.checkIsHost(django_args)
