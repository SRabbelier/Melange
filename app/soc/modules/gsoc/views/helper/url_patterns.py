#!/usr/bin/env python2.5
#
# Copyright 2011 the Melange authors.
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

"""Module for constructing GSoC related URL patterns
"""

__authors__ = [
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.models import linkable


def namedLinkIdPattern(names):
  """Returns a link ID pattern consisting of named parts.

  The returned pattern does not start or end with a /, the parts are however
  concatenated with a /.

  Args:
    names: The names that should be given to the different parts.
  """
  named_patterns = []
  for name in names:
    named_patterns.append(r'(?P<%s>%s)' % (name, linkable.LINK_ID_PATTERN_CORE))

  return r'/'.join(named_patterns)

SPONSOR   = namedLinkIdPattern(['sponsor'])
PROGRAM   = namedLinkIdPattern(['sponsor', 'program'])
STUDENT   = namedLinkIdPattern(['sponsor', 'program', 'student'])
PROPOSAL  = namedLinkIdPattern(['sponsor', 'program', 'student', 'proposal'])
MENTOR    = namedLinkIdPattern(['sponsor', 'program', 'organization', 'mentor'])
ORG_ADMIN = namedLinkIdPattern(['sponsor', 'program', 'organization', 'org_admin'])
PROJECT   = namedLinkIdPattern(['sponsor', 'program', 'organization', 'project'])