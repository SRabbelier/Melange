#!/usr/bin/env python2.5
#
# Copyright 2009 the Melange authors.
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

"""A Django template tag library containing GHOP Task 
specific Comments helpers.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from django import template


register = template.Library()


@register.inclusion_tag(
    'modules/ghop/templatetags/_as_ghop_task_comments.html',
    takes_context=True)
def as_ghop_task_comment(context, comment):
  """Returns a HTML representation of a GHOP task's comments.
  """

  context['comment'] =  comment
  context['comment_id'] =  comment.key().id_or_name()
  return context


@register.inclusion_tag(
    'modules/ghop/templatetags/_as_ghop_task_ws.html',
    takes_context=True)
def as_ghop_task_ws(context, comment):
  """Returns a HTML representation of a GHOP task's work submissions.
  """

  context['ws'] =  comment
  context['ws_id'] = comment.key().id_or_name()
  return context
