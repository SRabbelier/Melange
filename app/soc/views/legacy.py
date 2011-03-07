#!/usr/bin/env python2.5
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

"""Url registration for legacy views.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  ]


from soc.logic import system


class Legacy(object):
  """Class handling url registration for legacy views.
  """

  def djangoURLPatterns(self):
    """Returns the URL pattern for the legacy views.
    """
    patterns = [
        # TODO: replace with redirect to active program homepage
        (r'^$', 'soc.views.models.site.main_public'),
    ]

    from soc.tasks.updates import role_conversion
    from soc.modules.gsoc.views.models import timeline
    patterns += role_conversion.getDjangoURLPatterns()
    patterns += timeline.view.getDjangoURLPatterns()

    if system.isDebug():
      patterns += [
          ('^seed_db$', 'soc.models.seed_db.seed'),
          ('^clear_db$', 'soc.models.seed_db.clear'),
          ('^reseed_db$', 'soc.models.seed_db.reseed'),
      ]

    return patterns
