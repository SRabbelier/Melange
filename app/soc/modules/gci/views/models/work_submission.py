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

"""Views for GCI Work Submission.
"""

__authors__ = [
    '"Madhusudan.C.S" <madhusudancs@gmail.com>'
  ]


import urllib

from google.appengine.ext import blobstore

from django import http

from soc.logic import dicts
from soc.views.helper import decorators
from soc.views.models import base

from soc.modules.gci.views.helper import access as gci_access
from soc.views.helper import blobstore as bs_helper

import soc.modules.gci.logic.models.work_submission


class View(base.View):
  """View methods for the Task Subscriptions.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the work_submission.

    Params:
      params: a dict with params for this View
    """

    rights = gci_access.GCIChecker(params)
    rights['any_access'] = ['allow']
    rights['download_blob'] = ['allow']

    new_params = {}
    new_params['logic'] = soc.modules.gci.logic.models.work_submission.logic
    new_params['rights'] = rights

    new_params['name'] = "Work Submission"
    new_params['module_name'] = "work_submission"

    new_params['module_package'] = 'soc.modules.gci.views.models'
    new_params['url_name'] = 'gci/work_submission'

    patterns = []
    patterns += [
        (r'^%(url_name)s/(?P<access_type>download_blob)$',
        '%(module_package)s.%(module_name)s.download_blob',
        'Download the blob'),
        ]

    new_params['extra_django_patterns'] = patterns

    params = dicts.merge(params, new_params, sub_merge=True)

    super(View, self).__init__(params=params)

  @decorators.merge_params
  @decorators.check_access
  def downloadBlob(self, request, access_type, page_name=None,
                   params=None, **kwargs):
    """View that helps to download the blob.

    Args:
      request: the standard Django HTTP request object
    """

    blob_get_key = request.GET.get('key')

    if not blob_get_key:
      return http.HttpResponse('No blob key present')

    blob_key = str(urllib.unquote(blob_get_key))
    blob = blobstore.BlobInfo.get(blob_key)

    try:
      return bs_helper.send_blob(request, blob, save_as=True)
    except ValueError, error:
      return http.HttpResponse(str(error))


view = View()

download_blob = decorators.view(view.downloadBlob)
