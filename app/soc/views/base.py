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

"""Module containing the boiler plate required to construct views. This
module is largely based on appengine's webapp framework's code.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Sverre Rabbelier" <sverre@rabbelier.nl>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>'
  ]

import os

from django import http
from django.utils import simplejson
from django.template import loader

from soc.logic import system
from soc.logic.exceptions import LoginRequest
from soc.logic.exceptions import RedirectRequest
from soc.logic.exceptions import AccessViolation
from soc.logic.exceptions import Error
from soc.logic.helper import xsrfutil
from soc.logic.models.site import logic as site
from soc.views.helper.request_data import RequestData


class Response(http.HttpResponse):
  """Response class that wraps the Django's HttpResponse class but
  with message for every possible HTTP response code.
  """

  DEFAULT_CONTENT_TYPE = 'text/html'

  HTTP_STATUS_MESSAGES = {
      100: 'Continue',
      101: 'Switching Protocols',
      200: 'OK',
      201: 'Created',
      202: 'Accepted',
      203: 'Non-Authoritative Information',
      204: 'No Content',
      205: 'Reset Content',
      206: 'Partial Content',
      300: 'Multiple Choices',
      301: 'Moved Permanently',
      302: 'Moved Temporarily',
      303: 'See Other',
      304: 'Not Modified',
      305: 'Use Proxy',
      306: 'Unused',
      307: 'Temporary Redirect',
      400: 'Bad Request',
      401: 'Unauthorized',
      402: 'Payment Required',
      403: 'Forbidden',
      404: 'Not Found',
      405: 'Method Not Allowed',
      406: 'Not Acceptable',
      407: 'Proxy Authentication Required',
      408: 'Request Time-out',
      409: 'Conflict',
      410: 'Gone',
      411: 'Length Required',
      412: 'Precondition Failed',
      413: 'Request Entity Too Large',
      414: 'Request-URI Too Large',
      415: 'Unsupported Media Type',
      416: 'Requested Range Not Satisfiable',
      417: 'Expectation Failed',
      500: 'Internal Server Error',
      501: 'Not Implemented',
      502: 'Bad Gateway',
      503: 'Service Unavailable',
      504: 'Gateway Time-out',
      505: 'HTTP Version not supported'
      }

  def __init__(self, content='', mimetype=None, status=200,
               content_type=DEFAULT_CONTENT_TYPE):
    """Default constructor for an empty 200 response.
    """
    super(Response, self).__init__(content, mimetype,
                                   status, content_type)

  def set_status(self, status, message=None):
    """Sets the HTTP status and message for this response.

    Args:
      status: HTTP status code
      message: the HTTP status string to use

    If no status string is given, we use the default from the HTTP/1.1
    specification defined in the dictionary HTTP_STATUS_MESSAGE.
    """
    if not message:
      message = self.HTTP_STATUS_MESSAGES.get(status, '')

    self.status_code = status
    self.content = message


class RequestHandler(object):
  """Base class managing HTTP Requests.
  """

  def context(self):
    return {}

  def get(self):
    """Handler for HTTP GET request.

    Default implementation calls context and passes it to render to
    construct the page.
    """
    context = self.context()
    self.render(context)

  def json(self):
    """Handler for HTTP GET request with a 'fmt=json' parameter.
    """

    if not self.request.GET.get('plain'):
      self.response['Content-Type'] = 'application/json'

    # if the browser supports HTTP/1.1
    # post-check and pre-check and no-store for IE7
    self.response['Cache-Control'] = 'no-store, no-cache, must-revalidate, ' \
                                     'post-check=0, pre-check=0' # HTTP/1.1, IE7
    self.response['Pragma'] = 'no-cache'

    context = self.jsonContext()

    if self.request.GET.get('marker'):
      # allow the django test framework to capture the context dictionary
      loader.render_to_string('json_marker.html', dictionary=context)

    data = simplejson.dumps(context)
    self.response.write(data)

  def jsonContext(self):
    """Defines the JSON object to be dumped and returned on a HTTP GET request
    with 'fmt=json' parameter.
    """
    return {
        'error': "json() method not implemented",
    }

  def post(self):
    """Handler for HTTP POST request.
    """
    self.error(405)

  def head(self):
    """Handler for HTTP HEAD request.
    """
    self.error(405)

  def options(self):
    """Handler for HTTP OPTIONS request.
    """
    self.error(405)

  def put(self):
    """Handler for HTTP PUT request.
    """
    self.error(405)

  def delete(self):
    """Handler for HTTP DELETE request.
    """
    self.error(405)

  def trace(self):
    """Handler for HTTP TRACE request.
    """
    self.error(405)

  def error(self, status, message=None):
    """Sets the error response code and the message when the HTTP
    Request should get an error response.

    Args:
      status: the HTTP status error code
      message: the message to set, uses default if None
    """
    self.response.set_status(status, message=message)

  def djangoURLPatterns(self):
    """Returns a list of Django URL pattern tuples.
    """
    patterns = []
    return patterns

  def checkAccess(self):
    """Raise an exception if the user doesn't have access to the
    requested URL.
    """
    self.error(401, "checkAccess in base RequestHandler has not been changed "
               "to grant access")

  def render(self, context):
    """Renders the page using the specified context.

    The page is rendered using the template specified in self.templatePath()
    and is written to the response object.

    The context object is extended with the following values:
      app_version: the current version of the application, used e.g. in URL
                   patterns to avoid JS caching issues.
      is_local: Whether the application is running locally.
      posted: Whether render is called after a POST is request.
      xsrf_token: The xsrf token for the current user.

    Args:
      context: the context that should be used
    """

    context['app_version'] = os.environ.get('CURRENT_VERSION_ID', '').split('.')[0]
    context['is_local'] = system.isLocal()
    context['posted'] = self.posted
    xsrf_secret_key = site.getXsrfSecretKey(site.getSingleton())
    context['xsrf_token'] = xsrfutil.getGeneratedTokenForCurrentUser(xsrf_secret_key)

    rendered = loader.render_to_string(self.templatePath(), dictionary=context)
    self.response.write(rendered)

  def templatePath(self):
    """Returns the path to the template that should be used in render().

    Subclasses should override this method.
    """
    raise NotImplementedError()

  def accessViolation(self, status, message):
    """Default access violation handler.
    """
    self.error(status, message)

  def _dispatch(self):
    """Dispatches the HTTP request to its respective handler method.
    """
    if self.request.method == 'GET':
      if self.request.GET.get('fmt') == 'json':
        self.json()
      else:
        self.get()
    elif self.request.method == 'POST':
      self.post()
    elif self.request.method == 'HEAD':
      self.head()
    elif self.request.method == 'OPTIONS':
      self.options()
    elif self.request.method == 'PUT':
      self.put()
    elif self.request.method == 'DELETE':
      self.delete()
    elif self.request.method == 'TRACE':
      self.trace()
    else:
      self.error(501)

  def init(self, request, args, kwargs):
    """Initializes the RequestHandler.

    Sets the data and check fields.
    """
    self.data = None
    self.check = None

  def __call__(self, request, *args, **kwargs):
    """Returns the response object for the requested URL.

    In detail, this method does the following:
    1. Initialize request, arguments and keyword arguments as instance variables
    2. Construct the response object.
    3. Calls the access check.
    4. Delegates dispatching to the handler to the _dispatch method.
    5. Returns the response.
    """
    self.request = request
    self.args = args
    self.kwargs = kwargs

    self.response = Response()

    self.posted = request.POST or 'validated' in request.GET

    try:
      self.init(request, args, kwargs)
      self.checkAccess()
      self._dispatch()
    except LoginRequest, e:
      full_path = request.get_full_path().encode('utf-8')
      self.redirect.login().to()
    except RedirectRequest, e:
      self.redirect.toUrl(e.url)
    except AccessViolation, e:
      self.accessViolation(e.status, e.args[0])
    except Error, e:
      self.error(e.status, message=e.args[0])

    return self.response


class SiteRequestHandler(RequestHandler):
  """Customization required by global site pages to handle HTTP requests.
  """

  def init(self, request, args, kwargs):
    self.data = RequestData()
    self.data.populate(None, request, args, kwargs)

  def redirect(self, url):
    self.response = http.HttpResponseRedirect(url)
