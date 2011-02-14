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
  ]


from django.http import HttpResponse


class Response(HttpResponse):
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
    """Constructor to convert the status code to the relevant message.
    """

    if not content:
      content = self.HTTP_STATUS_MESSAGE.get(status, '')

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
      self.content = self.HTTP_STATUS_MESSAGE.get(status, '')


class RequestHandler(object):
  """Base class managing HTTP Requests.
  """

  def __init__(self, request, response):
    """Construct the request and response for a HTTP Request.
    """
    self.request= request
    self.response = response

  def get(self, request, *args, **kwargs):
    """Handler for HTTP GET request.
    """
    self.error(405)

  def post(self, request, *args, **kwargs):
    """Handler for HTTP POST request.
    """
    self.error(405)

  def head(self, request, *args, **kwargs):
    """Handler for HTTP HEAD request.
    """
    self.error(405)

  def options(self, request, *args, **kwargs):
    """Handler for HTTP OPTIONS request.
    """
    self.error(405)

  def put(self, request, *args, **kwargs):
    """Handler for HTTP PUT request.
    """
    self.error(405)

  def delete(self, request, *args, **kwargs):
    """Handler for HTTP DELETE request.
    """
    self.error(405)

  def trace(self, request, *args, **kwargs):
    """Handler for HTTP TRACE request.
    """
    self.error(405)

  def error(self, status):
    """Sets the error response code and the message when the HTTP
    Request should get an error response.

    Args:
      status: the HTTP status error code
    """
    self.response.set_status(status)

  def getDjangoURLPatterns(self):
    """Returns a list of Django URL pattern tuples.
    """

    patterns = []
    return patterns

  def __call__(self, request, *args, **kwargs):
    """Dispatches the relevant handler as specified in the request object.
    """

    if request.method == 'GET':
      self.get(request, *args, **kwargs)
    elif request.method == 'POST':
      self.post(request, *args, **kwargs)
    elif request.method == 'HEAD':
      self.head(request, *args, **kwargs)
    elif request.method == 'OPTIONS':
      self.options(request, *args, **kwargs)
    elif request.method == 'PUT':
      self.put(request, *args, **kwargs)
    elif request.method == 'DELETE':
      self.delete(request, *args, **kwargs)
    elif request.method == 'TRACE':
      self.trace(request, *args, **kwargs)
    else:
      self.error(501)

    return self.response
