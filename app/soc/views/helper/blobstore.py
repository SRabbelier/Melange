#!/usr/bin/env python2.5
#
# Copyright 2008 the Melange authors.
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

"""Blobstore Django helpers.

These helpers are used to handle uploading and downloading appengine blobs.

With due credits, this is not Melange code. This was shamelessly
flicked from http://appengine-cookbook.appspot.com/recipe/blobstore-get_uploads-helper-function-for-django-request/
Credits and big thanks to to: sebastian.serrano and emi420
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  ]


import cgi
import logging
import urllib

from google.appengine.ext import blobstore

from django.http import HttpResponse

from soc.logic.exceptions import BadRequest


def get_uploads(request, field_name=None, populate_post=False):
  """Get uploads sent to this handler.

  Args:
    field_name: Only select uploads that were sent as a specific field
    populate_post: Add the non blob fields to request.POST
  Returns:
    A list of BlobInfo records corresponding to each upload
    Empty list if there are no blob-info records for field_name
  """

  results = []

  # the __uploads attribute in the request object is used
  # only to cache the file uploads so that we need not
  # have to go through the process of reading HTTP request
  # original file if it has already been read in the same request.
  if hasattr(request,'__uploads') == False:
      request.META['wsgi.input'].seek(0)
      fields = cgi.FieldStorage(request.META['wsgi.input'],
                                environ=request.META)

      request.__uploads = {}
      if populate_post:
        request.POST = {}

      for key in fields.keys():
        field = fields[key]
        if isinstance(
            field, cgi.FieldStorage) and 'blob-key' in field.type_options:
          request.__uploads.setdefault(key, []).append(
              blobstore.parse_blob_info(field))
        elif populate_post:
          request.POST[key] = field.value
  if field_name:
    try:
      results = list(request.__uploads[field_name])
    except KeyError:
      return []
  else:
    for uploads in request.__uploads.itervalues():
      results += uploads

  request.file_uploads = results

  return results


def send_blob(blob_key_or_info, content_type=None, save_as=None):
  """Send a blob-response based on a blob_key.

  Sets the correct response header for serving a blob.  If BlobInfo
  is provided and no content_type specified, will set request content type
  to BlobInfo's content type.

  Args:
    blob_key_or_info: BlobKey or BlobInfo record to serve
    content_type: Content-type to override when known
    save_as: If True, and BlobInfo record is provided, use BlobInfos
      filename to save-as.  If string is provided, use string as filename.
      If None or False, do not send as attachment.

    Raises:
      ValueError on invalid save_as parameter or blob key.
  """

  CONTENT_DISPOSITION_FORMAT = 'attachment; filename="%s"'
  if isinstance(blob_key_or_info, blobstore.BlobInfo):
    blob_key = blob_key_or_info.key()
    blob_info = blob_key_or_info
  else:
    blob_key = blob_key_or_info
    blob_info = None

  logging.debug(blob_info)
  response = HttpResponse()
  response[blobstore.BLOB_KEY_HEADER] = str(blob_key)

  if content_type:
    if isinstance(content_type, unicode):
      content_type = content_type.encode('utf-8')
    response['Content-Type'] = content_type
  else:
    del response['Content-Type']

  def send_attachment(filename):
    if isinstance(filename, unicode):
      filename = filename.encode('utf-8')
    response['Content-Disposition'] = (CONTENT_DISPOSITION_FORMAT % filename)

  if save_as:
    if isinstance(save_as, basestring):
      send_attachment(save_as)
    elif blob_info and save_as is True:
      send_attachment(blob_info.filename)
    else:
      if not blob_info:
        raise ValueError('The specified file is not found.')
      else:
        raise ValueError(
            'Unexpected value for the name in which file is '
            'expected to be downloaded')

  return response

def download_blob(blob_key_str):
  """A function which provides the boiler plate required to process
  the blob key string and calls the actual function which sends the
  blob as the HTTP Response.

  Args:
    blob_key_str: The blob key for which the blob must be retrieved
        in the normal string format
  """

  if not blob_key_str:
    raise BadRequest('No blob key present')

  blob_key = str(urllib.unquote(blob_key_str))
  blob = blobstore.BlobInfo.get(blob_key)

  try:
    return send_blob(blob, save_as=True)
  except ValueError, error:
    raise BadRequest(str(error))
