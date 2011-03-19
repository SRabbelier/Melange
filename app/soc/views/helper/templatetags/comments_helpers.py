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

"""A Django template tag library containing Comments helpers.
"""

__authors__ = [
  '"Sverre Rabbelier" <srabbelier@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import template

from soc.logic.models import user as user_logic
from soc.views.helper import redirects


register = template.Library()


@register.inclusion_tag('soc/templatetags/_as_comments.html',
                        takes_context=True)
def as_comments(context, work):
  """Returns a HTML representation of a work's comments.
  """

  context['comments'] =  work.comments
  return context

@register.inclusion_tag('soc/templatetags/_as_comment.html',
                        takes_context=True)
def as_comment(context, comment):
  """Returns a HTML representation of a comment.
  """

  edit_link = ''
  current_user = user_logic.logic.getCurrentUser()
  # pylint: disable=E1103
  if current_user and comment.author.key() == current_user.key():
    params = {'url_name': context['comment_on_url_name']}
    edit_link = redirects.getEditRedirect(comment, params)

  context.update({
      'author': comment.author.name,
      'content': comment.content,
      'created': comment.created,
      'edit_link': edit_link,
      'modified_on': comment.modified,
      'modified_by': comment.modified_by.name if comment.modified_by else '',
      'comment_class': "public" if comment.is_public else "private",
      })

  return context

@register.inclusion_tag('soc/templatetags/_as_review.html',
                        takes_context=True)
def as_review(context, review):
  """Returns a HTML representation of a review.
  """

  # TODO(ljvderijk) once review editing is allowed redo this

  context.update({
      'author': review.author_name(),
      'content': review.content,
      'created': review.created,
      'score': review.score,
      'is_public': review.is_public,
      'comment_class': "public" if review.is_public else "private",
      })

  return context

@register.inclusion_tag('soc/templatetags/_as_student_proposal_review.html',
                        takes_context=True)
def as_student_proposal_review(context, review, student):
  """Returns a HTML representation of a student proposal review.
  """

  # TODO(ljvderijk) once review editing is allowed redo this

  context.update({
      'author': review.author_name(),
      'content': review.content,
      'created': review.created,
      'score': review.score,
      'is_public': review.is_public,
      'from_student': review.author.key() == student.user.key()
      })

  return context
