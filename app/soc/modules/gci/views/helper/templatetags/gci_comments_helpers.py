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

"""A Django template tag library containing GCI Task 
specific Comments helpers.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


from google.appengine.ext import blobstore

from django import template

from soc.views.helper import redirects


register = template.Library()


@register.inclusion_tag(
    'modules/gci/templatetags/_as_gci_task_comments.html',
    takes_context=True)
def as_gci_task_comment(context, comment):
  """Returns a HTML representation of a GCI task's comments.
  """

  context['comment'] =  comment
  context['comment_id'] =  comment.key().id_or_name()
  return context


@register.inclusion_tag(
    'modules/gci/templatetags/_as_gci_task_ws.html',
    takes_context=True)
def as_gci_task_ws(context, comment):
  """Returns a HTML representation of a GCI task's work submissions.
  """

  context['ws'] =  comment
  context['ws_id'] = comment.key().id_or_name()

  if comment.upload_of_work:
    blob_key = comment.upload_of_work.key()

    blob = blobstore.BlobInfo.get(blob_key)
    if blob:
      context['ws_file_blob_key'] = blob_key
      context['ws_file_name'] = blob.filename
      context['ws_file_size'] = blob.size
      context['ws_file_download_url'] = \
          redirects.getDownloadBlobRedirectWithGet(
              blob, {'url_name': 'gci/work_submission'})

  return context
