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

"""A Django template tag library containing StudentProposal helpers.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from google.appengine.ext import db

from django import template

from soc.modules.gsoc.logic.models.org_admin import logic as org_admin_logic

register = template.Library()


@register.inclusion_tag(
    'modules/gsoc/templatetags/_as_proposal_duplicates.html',
    takes_context=True)
def as_proposal_duplicates(context, proposal_duplicate):
  """Returns a HTML representation of a proposal duplicates.
  """

  context['student'] =  proposal_duplicate.student
  orgs = db.get(proposal_duplicate.orgs)
  proposals = db.get(proposal_duplicate.duplicates)

  orgs_details = {}
  for org in orgs:
    orgs_details[org.key().id_or_name()] = {
        'name': org.name
        }
    fields = {'scope': org,
              'status': 'active'}
    org_admins = org_admin_logic.getForFields(fields)

    orgs_details[org.key().id_or_name()]['admins'] = []
    for org_admin in org_admins:
      orgs_details[org.key().id_or_name()]['admins'].append({
          'name': org_admin.name(),
          'email': org_admin.email
          })

    orgs_details[org.key().id_or_name()]['proposals'] = []
    for proposal in proposals:
      if proposal.org.key() == org.key():
        orgs_details[org.key().id_or_name()]['proposals'].append({
            'key': proposal.key().id_or_name(),
            'title': proposal.title,
            })

  context['orgs'] = orgs_details
  return context
