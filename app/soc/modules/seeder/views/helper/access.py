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
    '"Felix Kerekes" <sttwister@gmail.com>',
  ]


from soc.views.helper import access


# pylint: disable=R0904
class DataSeederChecker(access.Checker):
  """See soc.views.helper.access.Checker.
  """

  @access.denySidebar
  @access.allowDeveloper
  def checkCanManageDataSeeder(self, django_args):
    """Checks if the user can manage data seeding operations

    Args:
      django_args: a dictionary with django's arguments
    """

    self.checkIsDeveloper(django_args)