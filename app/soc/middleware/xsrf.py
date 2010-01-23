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

"""Middleware to protect against cross site request forgeries.

This middleware will automatically add a hidden form input containing the XSRF
token to any <form> sent to the browser, and any (non-AppEngine) POST requests
will be rejected if the provided token is invalid.
"""

__authors__ = [
  '"Doug Coker" <dcoker@google.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


import itertools
import os
import re

from django import http
from django.utils.safestring import mark_safe

from soc.logic.helper import xsrfutil
from soc.logic.models.site import logic as site_logic
from soc.views.helper import responses


_HTML_TYPES = ('text/html', 'application/xhtml+xml')
_POST_FORM_RE = \
  re.compile(r'(<form\W[^>]*\bmethod\s*=\s*(\'|"|)POST(\'|"|)\b[^>]*>)',
    re.IGNORECASE)

class XsrfMiddleware(object):
  """Middleware for preventing cross-site request forgery attacks."""

  def _getSecretKey(self, request):
    """Gets the XSRF secret key from the request context."""
    return site_logic.getXsrfSecretKey(site_logic.getSingleton())

  def process_request(self, request):
    """Requires a valid XSRF token on POST requests."""
    # we only care about POST
    if request.method != 'POST':
      return None

    # HTTPRequests from AppEngine do not have to have a key
    app_engine_request = ('HTTP_X_APPENGINE_CRON' in os.environ) or \
        ('HTTP_X_APPENGINE_QUEUENAME' in os.environ)

    if app_engine_request:
      return None

    post_token = request.POST.get('xsrf_token')

    if not post_token:
      return http.HttpResponse('Missing XSRF token.', status=403)

    if not xsrfutil.isTokenValid(self._getSecretKey(request), post_token):
      return http.HttpResponse('Invalid XSRF token.', status=403)

    return None

  def process_response(self, request, response):
    """Alters HTML responses containing <form> tags to embed the XSRF token."""
    if response['Content-Type'].split(';')[0] in _HTML_TYPES:
      xsrf_token = \
        xsrfutil.getGeneratedTokenForCurrentUser(self._getSecretKey(request))

      # there may be multiple forms per page, but we only id= one of them
      idattributes = itertools.chain(("id='xsrftoken'",), itertools.repeat(''))

      # invoked on every matching <form> tag
      def add_xsrf_field(match):
        """Returns the matched <form> tag plus the added <input> element"""
        return mark_safe(match.group() + ("<div style='display:none;'>" +
            "<input type='hidden' " + idattributes.next() +
            " name='xsrf_token' value='" + xsrf_token +
            "' /></div>"))

      response.content, n = _POST_FORM_RE.subn(add_xsrf_field, response.content)
      if n > 0:
        # content has changed, so ETag would be invalid
        del response['ETag']

    return response
