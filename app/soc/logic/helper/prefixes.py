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

  if getattr(entity, 'scope', None):
    return entity.scope

  entity.scope = getScopeForPrefix(entity.prefix, entity.scope_path)
  entity.put()


def getScopeForPrefix(prefix, key_name):
  """Gets the scope for the given prefix and key_name.

  params:
      prefix: the prefix of the document
      key_name: the key_name of the document
  """
  import soc.models.program
  import soc.models.organization
  import soc.models.user
  import soc.models.site

  import soc.modules.gsoc.models.organization
  import soc.modules.gsoc.models.program

  import soc.modules.gci.models.organization
  import soc.modules.gci.models.program

  # use prefix to generate dict key
  scope_types = {
      "gsoc_program": soc.modules.gsoc.models.program.GSoCProgram,
      "gci_program": soc.modules.gci.models.program.GCIProgram,
      "program": soc.models.program.Program,
      "gsoc_org": soc.modules.gsoc.models.organization.GSoCOrganization,
      "gci_org": soc.modules.gci.models.organization.GCIOrganization,
      "org": soc.models.organization.Organization,
      "user": soc.models.user.User,
      "site": soc.models.site.Site,
  }

  # determine the type of the scope
  scope_type = scope_types.get(prefix)

  if not scope_type:
    # no matching scope type found
    raise AttributeError('No Matching Scope type found for %s' \
        % entity.prefix)

  return scope_type.get_by_key_name(key_name)
