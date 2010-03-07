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

"""Prefix helper module for models with document prefixes.
"""

__authors__ = [
  '"James Levy" <jamesalexanderlevy@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


def getOrSetScope(entity):
  """Gets or sets scope for the given entity.

  params:
    entity = Entity which uses document prefix.
  """

  import soc.models.program
  import soc.models.organization
  import soc.models.user
  import soc.models.site

  import soc.modules.gsoc.models.program
  import soc.modules.ghop.models.program

  if getattr(entity, 'scope', None):
    return entity.scope

  # use prefix to generate dict key
  scope_types = {
      "gsoc_program": soc.modules.gsoc.models.program.GSoCProgram,
      "ghop_program": soc.modules.ghop.models.program.GHOPProgram,
      "program": soc.models.program.Program,
      "org": soc.models.organization.Organization,
      "user": soc.models.user.User,
      "site": soc.models.site.Site}

  # determine the type of the scope
  scope_type = scope_types.get(entity.prefix)

  if not scope_type:
    # no matching scope type found
    raise AttributeError('No Matching Scope type found for %s' \
        % entity.prefix)

  # set the scope and update the entity
  entity.scope = scope_type.get_by_key_name(entity.scope_path)
  entity.put()

  # return the scope
  return entity.scope
