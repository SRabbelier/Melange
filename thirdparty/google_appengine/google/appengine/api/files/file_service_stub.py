#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""Stubs for File service."""


import base64
import cgi
import datetime
import md5
import os
import random
import string
import tempfile
import time
import urllib
import urlparse

from google.appengine.api import apiproxy_stub
from google.appengine.api import datastore
from google.appengine.api import datastore_errors
from google.appengine.api.files import file_service_pb
from google.appengine.ext import blobstore
from google.appengine.runtime import apiproxy_errors
from google.appengine.tools import dev_appserver_upload


_now_function = datetime.datetime.now


def raise_error(error_code, error_detail=''):
  """Raise application error helper method."""
  raise apiproxy_errors.ApplicationError(error_code, error_detail=error_detail)


class FileStorage:
  """Virtual file storage to be used by file api.

  Abstracts away all aspects of logical and physical file organization of the
  API.
  """

  def __init__(self, blob_storage):
    """Constructor.

    Args:
      blob_storage: An instance of
      apphosting.api.blobstore.blobstore_stub.BlobStorage to use for blob
      integration.
    """
    self.blob_keys = {}
    self.blobstore_files = set()
    self.finalized_files = set()
    self.created_files = set()
    self.data_files = {}
    self.sequence_keys = {}
    self.blob_storage = blob_storage

    self.blob_content_types = {}

  def finalize(self, filename):
    """Marks file as finalized."""
    if self.is_finalized(filename):
      raise_error(file_service_pb.FileServiceErrors.FINALIZATION_ERROR,
                  'File is already finalized')
    self.finalized_files.add(filename)

  def is_finalized(self, filename):
    """Checks if file is already finalized."""
    return filename in self.finalized_files

  def get_blob_key(self, ticket):
    """Gets blob key for blob creation ticket."""
    return self.blob_keys.get(ticket)

  def register_blob_key(self, ticket, blob_key):
    """Register blob key for a ticket."""
    self.blob_keys[ticket] = blob_key

  def has_blobstore_file(self, filename):
    """Checks if blobstore file was already created."""
    return filename in self.blobstore_files

  def add_blobstore_file(self, filename, content_type):
    """Registers a created blob store file."""
    self.blobstore_files.add(filename)
    self.blob_content_types[filename] = content_type

  def get_sequence_key(self, filename):
    """Get sequence key for a file."""
    return self.sequence_keys.get(filename, '')

  def set_sequence_key(self, filename, sequence_key):
    """Set sequence key for a file."""
    self.sequence_keys[filename] = sequence_key

  def save_blob(self, filename, blob_key):
    """Save filename temp data to a blobstore under given key."""
    f = self._get_data_file(filename)
    f.seek(0)
    self.blob_storage.StoreBlob(blob_key, f)
    f.seek(0, os.SEEK_END)
    size = f.tell()
    f.close()
    del self.data_files[filename]
    return size

  def _get_data_file(self, filename):
    """Get a temp data file for a file."""
    if not filename in self.data_files:
      f = tempfile.TemporaryFile()
      self.data_files[filename] = f
      return f
    return self.data_files[filename]

  def append(self, filename, data):
    """Append data to file."""
    self._get_data_file(filename).write(data)

  def get_content_type(self, filename):
    return self.blob_content_types[filename]

  def create(self, filename):
    self.created_files.add(filename)

  def exists(self, filename):
    return filename in self.created_files


class NewBlobstoreFile(object):
  """File object for '/blobstore/new' file."""

  def __init__(self, file_storage):
    """Constructor.

    Args:
      file_storage: An instance of FileStorage.
    """
    self.file_storage = file_storage

  def read(self, request, response):
    """Read data from file.

    Generates new /blobstore/<filename> name and registers it in the stub.

    Args:
      request: An instance of file_service_pb.ReadRequest.
      response: An instance of file_service_pb.ReadResponse.
    """
    pos = request.pos()
    max_bytes = request.max_bytes()
    request_filename = request.filename()
    request_qs = urlparse.urlparse(request_filename).query
    params = cgi.parse_qs(request_qs)

    if 'content_type' not in params:
      raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME,
                  'content_type not specified')
    content_type = params['content_type'][0]

    random_str = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(64))
    filename = '/blobstore/' + base64.urlsafe_b64encode(random_str)
    self.file_storage.add_blobstore_file(filename, content_type)
    result = filename[pos:(pos + max_bytes)]
    response.set_data(result)

  def append(self, request, response):
    """Append data to file (raises error)."""
    raise_error(file_service_pb.FileServiceErrors.WRONG_OPEN_MODE)


class GetBlobKeyFile(object):
  """File object for a /blobstore/get_blob_key file."""

  def __init__(self, filename, file_storage):
    """Constructor.

    Args:
      filename: file name as string.
      file_storage: an instance of FileStorage."""
    self.filename = filename
    self.file_storage = file_storage

    request_qs = urlparse.urlparse(filename).query
    params = cgi.parse_qs(request_qs)

    if 'ticket' not in params:
      raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME,
                  'ticket not specified')
    self.ticket = params['ticket'][0]

  def read(self, request, response):
    """Read from file."""
    assert self.filename == request.filename()
    pos = request.pos()
    max_bytes = request.max_bytes()
    result = self.file_storage.get_blob_key(self.ticket)
    if result is None:
      raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME,
                  'invalid ticket')
    result = result[pos:(pos + max_bytes)]
    response.set_data(result)


class BlobstoreFile(object):
  """File object for generic '/blobstore/' file."""

  def __init__(self, open_request, file_storage):
    """Constructor.

    Args:
      open_request: An instance of open file request.
      file_storage: An instance of FileStorage.
    """
    self.filename = open_request.filename()
    self.file_storage = file_storage
    self.blob_reader = None
    self.content_type = None
    self.mime_content_type = None

    open_mode = open_request.open_mode()
    content_type = open_request.content_type()
    create = open_request.create_options().create()
    exists = self.file_storage.exists(self.filename)

    if not self.filename.startswith('/blobstore/'):
      if not self.file_storage.has_blobstore_file(self.filename):
        raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME)
    self.ticket = self.filename[len('/blobstore/'):]

    if open_mode == file_service_pb.OpenRequest.APPEND:
      if not self.file_storage.has_blobstore_file(self.filename):
        raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME)
      if (create and exists) or ((not create) and (not exists)):
        raise_error(file_service_pb.FileServiceErrors.EXISTENCE_ERROR)

      self.mime_content_type = self.file_storage.get_content_type(self.filename)
    else:
      blob_info = blobstore.BlobInfo.get(self.ticket)
      if not blob_info:
        raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME)
      self.blob_reader = blobstore.BlobReader(blob_info)
      self.mime_content_type = blob_info.content_type
    if content_type != file_service_pb.FileContentType.RAW:
      raise_error(file_service_pb.FileServiceErrors.WRONG_CONTENT_TYPE)

    if self.file_storage.is_finalized(self.filename):
      raise_error(file_service_pb.FileServiceErrors.FINALIZATION_ERROR,
                  'File is already finalized')

    if create:
      self.file_storage.create(self.filename)

  def read(self, request, response):
    """Read data from file

    Args:
      request: An instance of file_service_pb.ReadRequest.
      response: An instance of file_service_pb.ReadResponse.
    """
    if not self.blob_reader:
      raise_error(file_service_pb.FileServiceErrors.WRONG_OPEN_MODE)
    self.blob_reader.seek(request.pos())
    response.set_data(self.blob_reader.read(request.max_bytes()))

  def append(self, request, response):
    """Append data to file.

    Args:
      request: An instance of file_service_pb.AppendRequest.
      response: An instance of file_service_pb.AppendResponse.
    """
    sequence_key = request.sequence_key()

    if sequence_key:
      current_sequence_key = self.file_storage.get_sequence_key(self.filename)
      if current_sequence_key and current_sequence_key >= sequence_key:
        raise_error(file_service_pb.FileServiceErrors.SEQUENCE_KEY_OUT_OF_ORDER,
                    error_detail=current_sequence_key)
      self.file_storage.set_sequence_key(self.filename, sequence_key)
    self.file_storage.append(self.filename, request.data())

  def finalize(self):
    """Finalize a file.

    Copies temp file data to the blobstore.
    """
    self.file_storage.finalize(self.filename)
    blob_key = dev_appserver_upload.GenerateBlobKey()
    self.file_storage.register_blob_key(self.ticket, blob_key)

    size = self.file_storage.save_blob(self.filename, blob_key)
    blob_entity = datastore.Entity('__BlobInfo__',
                                   name=str(blob_key),
                                   namespace='')
    blob_entity['content_type'] = self.mime_content_type
    blob_entity['creation'] = _now_function()
    blob_entity['filename'] = self.ticket
    blob_entity['size'] = size
    datastore.Put(blob_entity)


class FileServiceStub(apiproxy_stub.APIProxyStub):
  """Python stub for file service."""

  def __init__(self, blob_storage):
    """Constructor."""
    super(FileServiceStub, self).__init__('file')
    self.open_files = {}
    self.file_storage = FileStorage(blob_storage)

  def _Dynamic_Open(self, request, response):
    """Handler for Open RPC call."""
    filename = request.filename()
    content_type = request.content_type()
    open_mode = request.open_mode()

    if (filename == '/blobstore/new' or
        filename.startswith('/blobstore/new?')):
      if open_mode != file_service_pb.OpenRequest.READ:
        raise_error(file_service_pb.FileServiceErrors.READ_ONLY)
      if content_type != file_service_pb.FileContentType.RAW:
        raise_error(file_service_pb.FileServiceErrors.WRONG_CONTENT_TYPE)

      self.open_files[filename] = NewBlobstoreFile(self.file_storage)
    elif (filename == '/blobstore/get_blob_key' or
        filename.startswith('/blobstore/get_blob_key?')):
      if open_mode != file_service_pb.OpenRequest.READ:
        raise_error(file_service_pb.FileServiceErrors.READ_ONLY)
      if content_type != file_service_pb.FileContentType.RAW:
        raise_error(file_service_pb.FileServiceErrors.WRONG_CONTENT_TYPE)

      self.open_files[filename] = GetBlobKeyFile(filename, self.file_storage)
    elif filename.startswith('/blobstore/'):
      self.open_files[filename] = BlobstoreFile(request, self.file_storage)
    else:
      raise_error(file_service_pb.FileServiceErrors.INVALID_FILE_NAME)

  def _Dynamic_Close(self, request, response):
    """Handler for Close RPC call."""
    filename = request.filename()
    finalize = request.finalize()

    if not filename in self.open_files:
      raise_error(file_service_pb.FileServiceErrors.FILE_NOT_OPENED)

    if finalize:
      self.open_files[filename].finalize()

    del self.open_files[filename]

  def _Dynamic_Read(self, request, response):
    """Handler for Read RPC call."""
    filename = request.filename()

    if not filename in self.open_files:
      raise_error(file_service_pb.FileServiceErrors.FILE_NOT_OPENED)

    self.open_files[filename].read(request, response)

  def _Dynamic_Append(self, request, response):
    """Handler for Append RPC call."""
    filename = request.filename()

    if not filename in self.open_files:
      raise_error(file_service_pb.FileServiceErrors.FILE_NOT_OPENED)

    self.open_files[filename].append(request, response)
