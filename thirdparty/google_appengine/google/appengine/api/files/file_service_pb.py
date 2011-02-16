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

from google.net.proto import ProtocolBuffer
import array
import base64
import dummy_thread as thread
try:
  from google3.net.proto import _net_proto___parse__python
except ImportError:
  _net_proto___parse__python = None
import sys
try:
  __import__('google.net.rpc.python.rpc_internals')
  __import__('google.net.rpc.python.pywraprpc')
  rpc_internals = sys.modules.get('google.net.rpc.python.rpc_internals')
  pywraprpc = sys.modules.get('google.net.rpc.python.pywraprpc')
  _client_stub_base_class = rpc_internals.StubbyRPCBaseStub
except ImportError:
  _client_stub_base_class = object
try:
  __import__('google.net.rpc.python.rpcserver')
  rpcserver = sys.modules.get('google.net.rpc.python.rpcserver')
  _server_stub_base_class = rpcserver.BaseRpcServer
except ImportError:
  _server_stub_base_class = object

__pychecker__ = """maxreturns=0 maxbranches=0 no-callinit
                   unusednames=printElemNumber,debug_strs no-special"""

from google.appengine.api.api_base_pb import *
import google.appengine.api.api_base_pb
class FileServiceErrors(ProtocolBuffer.ProtocolMessage):

  OK           =    0
  API_TEMPORARILY_UNAVAILABLE =    1
  REQUEST_TOO_LARGE =    3
  RESPONSE_TOO_LARGE =    4
  INVALID_FILE_NAME =    5
  OPERATION_NOT_SUPPORTED =    6
  IO_ERROR     =    7
  PERMISSION_DENIED =    8
  WRONG_CONTENT_TYPE =    9
  FILE_NOT_OPENED =   10
  WRONG_OPEN_MODE =   11
  EXCLUSIVE_LOCK_REQUIRED =   12
  EXISTENCE_ERROR =  100
  FINALIZATION_ERROR =  101
  UNSUPPORTED_CONTENT_TYPE =  102
  READ_ONLY    =  103
  EXCLUSIVE_LOCK_FAILED =  104
  SEQUENCE_KEY_OUT_OF_ORDER =  300
  WRONG_KEY_ORDER =  400
  OUT_OF_BOUNDS =  500
  GLOBS_NOT_SUPPORTED =  600
  MAX_ERROR_CODE = 9999

  _ErrorCode_NAMES = {
    0: "OK",
    1: "API_TEMPORARILY_UNAVAILABLE",
    3: "REQUEST_TOO_LARGE",
    4: "RESPONSE_TOO_LARGE",
    5: "INVALID_FILE_NAME",
    6: "OPERATION_NOT_SUPPORTED",
    7: "IO_ERROR",
    8: "PERMISSION_DENIED",
    9: "WRONG_CONTENT_TYPE",
    10: "FILE_NOT_OPENED",
    11: "WRONG_OPEN_MODE",
    12: "EXCLUSIVE_LOCK_REQUIRED",
    100: "EXISTENCE_ERROR",
    101: "FINALIZATION_ERROR",
    102: "UNSUPPORTED_CONTENT_TYPE",
    103: "READ_ONLY",
    104: "EXCLUSIVE_LOCK_FAILED",
    300: "SEQUENCE_KEY_OUT_OF_ORDER",
    400: "WRONG_KEY_ORDER",
    500: "OUT_OF_BOUNDS",
    600: "GLOBS_NOT_SUPPORTED",
    9999: "MAX_ERROR_CODE",
  }

  def ErrorCode_Name(cls, x): return cls._ErrorCode_NAMES.get(x, "")
  ErrorCode_Name = classmethod(ErrorCode_Name)


  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.FileServiceErrors', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.FileServiceErrors')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.FileServiceErrors')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.FileServiceErrors', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.FileServiceErrors', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.FileServiceErrors', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnNzeglFcnJvckNvZGWLAZIBAk9LmAEAjAGLAZIBG0FQSV9URU1QT1JBUklMWV9VTkFWQUlMQUJMRZgBAYwBiwGSARFSRVFVRVNUX1RPT19MQVJHRZgBA4wBiwGSARJSRVNQT05TRV9UT09fTEFSR0WYAQSMAYsBkgERSU5WQUxJRF9GSUxFX05BTUWYAQWMAYsBkgEXT1BFUkFUSU9OX05PVF9TVVBQT1JURUSYAQaMAYsBkgEISU9fRVJST1KYAQeMAYsBkgERUEVSTUlTU0lPTl9ERU5JRUSYAQiMAYsBkgESV1JPTkdfQ09OVEVOVF9UWVBFmAEJjAGLAZIBD0ZJTEVfTk9UX09QRU5FRJgBCowBiwGSAQ9XUk9OR19PUEVOX01PREWYAQuMAYsBkgEXRVhDTFVTSVZFX0xPQ0tfUkVRVUlSRUSYAQyMAYsBkgEPRVhJU1RFTkNFX0VSUk9SmAFkjAGLAZIBEkZJTkFMSVpBVElPTl9FUlJPUpgBZYwBiwGSARhVTlNVUFBPUlRFRF9DT05URU5UX1RZUEWYAWaMAYsBkgEJUkVBRF9PTkxZmAFnjAGLAZIBFUVYQ0xVU0lWRV9MT0NLX0ZBSUxFRJgBaIwBiwGSARlTRVFVRU5DRV9LRVlfT1VUX09GX09SREVSmAGsAowBiwGSAQ9XUk9OR19LRVlfT1JERVKYAZADjAGLAZIBDU9VVF9PRl9CT1VORFOYAfQDjAGLAZIBE0dMT0JTX05PVF9TVVBQT1JURUSYAdgEjAGLAZIBDk1BWF9FUlJPUl9DT0RFmAGPTowBdLoBsBYKJ2FwcGhvc3RpbmcvYXBpL2ZpbGVzL2ZpbGVfc2VydmljZS5wcm90bxIQYXBwaG9zdGluZy5maWxlcxodYXBwaG9zdGluZy9hcGkvYXBpX2Jhc2UucHJvdG8inwQKEUZpbGVTZXJ2aWNlRXJyb3JzIokECglFcnJvckNvZGUSBgoCT0sQABIfChtBUElfVEVNUE9SQVJJTFlfVU5BVkFJTEFCTEUQARIVChFSRVFVRVNUX1RPT19MQVJHRRADEhYKElJFU1BPTlNFX1RPT19MQVJHRRAEEhUKEUlOVkFMSURfRklMRV9OQU1FEAUSGwoXT1BFUkFUSU9OX05PVF9TVVBQT1JURUQQBhIMCghJT19FUlJPUhAHEhUKEVBFUk1JU1NJT05fREVOSUVEEAgSFgoSV1JPTkdfQ09OVEVOVF9UWVBFEAkSEwoPRklMRV9OT1RfT1BFTkVEEAoSEwoPV1JPTkdfT1BFTl9NT0RFEAsSGwoXRVhDTFVTSVZFX0xPQ0tfUkVRVUlSRUQQDBITCg9FWElTVEVOQ0VfRVJST1IQZBIWChJGSU5BTElaQVRJT05fRVJST1IQZRIcChhVTlNVUFBPUlRFRF9DT05URU5UX1RZUEUQZhINCglSRUFEX09OTFkQZxIZChVFWENMVVNJVkVfTE9DS19GQUlMRUQQaBIeChlTRVFVRU5DRV9LRVlfT1VUX09GX09SREVSEKwCEhQKD1dST05HX0tFWV9PUkRFUhCQAxISCg1PVVRfT0ZfQk9VTkRTEPQDEhgKE0dMT0JTX05PVF9TVVBQT1JURUQQ2AQSEwoOTUFYX0VSUk9SX0NPREUQj04iUgoPRmlsZUNvbnRlbnRUeXBlIj8KC0NvbnRlbnRUeXBlEgcKA1JBVxAAEhUKEU9SREVSRURfS0VZX1ZBTFVFEAISEAoMSU5WQUxJRF9UWVBFEH8ijgMKC09wZW5SZXF1ZXN0EhAKCGZpbGVuYW1lGAEgAigJEkMKDGNvbnRlbnRfdHlwZRgCIAIoDjItLmFwcGhvc3RpbmcuZmlsZXMuRmlsZUNvbnRlbnRUeXBlLkNvbnRlbnRUeXBlEjkKCW9wZW5fbW9kZRgDIAIoDjImLmFwcGhvc3RpbmcuZmlsZXMuT3BlblJlcXVlc3QuT3Blbk1vZGUSHQoOZXhjbHVzaXZlX2xvY2sYBCABKAg6BWZhbHNlEh4KD2J1ZmZlcmVkX291dHB1dBgFIAEoCDoFZmFsc2USQwoOY3JlYXRlX29wdGlvbnMYBiABKAsyKy5hcHBob3N0aW5nLmZpbGVzLk9wZW5SZXF1ZXN0LkNyZWF0ZU9wdGlvbnMaRwoNQ3JlYXRlT3B0aW9ucxIVCgZjcmVhdGUYASABKAg6BWZhbHNlEh8KF2V4cGlyYXRpb25fdGltZV9zZWNvbmRzGAIgASgDIiAKCE9wZW5Nb2RlEgoKBkFQUEVORBABEggKBFJFQUQQAiIOCgxPcGVuUmVzcG9uc2UiOQoMQ2xvc2VSZXF1ZXN0EhAKCGZpbGVuYW1lGAEgAigJEhcKCGZpbmFsaXplGAIgASgIOgVmYWxzZSIPCg1DbG9zZVJlc3BvbnNlIqIBCghGaWxlU3RhdBIQCghmaWxlbmFtZRgBIAIoCRJDCgxjb250ZW50X3R5cGUYAiACKA4yLS5hcHBob3N0aW5nLmZpbGVzLkZpbGVDb250ZW50VHlwZS5Db250ZW50VHlwZRIRCglmaW5hbGl6ZWQYAyACKAgSDgoGbGVuZ3RoGAQgASgDEg0KBWN0aW1lGAUgASgDEg0KBW10aW1lGAYgASgDIjIKC1N0YXRSZXF1ZXN0EhAKCGZpbGVuYW1lGAEgASgJEhEKCWZpbGVfZ2xvYhgCIAEoCSJZCgxTdGF0UmVzcG9uc2USKAoEc3RhdBgBIAMoCzIaLmFwcGhvc3RpbmcuZmlsZXMuRmlsZVN0YXQSHwoQbW9yZV9maWxlc19mb3VuZBgCIAIoCDoFZmFsc2UiTQoNQXBwZW5kUmVxdWVzdBIQCghmaWxlbmFtZRgBIAIoCRIQCgRkYXRhGAIgAigMQgIIARIYCgxzZXF1ZW5jZV9rZXkYAyABKAlCAggBIhAKDkFwcGVuZFJlc3BvbnNlIk0KFUFwcGVuZEtleVZhbHVlUmVxdWVzdBIQCghmaWxlbmFtZRgBIAIoCRIPCgNrZXkYAiACKAxCAggBEhEKBXZhbHVlGAMgAigMQgIIASIYChZBcHBlbmRLZXlWYWx1ZVJlc3BvbnNlIiEKDURlbGV0ZVJlcXVlc3QSEAoIZmlsZW5hbWUYASACKAkiEAoORGVsZXRlUmVzcG9uc2UiPwoLUmVhZFJlcXVlc3QSEAoIZmlsZW5hbWUYASACKAkSCwoDcG9zGAIgAigDEhEKCW1heF9ieXRlcxgDIAIoAyIgCgxSZWFkUmVzcG9uc2USEAoEZGF0YRgBIAIoDEICCAEiZAoTUmVhZEtleVZhbHVlUmVxdWVzdBIQCghmaWxlbmFtZRgBIAIoCRIVCglzdGFydF9rZXkYAiACKAxCAggBEhEKCW1heF9ieXRlcxgDIAIoAxIRCgl2YWx1ZV9wb3MYBCABKAMisAEKFFJlYWRLZXlWYWx1ZVJlc3BvbnNlEj0KBGRhdGEYASADKAsyLy5hcHBob3N0aW5nLmZpbGVzLlJlYWRLZXlWYWx1ZVJlc3BvbnNlLktleVZhbHVlEhAKCG5leHRfa2V5GAIgASgMEhcKD3RydW5jYXRlZF92YWx1ZRgDIAEoCBouCghLZXlWYWx1ZRIPCgNrZXkYASACKAxCAggBEhEKBXZhbHVlGAIgAigMQgIIATKKBQoLRmlsZVNlcnZpY2USRQoET3BlbhIdLmFwcGhvc3RpbmcuZmlsZXMuT3BlblJlcXVlc3QaHi5hcHBob3N0aW5nLmZpbGVzLk9wZW5SZXNwb25zZRJICgVDbG9zZRIeLmFwcGhvc3RpbmcuZmlsZXMuQ2xvc2VSZXF1ZXN0Gh8uYXBwaG9zdGluZy5maWxlcy5DbG9zZVJlc3BvbnNlEksKBkFwcGVuZBIfLmFwcGhvc3RpbmcuZmlsZXMuQXBwZW5kUmVxdWVzdBogLmFwcGhvc3RpbmcuZmlsZXMuQXBwZW5kUmVzcG9uc2USYwoOQXBwZW5kS2V5VmFsdWUSJy5hcHBob3N0aW5nLmZpbGVzLkFwcGVuZEtleVZhbHVlUmVxdWVzdBooLmFwcGhvc3RpbmcuZmlsZXMuQXBwZW5kS2V5VmFsdWVSZXNwb25zZRJFCgRTdGF0Eh0uYXBwaG9zdGluZy5maWxlcy5TdGF0UmVxdWVzdBoeLmFwcGhvc3RpbmcuZmlsZXMuU3RhdFJlc3BvbnNlEksKBkRlbGV0ZRIfLmFwcGhvc3RpbmcuZmlsZXMuRGVsZXRlUmVxdWVzdBogLmFwcGhvc3RpbmcuZmlsZXMuRGVsZXRlUmVzcG9uc2USRQoEUmVhZBIdLmFwcGhvc3RpbmcuZmlsZXMuUmVhZFJlcXVlc3QaHi5hcHBob3N0aW5nLmZpbGVzLlJlYWRSZXNwb25zZRJdCgxSZWFkS2V5VmFsdWUSJS5hcHBob3N0aW5nLmZpbGVzLlJlYWRLZXlWYWx1ZVJlcXVlc3QaJi5hcHBob3N0aW5nLmZpbGVzLlJlYWRLZXlWYWx1ZVJlc3BvbnNlQjUKHmNvbS5nb29nbGUuYXBwZW5naW5lLmFwaS5maWxlcxABIAEoAkINRmlsZVNlcnZpY2VQYg=="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class FileContentType(ProtocolBuffer.ProtocolMessage):

  RAW          =    0
  ORDERED_KEY_VALUE =    2
  INVALID_TYPE =  127

  _ContentType_NAMES = {
    0: "RAW",
    2: "ORDERED_KEY_VALUE",
    127: "INVALID_TYPE",
  }

  def ContentType_Name(cls, x): return cls._ContentType_NAMES.get(x, "")
  ContentType_Name = classmethod(ContentType_Name)


  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.FileContentType', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.FileContentType')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.FileContentType')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.FileContentType', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.FileContentType', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.FileContentType', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KIGFwcGhvc3RpbmcuZmlsZXMuRmlsZUNvbnRlbnRUeXBlc3oLQ29udGVudFR5cGWLAZIBA1JBV5gBAIwBiwGSARFPUkRFUkVEX0tFWV9WQUxVRZgBAowBiwGSAQxJTlZBTElEX1RZUEWYAX+MAXTCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3Jz"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class OpenRequest_CreateOptions(ProtocolBuffer.ProtocolMessage):
  has_create_ = 0
  create_ = 0
  has_expiration_time_seconds_ = 0
  expiration_time_seconds_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def create(self): return self.create_

  def set_create(self, x):
    self.has_create_ = 1
    self.create_ = x

  def clear_create(self):
    if self.has_create_:
      self.has_create_ = 0
      self.create_ = 0

  def has_create(self): return self.has_create_

  def expiration_time_seconds(self): return self.expiration_time_seconds_

  def set_expiration_time_seconds(self, x):
    self.has_expiration_time_seconds_ = 1
    self.expiration_time_seconds_ = x

  def clear_expiration_time_seconds(self):
    if self.has_expiration_time_seconds_:
      self.has_expiration_time_seconds_ = 0
      self.expiration_time_seconds_ = 0

  def has_expiration_time_seconds(self): return self.has_expiration_time_seconds_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_create()): self.set_create(x.create())
    if (x.has_expiration_time_seconds()): self.set_expiration_time_seconds(x.expiration_time_seconds())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.OpenRequest_CreateOptions', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.OpenRequest_CreateOptions')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.OpenRequest_CreateOptions')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.OpenRequest_CreateOptions', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.OpenRequest_CreateOptions', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.OpenRequest_CreateOptions', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_create_ != x.has_create_: return 0
    if self.has_create_ and self.create_ != x.create_: return 0
    if self.has_expiration_time_seconds_ != x.has_expiration_time_seconds_: return 0
    if self.has_expiration_time_seconds_ and self.expiration_time_seconds_ != x.expiration_time_seconds_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_create_): n += 2
    if (self.has_expiration_time_seconds_): n += 1 + self.lengthVarInt64(self.expiration_time_seconds_)
    return n

  def ByteSizePartial(self):
    n = 0
    if (self.has_create_): n += 2
    if (self.has_expiration_time_seconds_): n += 1 + self.lengthVarInt64(self.expiration_time_seconds_)
    return n

  def Clear(self):
    self.clear_create()
    self.clear_expiration_time_seconds()

  def OutputUnchecked(self, out):
    if (self.has_create_):
      out.putVarInt32(8)
      out.putBoolean(self.create_)
    if (self.has_expiration_time_seconds_):
      out.putVarInt32(16)
      out.putVarInt64(self.expiration_time_seconds_)

  def OutputPartial(self, out):
    if (self.has_create_):
      out.putVarInt32(8)
      out.putBoolean(self.create_)
    if (self.has_expiration_time_seconds_):
      out.putVarInt32(16)
      out.putVarInt64(self.expiration_time_seconds_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 8:
        self.set_create(d.getBoolean())
        continue
      if tt == 16:
        self.set_expiration_time_seconds(d.getVarInt64())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_create_: res+=prefix+("create: %s\n" % self.DebugFormatBool(self.create_))
    if self.has_expiration_time_seconds_: res+=prefix+("expiration_time_seconds: %s\n" % self.DebugFormatInt64(self.expiration_time_seconds_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kcreate = 1
  kexpiration_time_seconds = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "create",
    2: "expiration_time_seconds",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.NUMERIC,
    2: ProtocolBuffer.Encoder.NUMERIC,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KKmFwcGhvc3RpbmcuZmlsZXMuT3BlblJlcXVlc3RfQ3JlYXRlT3B0aW9ucxMaBmNyZWF0ZSABKAAwCDgBQgVmYWxzZaMBqgEHZGVmYXVsdLIBBWZhbHNlpAEUExoXZXhwaXJhdGlvbl90aW1lX3NlY29uZHMgAigAMAM4ARTCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3JzygEqYXBwaG9zdGluZy5maWxlcy5PcGVuUmVxdWVzdC5DcmVhdGVPcHRpb25z"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class OpenRequest(ProtocolBuffer.ProtocolMessage):

  APPEND       =    1
  READ         =    2

  _OpenMode_NAMES = {
    1: "APPEND",
    2: "READ",
  }

  def OpenMode_Name(cls, x): return cls._OpenMode_NAMES.get(x, "")
  OpenMode_Name = classmethod(OpenMode_Name)

  has_filename_ = 0
  filename_ = ""
  has_content_type_ = 0
  content_type_ = 0
  has_open_mode_ = 0
  open_mode_ = 0
  has_exclusive_lock_ = 0
  exclusive_lock_ = 0
  has_buffered_output_ = 0
  buffered_output_ = 0
  has_create_options_ = 0
  create_options_ = None

  def __init__(self, contents=None):
    self.lazy_init_lock_ = thread.allocate_lock()
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def content_type(self): return self.content_type_

  def set_content_type(self, x):
    self.has_content_type_ = 1
    self.content_type_ = x

  def clear_content_type(self):
    if self.has_content_type_:
      self.has_content_type_ = 0
      self.content_type_ = 0

  def has_content_type(self): return self.has_content_type_

  def open_mode(self): return self.open_mode_

  def set_open_mode(self, x):
    self.has_open_mode_ = 1
    self.open_mode_ = x

  def clear_open_mode(self):
    if self.has_open_mode_:
      self.has_open_mode_ = 0
      self.open_mode_ = 0

  def has_open_mode(self): return self.has_open_mode_

  def exclusive_lock(self): return self.exclusive_lock_

  def set_exclusive_lock(self, x):
    self.has_exclusive_lock_ = 1
    self.exclusive_lock_ = x

  def clear_exclusive_lock(self):
    if self.has_exclusive_lock_:
      self.has_exclusive_lock_ = 0
      self.exclusive_lock_ = 0

  def has_exclusive_lock(self): return self.has_exclusive_lock_

  def buffered_output(self): return self.buffered_output_

  def set_buffered_output(self, x):
    self.has_buffered_output_ = 1
    self.buffered_output_ = x

  def clear_buffered_output(self):
    if self.has_buffered_output_:
      self.has_buffered_output_ = 0
      self.buffered_output_ = 0

  def has_buffered_output(self): return self.has_buffered_output_

  def create_options(self):
    if self.create_options_ is None:
      self.lazy_init_lock_.acquire()
      try:
        if self.create_options_ is None: self.create_options_ = OpenRequest_CreateOptions()
      finally:
        self.lazy_init_lock_.release()
    return self.create_options_

  def mutable_create_options(self): self.has_create_options_ = 1; return self.create_options()

  def clear_create_options(self):
    if self.has_create_options_:
      self.has_create_options_ = 0;
      if self.create_options_ is not None: self.create_options_.Clear()

  def has_create_options(self): return self.has_create_options_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_content_type()): self.set_content_type(x.content_type())
    if (x.has_open_mode()): self.set_open_mode(x.open_mode())
    if (x.has_exclusive_lock()): self.set_exclusive_lock(x.exclusive_lock())
    if (x.has_buffered_output()): self.set_buffered_output(x.buffered_output())
    if (x.has_create_options()): self.mutable_create_options().MergeFrom(x.create_options())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.OpenRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.OpenRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.OpenRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.OpenRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.OpenRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.OpenRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_content_type_ != x.has_content_type_: return 0
    if self.has_content_type_ and self.content_type_ != x.content_type_: return 0
    if self.has_open_mode_ != x.has_open_mode_: return 0
    if self.has_open_mode_ and self.open_mode_ != x.open_mode_: return 0
    if self.has_exclusive_lock_ != x.has_exclusive_lock_: return 0
    if self.has_exclusive_lock_ and self.exclusive_lock_ != x.exclusive_lock_: return 0
    if self.has_buffered_output_ != x.has_buffered_output_: return 0
    if self.has_buffered_output_ and self.buffered_output_ != x.buffered_output_: return 0
    if self.has_create_options_ != x.has_create_options_: return 0
    if self.has_create_options_ and self.create_options_ != x.create_options_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    if (not self.has_content_type_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: content_type not set.')
    if (not self.has_open_mode_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: open_mode not set.')
    if (self.has_create_options_ and not self.create_options_.IsInitialized(debug_strs)): initialized = 0
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    n += self.lengthVarInt64(self.content_type_)
    n += self.lengthVarInt64(self.open_mode_)
    if (self.has_exclusive_lock_): n += 2
    if (self.has_buffered_output_): n += 2
    if (self.has_create_options_): n += 1 + self.lengthString(self.create_options_.ByteSize())
    return n + 3

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_content_type_):
      n += 1
      n += self.lengthVarInt64(self.content_type_)
    if (self.has_open_mode_):
      n += 1
      n += self.lengthVarInt64(self.open_mode_)
    if (self.has_exclusive_lock_): n += 2
    if (self.has_buffered_output_): n += 2
    if (self.has_create_options_): n += 1 + self.lengthString(self.create_options_.ByteSizePartial())
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_content_type()
    self.clear_open_mode()
    self.clear_exclusive_lock()
    self.clear_buffered_output()
    self.clear_create_options()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    out.putVarInt32(16)
    out.putVarInt32(self.content_type_)
    out.putVarInt32(24)
    out.putVarInt32(self.open_mode_)
    if (self.has_exclusive_lock_):
      out.putVarInt32(32)
      out.putBoolean(self.exclusive_lock_)
    if (self.has_buffered_output_):
      out.putVarInt32(40)
      out.putBoolean(self.buffered_output_)
    if (self.has_create_options_):
      out.putVarInt32(50)
      out.putVarInt32(self.create_options_.ByteSize())
      self.create_options_.OutputUnchecked(out)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_content_type_):
      out.putVarInt32(16)
      out.putVarInt32(self.content_type_)
    if (self.has_open_mode_):
      out.putVarInt32(24)
      out.putVarInt32(self.open_mode_)
    if (self.has_exclusive_lock_):
      out.putVarInt32(32)
      out.putBoolean(self.exclusive_lock_)
    if (self.has_buffered_output_):
      out.putVarInt32(40)
      out.putBoolean(self.buffered_output_)
    if (self.has_create_options_):
      out.putVarInt32(50)
      out.putVarInt32(self.create_options_.ByteSizePartial())
      self.create_options_.OutputPartial(out)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 16:
        self.set_content_type(d.getVarInt32())
        continue
      if tt == 24:
        self.set_open_mode(d.getVarInt32())
        continue
      if tt == 32:
        self.set_exclusive_lock(d.getBoolean())
        continue
      if tt == 40:
        self.set_buffered_output(d.getBoolean())
        continue
      if tt == 50:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.mutable_create_options().TryMerge(tmp)
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_content_type_: res+=prefix+("content_type: %s\n" % self.DebugFormatInt32(self.content_type_))
    if self.has_open_mode_: res+=prefix+("open_mode: %s\n" % self.DebugFormatInt32(self.open_mode_))
    if self.has_exclusive_lock_: res+=prefix+("exclusive_lock: %s\n" % self.DebugFormatBool(self.exclusive_lock_))
    if self.has_buffered_output_: res+=prefix+("buffered_output: %s\n" % self.DebugFormatBool(self.buffered_output_))
    if self.has_create_options_:
      res+=prefix+"create_options <\n"
      res+=self.create_options_.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kcontent_type = 2
  kopen_mode = 3
  kexclusive_lock = 4
  kbuffered_output = 5
  kcreate_options = 6

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "content_type",
    3: "open_mode",
    4: "exclusive_lock",
    5: "buffered_output",
    6: "create_options",
  }, 6)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
    4: ProtocolBuffer.Encoder.NUMERIC,
    5: ProtocolBuffer.Encoder.NUMERIC,
    6: ProtocolBuffer.Encoder.STRING,
  }, 6, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHGFwcGhvc3RpbmcuZmlsZXMuT3BlblJlcXVlc3QTGghmaWxlbmFtZSABKAIwCTgCFBMaDGNvbnRlbnRfdHlwZSACKAAwBTgCFBMaCW9wZW5fbW9kZSADKAAwBTgCaAAUExoOZXhjbHVzaXZlX2xvY2sgBCgAMAg4AUIFZmFsc2WjAaoBB2RlZmF1bHSyAQVmYWxzZaQBFBMaD2J1ZmZlcmVkX291dHB1dCAFKAAwCDgBQgVmYWxzZaMBqgEHZGVmYXVsdLIBBWZhbHNlpAEUExoOY3JlYXRlX29wdGlvbnMgBigCMAs4AUoqYXBwaG9zdGluZy5maWxlcy5PcGVuUmVxdWVzdF9DcmVhdGVPcHRpb25zFHN6CE9wZW5Nb2RliwGSAQZBUFBFTkSYAQGMAYsBkgEEUkVBRJgBAowBdMIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class OpenResponse(ProtocolBuffer.ProtocolMessage):

  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.OpenResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.OpenResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.OpenResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.OpenResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.OpenResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.OpenResponse', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHWFwcGhvc3RpbmcuZmlsZXMuT3BlblJlc3BvbnNlwgEiYXBwaG9zdGluZy5maWxlcy5GaWxlU2VydmljZUVycm9ycw=="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class CloseRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_finalize_ = 0
  finalize_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def finalize(self): return self.finalize_

  def set_finalize(self, x):
    self.has_finalize_ = 1
    self.finalize_ = x

  def clear_finalize(self):
    if self.has_finalize_:
      self.has_finalize_ = 0
      self.finalize_ = 0

  def has_finalize(self): return self.has_finalize_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_finalize()): self.set_finalize(x.finalize())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.CloseRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.CloseRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.CloseRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.CloseRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.CloseRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.CloseRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_finalize_ != x.has_finalize_: return 0
    if self.has_finalize_ and self.finalize_ != x.finalize_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    if (self.has_finalize_): n += 2
    return n + 1

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_finalize_): n += 2
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_finalize()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    if (self.has_finalize_):
      out.putVarInt32(16)
      out.putBoolean(self.finalize_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_finalize_):
      out.putVarInt32(16)
      out.putBoolean(self.finalize_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 16:
        self.set_finalize(d.getBoolean())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_finalize_: res+=prefix+("finalize: %s\n" % self.DebugFormatBool(self.finalize_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kfinalize = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "finalize",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.NUMERIC,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHWFwcGhvc3RpbmcuZmlsZXMuQ2xvc2VSZXF1ZXN0ExoIZmlsZW5hbWUgASgCMAk4AhQTGghmaW5hbGl6ZSACKAAwCDgBQgVmYWxzZaMBqgEHZGVmYXVsdLIBBWZhbHNlpAEUwgEiYXBwaG9zdGluZy5maWxlcy5GaWxlU2VydmljZUVycm9ycw=="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class CloseResponse(ProtocolBuffer.ProtocolMessage):

  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.CloseResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.CloseResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.CloseResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.CloseResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.CloseResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.CloseResponse', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHmFwcGhvc3RpbmcuZmlsZXMuQ2xvc2VSZXNwb25zZcIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class FileStat(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_content_type_ = 0
  content_type_ = 0
  has_finalized_ = 0
  finalized_ = 0
  has_length_ = 0
  length_ = 0
  has_ctime_ = 0
  ctime_ = 0
  has_mtime_ = 0
  mtime_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def content_type(self): return self.content_type_

  def set_content_type(self, x):
    self.has_content_type_ = 1
    self.content_type_ = x

  def clear_content_type(self):
    if self.has_content_type_:
      self.has_content_type_ = 0
      self.content_type_ = 0

  def has_content_type(self): return self.has_content_type_

  def finalized(self): return self.finalized_

  def set_finalized(self, x):
    self.has_finalized_ = 1
    self.finalized_ = x

  def clear_finalized(self):
    if self.has_finalized_:
      self.has_finalized_ = 0
      self.finalized_ = 0

  def has_finalized(self): return self.has_finalized_

  def length(self): return self.length_

  def set_length(self, x):
    self.has_length_ = 1
    self.length_ = x

  def clear_length(self):
    if self.has_length_:
      self.has_length_ = 0
      self.length_ = 0

  def has_length(self): return self.has_length_

  def ctime(self): return self.ctime_

  def set_ctime(self, x):
    self.has_ctime_ = 1
    self.ctime_ = x

  def clear_ctime(self):
    if self.has_ctime_:
      self.has_ctime_ = 0
      self.ctime_ = 0

  def has_ctime(self): return self.has_ctime_

  def mtime(self): return self.mtime_

  def set_mtime(self, x):
    self.has_mtime_ = 1
    self.mtime_ = x

  def clear_mtime(self):
    if self.has_mtime_:
      self.has_mtime_ = 0
      self.mtime_ = 0

  def has_mtime(self): return self.has_mtime_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_content_type()): self.set_content_type(x.content_type())
    if (x.has_finalized()): self.set_finalized(x.finalized())
    if (x.has_length()): self.set_length(x.length())
    if (x.has_ctime()): self.set_ctime(x.ctime())
    if (x.has_mtime()): self.set_mtime(x.mtime())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.FileStat', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.FileStat')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.FileStat')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.FileStat', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.FileStat', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.FileStat', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_content_type_ != x.has_content_type_: return 0
    if self.has_content_type_ and self.content_type_ != x.content_type_: return 0
    if self.has_finalized_ != x.has_finalized_: return 0
    if self.has_finalized_ and self.finalized_ != x.finalized_: return 0
    if self.has_length_ != x.has_length_: return 0
    if self.has_length_ and self.length_ != x.length_: return 0
    if self.has_ctime_ != x.has_ctime_: return 0
    if self.has_ctime_ and self.ctime_ != x.ctime_: return 0
    if self.has_mtime_ != x.has_mtime_: return 0
    if self.has_mtime_ and self.mtime_ != x.mtime_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    if (not self.has_content_type_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: content_type not set.')
    if (not self.has_finalized_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: finalized not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    n += self.lengthVarInt64(self.content_type_)
    if (self.has_length_): n += 1 + self.lengthVarInt64(self.length_)
    if (self.has_ctime_): n += 1 + self.lengthVarInt64(self.ctime_)
    if (self.has_mtime_): n += 1 + self.lengthVarInt64(self.mtime_)
    return n + 4

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_content_type_):
      n += 1
      n += self.lengthVarInt64(self.content_type_)
    if (self.has_finalized_):
      n += 2
    if (self.has_length_): n += 1 + self.lengthVarInt64(self.length_)
    if (self.has_ctime_): n += 1 + self.lengthVarInt64(self.ctime_)
    if (self.has_mtime_): n += 1 + self.lengthVarInt64(self.mtime_)
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_content_type()
    self.clear_finalized()
    self.clear_length()
    self.clear_ctime()
    self.clear_mtime()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    out.putVarInt32(16)
    out.putVarInt32(self.content_type_)
    out.putVarInt32(24)
    out.putBoolean(self.finalized_)
    if (self.has_length_):
      out.putVarInt32(32)
      out.putVarInt64(self.length_)
    if (self.has_ctime_):
      out.putVarInt32(40)
      out.putVarInt64(self.ctime_)
    if (self.has_mtime_):
      out.putVarInt32(48)
      out.putVarInt64(self.mtime_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_content_type_):
      out.putVarInt32(16)
      out.putVarInt32(self.content_type_)
    if (self.has_finalized_):
      out.putVarInt32(24)
      out.putBoolean(self.finalized_)
    if (self.has_length_):
      out.putVarInt32(32)
      out.putVarInt64(self.length_)
    if (self.has_ctime_):
      out.putVarInt32(40)
      out.putVarInt64(self.ctime_)
    if (self.has_mtime_):
      out.putVarInt32(48)
      out.putVarInt64(self.mtime_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 16:
        self.set_content_type(d.getVarInt32())
        continue
      if tt == 24:
        self.set_finalized(d.getBoolean())
        continue
      if tt == 32:
        self.set_length(d.getVarInt64())
        continue
      if tt == 40:
        self.set_ctime(d.getVarInt64())
        continue
      if tt == 48:
        self.set_mtime(d.getVarInt64())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_content_type_: res+=prefix+("content_type: %s\n" % self.DebugFormatInt32(self.content_type_))
    if self.has_finalized_: res+=prefix+("finalized: %s\n" % self.DebugFormatBool(self.finalized_))
    if self.has_length_: res+=prefix+("length: %s\n" % self.DebugFormatInt64(self.length_))
    if self.has_ctime_: res+=prefix+("ctime: %s\n" % self.DebugFormatInt64(self.ctime_))
    if self.has_mtime_: res+=prefix+("mtime: %s\n" % self.DebugFormatInt64(self.mtime_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kcontent_type = 2
  kfinalized = 3
  klength = 4
  kctime = 5
  kmtime = 6

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "content_type",
    3: "finalized",
    4: "length",
    5: "ctime",
    6: "mtime",
  }, 6)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
    4: ProtocolBuffer.Encoder.NUMERIC,
    5: ProtocolBuffer.Encoder.NUMERIC,
    6: ProtocolBuffer.Encoder.NUMERIC,
  }, 6, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KGWFwcGhvc3RpbmcuZmlsZXMuRmlsZVN0YXQTGghmaWxlbmFtZSABKAIwCTgCFBMaDGNvbnRlbnRfdHlwZSACKAAwBTgCFBMaCWZpbmFsaXplZCADKAAwCDgCFBMaBmxlbmd0aCAEKAAwAzgBFBMaBWN0aW1lIAUoADADOAEUExoFbXRpbWUgBigAMAM4ARTCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3Jz"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class StatRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_file_glob_ = 0
  file_glob_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def file_glob(self): return self.file_glob_

  def set_file_glob(self, x):
    self.has_file_glob_ = 1
    self.file_glob_ = x

  def clear_file_glob(self):
    if self.has_file_glob_:
      self.has_file_glob_ = 0
      self.file_glob_ = ""

  def has_file_glob(self): return self.has_file_glob_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_file_glob()): self.set_file_glob(x.file_glob())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.StatRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.StatRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.StatRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.StatRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.StatRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.StatRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_file_glob_ != x.has_file_glob_: return 0
    if self.has_file_glob_ and self.file_glob_ != x.file_glob_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    if (self.has_filename_): n += 1 + self.lengthString(len(self.filename_))
    if (self.has_file_glob_): n += 1 + self.lengthString(len(self.file_glob_))
    return n

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_): n += 1 + self.lengthString(len(self.filename_))
    if (self.has_file_glob_): n += 1 + self.lengthString(len(self.file_glob_))
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_file_glob()

  def OutputUnchecked(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_file_glob_):
      out.putVarInt32(18)
      out.putPrefixedString(self.file_glob_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_file_glob_):
      out.putVarInt32(18)
      out.putPrefixedString(self.file_glob_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_file_glob(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_file_glob_: res+=prefix+("file_glob: %s\n" % self.DebugFormatString(self.file_glob_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kfile_glob = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "file_glob",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHGFwcGhvc3RpbmcuZmlsZXMuU3RhdFJlcXVlc3QTGghmaWxlbmFtZSABKAIwCTgBFBMaCWZpbGVfZ2xvYiACKAIwCTgBFMIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class StatResponse(ProtocolBuffer.ProtocolMessage):
  has_more_files_found_ = 0
  more_files_found_ = 0

  def __init__(self, contents=None):
    self.stat_ = []
    if contents is not None: self.MergeFromString(contents)

  def stat_size(self): return len(self.stat_)
  def stat_list(self): return self.stat_

  def stat(self, i):
    return self.stat_[i]

  def mutable_stat(self, i):
    return self.stat_[i]

  def add_stat(self):
    x = FileStat()
    self.stat_.append(x)
    return x

  def clear_stat(self):
    self.stat_ = []
  def more_files_found(self): return self.more_files_found_

  def set_more_files_found(self, x):
    self.has_more_files_found_ = 1
    self.more_files_found_ = x

  def clear_more_files_found(self):
    if self.has_more_files_found_:
      self.has_more_files_found_ = 0
      self.more_files_found_ = 0

  def has_more_files_found(self): return self.has_more_files_found_


  def MergeFrom(self, x):
    assert x is not self
    for i in xrange(x.stat_size()): self.add_stat().CopyFrom(x.stat(i))
    if (x.has_more_files_found()): self.set_more_files_found(x.more_files_found())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.StatResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.StatResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.StatResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.StatResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.StatResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.StatResponse', s)


  def Equals(self, x):
    if x is self: return 1
    if len(self.stat_) != len(x.stat_): return 0
    for e1, e2 in zip(self.stat_, x.stat_):
      if e1 != e2: return 0
    if self.has_more_files_found_ != x.has_more_files_found_: return 0
    if self.has_more_files_found_ and self.more_files_found_ != x.more_files_found_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    for p in self.stat_:
      if not p.IsInitialized(debug_strs): initialized=0
    if (not self.has_more_files_found_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: more_files_found not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += 1 * len(self.stat_)
    for i in xrange(len(self.stat_)): n += self.lengthString(self.stat_[i].ByteSize())
    return n + 2

  def ByteSizePartial(self):
    n = 0
    n += 1 * len(self.stat_)
    for i in xrange(len(self.stat_)): n += self.lengthString(self.stat_[i].ByteSizePartial())
    if (self.has_more_files_found_):
      n += 2
    return n

  def Clear(self):
    self.clear_stat()
    self.clear_more_files_found()

  def OutputUnchecked(self, out):
    for i in xrange(len(self.stat_)):
      out.putVarInt32(10)
      out.putVarInt32(self.stat_[i].ByteSize())
      self.stat_[i].OutputUnchecked(out)
    out.putVarInt32(16)
    out.putBoolean(self.more_files_found_)

  def OutputPartial(self, out):
    for i in xrange(len(self.stat_)):
      out.putVarInt32(10)
      out.putVarInt32(self.stat_[i].ByteSizePartial())
      self.stat_[i].OutputPartial(out)
    if (self.has_more_files_found_):
      out.putVarInt32(16)
      out.putBoolean(self.more_files_found_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.add_stat().TryMerge(tmp)
        continue
      if tt == 16:
        self.set_more_files_found(d.getBoolean())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    cnt=0
    for e in self.stat_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("stat%s <\n" % elm)
      res+=e.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
      cnt+=1
    if self.has_more_files_found_: res+=prefix+("more_files_found: %s\n" % self.DebugFormatBool(self.more_files_found_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kstat = 1
  kmore_files_found = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "stat",
    2: "more_files_found",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.NUMERIC,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHWFwcGhvc3RpbmcuZmlsZXMuU3RhdFJlc3BvbnNlExoEc3RhdCABKAIwCzgDShlhcHBob3N0aW5nLmZpbGVzLkZpbGVTdGF0FBMaEG1vcmVfZmlsZXNfZm91bmQgAigAMAg4AkIFZmFsc2WjAaoBB2RlZmF1bHSyAQVmYWxzZaQBFMIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class AppendRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_data_ = 0
  data_ = ""
  has_sequence_key_ = 0
  sequence_key_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def data(self): return self.data_

  def set_data(self, x):
    self.has_data_ = 1
    self.data_ = x

  def clear_data(self):
    if self.has_data_:
      self.has_data_ = 0
      self.data_ = ""

  def has_data(self): return self.has_data_

  def sequence_key(self): return self.sequence_key_

  def set_sequence_key(self, x):
    self.has_sequence_key_ = 1
    self.sequence_key_ = x

  def clear_sequence_key(self):
    if self.has_sequence_key_:
      self.has_sequence_key_ = 0
      self.sequence_key_ = ""

  def has_sequence_key(self): return self.has_sequence_key_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_data()): self.set_data(x.data())
    if (x.has_sequence_key()): self.set_sequence_key(x.sequence_key())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.AppendRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.AppendRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.AppendRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.AppendRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.AppendRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.AppendRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_data_ != x.has_data_: return 0
    if self.has_data_ and self.data_ != x.data_: return 0
    if self.has_sequence_key_ != x.has_sequence_key_: return 0
    if self.has_sequence_key_ and self.sequence_key_ != x.sequence_key_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    if (not self.has_data_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: data not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    n += self.lengthString(len(self.data_))
    if (self.has_sequence_key_): n += 1 + self.lengthString(len(self.sequence_key_))
    return n + 2

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_data_):
      n += 1
      n += self.lengthString(len(self.data_))
    if (self.has_sequence_key_): n += 1 + self.lengthString(len(self.sequence_key_))
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_data()
    self.clear_sequence_key()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    out.putVarInt32(18)
    out.putPrefixedString(self.data_)
    if (self.has_sequence_key_):
      out.putVarInt32(26)
      out.putPrefixedString(self.sequence_key_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_data_):
      out.putVarInt32(18)
      out.putPrefixedString(self.data_)
    if (self.has_sequence_key_):
      out.putVarInt32(26)
      out.putPrefixedString(self.sequence_key_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_data(d.getPrefixedString())
        continue
      if tt == 26:
        self.set_sequence_key(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_data_: res+=prefix+("data: %s\n" % self.DebugFormatString(self.data_))
    if self.has_sequence_key_: res+=prefix+("sequence_key: %s\n" % self.DebugFormatString(self.sequence_key_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kdata = 2
  ksequence_key = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "data",
    3: "sequence_key",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.STRING,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHmFwcGhvc3RpbmcuZmlsZXMuQXBwZW5kUmVxdWVzdBMaCGZpbGVuYW1lIAEoAjAJOAIUExoEZGF0YSACKAIwCTgCowGqAQVjdHlwZbIBBENvcmSkARQTGgxzZXF1ZW5jZV9rZXkgAygCMAk4AaMBqgEFY3R5cGWyAQRDb3JkpAEUwgEiYXBwaG9zdGluZy5maWxlcy5GaWxlU2VydmljZUVycm9ycw=="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class AppendResponse(ProtocolBuffer.ProtocolMessage):

  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.AppendResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.AppendResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.AppendResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.AppendResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.AppendResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.AppendResponse', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KH2FwcGhvc3RpbmcuZmlsZXMuQXBwZW5kUmVzcG9uc2XCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3Jz"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class AppendKeyValueRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_key_ = 0
  key_ = ""
  has_value_ = 0
  value_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def key(self): return self.key_

  def set_key(self, x):
    self.has_key_ = 1
    self.key_ = x

  def clear_key(self):
    if self.has_key_:
      self.has_key_ = 0
      self.key_ = ""

  def has_key(self): return self.has_key_

  def value(self): return self.value_

  def set_value(self, x):
    self.has_value_ = 1
    self.value_ = x

  def clear_value(self):
    if self.has_value_:
      self.has_value_ = 0
      self.value_ = ""

  def has_value(self): return self.has_value_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_key()): self.set_key(x.key())
    if (x.has_value()): self.set_value(x.value())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.AppendKeyValueRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.AppendKeyValueRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.AppendKeyValueRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.AppendKeyValueRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.AppendKeyValueRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.AppendKeyValueRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_key_ != x.has_key_: return 0
    if self.has_key_ and self.key_ != x.key_: return 0
    if self.has_value_ != x.has_value_: return 0
    if self.has_value_ and self.value_ != x.value_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    if (not self.has_key_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: key not set.')
    if (not self.has_value_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: value not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    n += self.lengthString(len(self.key_))
    n += self.lengthString(len(self.value_))
    return n + 3

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_key_):
      n += 1
      n += self.lengthString(len(self.key_))
    if (self.has_value_):
      n += 1
      n += self.lengthString(len(self.value_))
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_key()
    self.clear_value()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    out.putVarInt32(18)
    out.putPrefixedString(self.key_)
    out.putVarInt32(26)
    out.putPrefixedString(self.value_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_key_):
      out.putVarInt32(18)
      out.putPrefixedString(self.key_)
    if (self.has_value_):
      out.putVarInt32(26)
      out.putPrefixedString(self.value_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_key(d.getPrefixedString())
        continue
      if tt == 26:
        self.set_value(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_key_: res+=prefix+("key: %s\n" % self.DebugFormatString(self.key_))
    if self.has_value_: res+=prefix+("value: %s\n" % self.DebugFormatString(self.value_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kkey = 2
  kvalue = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "key",
    3: "value",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.STRING,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KJmFwcGhvc3RpbmcuZmlsZXMuQXBwZW5kS2V5VmFsdWVSZXF1ZXN0ExoIZmlsZW5hbWUgASgCMAk4AhQTGgNrZXkgAigCMAk4AqMBqgEFY3R5cGWyAQRDb3JkpAEUExoFdmFsdWUgAygCMAk4AqMBqgEFY3R5cGWyAQRDb3JkpAEUwgEiYXBwaG9zdGluZy5maWxlcy5GaWxlU2VydmljZUVycm9ycw=="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class AppendKeyValueResponse(ProtocolBuffer.ProtocolMessage):

  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.AppendKeyValueResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.AppendKeyValueResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.AppendKeyValueResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.AppendKeyValueResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.AppendKeyValueResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.AppendKeyValueResponse', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KJ2FwcGhvc3RpbmcuZmlsZXMuQXBwZW5kS2V5VmFsdWVSZXNwb25zZcIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class DeleteRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.DeleteRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.DeleteRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.DeleteRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.DeleteRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.DeleteRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.DeleteRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    return n + 1

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    return n

  def Clear(self):
    self.clear_filename()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHmFwcGhvc3RpbmcuZmlsZXMuRGVsZXRlUmVxdWVzdBMaCGZpbGVuYW1lIAEoAjAJOAIUwgEiYXBwaG9zdGluZy5maWxlcy5GaWxlU2VydmljZUVycm9ycw=="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class DeleteResponse(ProtocolBuffer.ProtocolMessage):

  def __init__(self, contents=None):
    pass
    if contents is not None: self.MergeFromString(contents)


  def MergeFrom(self, x):
    assert x is not self

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.DeleteResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.DeleteResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.DeleteResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.DeleteResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.DeleteResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.DeleteResponse', s)


  def Equals(self, x):
    if x is self: return 1
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    return initialized

  def ByteSize(self):
    n = 0
    return n

  def ByteSizePartial(self):
    n = 0
    return n

  def Clear(self):
    pass

  def OutputUnchecked(self, out):
    pass

  def OutputPartial(self, out):
    pass

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])


  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
  }, 0)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
  }, 0, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KH2FwcGhvc3RpbmcuZmlsZXMuRGVsZXRlUmVzcG9uc2XCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3Jz"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class ReadRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_pos_ = 0
  pos_ = 0
  has_max_bytes_ = 0
  max_bytes_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def pos(self): return self.pos_

  def set_pos(self, x):
    self.has_pos_ = 1
    self.pos_ = x

  def clear_pos(self):
    if self.has_pos_:
      self.has_pos_ = 0
      self.pos_ = 0

  def has_pos(self): return self.has_pos_

  def max_bytes(self): return self.max_bytes_

  def set_max_bytes(self, x):
    self.has_max_bytes_ = 1
    self.max_bytes_ = x

  def clear_max_bytes(self):
    if self.has_max_bytes_:
      self.has_max_bytes_ = 0
      self.max_bytes_ = 0

  def has_max_bytes(self): return self.has_max_bytes_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_pos()): self.set_pos(x.pos())
    if (x.has_max_bytes()): self.set_max_bytes(x.max_bytes())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.ReadRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.ReadRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.ReadRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.ReadRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.ReadRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.ReadRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_pos_ != x.has_pos_: return 0
    if self.has_pos_ and self.pos_ != x.pos_: return 0
    if self.has_max_bytes_ != x.has_max_bytes_: return 0
    if self.has_max_bytes_ and self.max_bytes_ != x.max_bytes_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    if (not self.has_pos_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: pos not set.')
    if (not self.has_max_bytes_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: max_bytes not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    n += self.lengthVarInt64(self.pos_)
    n += self.lengthVarInt64(self.max_bytes_)
    return n + 3

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_pos_):
      n += 1
      n += self.lengthVarInt64(self.pos_)
    if (self.has_max_bytes_):
      n += 1
      n += self.lengthVarInt64(self.max_bytes_)
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_pos()
    self.clear_max_bytes()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    out.putVarInt32(16)
    out.putVarInt64(self.pos_)
    out.putVarInt32(24)
    out.putVarInt64(self.max_bytes_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_pos_):
      out.putVarInt32(16)
      out.putVarInt64(self.pos_)
    if (self.has_max_bytes_):
      out.putVarInt32(24)
      out.putVarInt64(self.max_bytes_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 16:
        self.set_pos(d.getVarInt64())
        continue
      if tt == 24:
        self.set_max_bytes(d.getVarInt64())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_pos_: res+=prefix+("pos: %s\n" % self.DebugFormatInt64(self.pos_))
    if self.has_max_bytes_: res+=prefix+("max_bytes: %s\n" % self.DebugFormatInt64(self.max_bytes_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kpos = 2
  kmax_bytes = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "pos",
    3: "max_bytes",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.NUMERIC,
    3: ProtocolBuffer.Encoder.NUMERIC,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHGFwcGhvc3RpbmcuZmlsZXMuUmVhZFJlcXVlc3QTGghmaWxlbmFtZSABKAIwCTgCFBMaA3BvcyACKAAwAzgCFBMaCW1heF9ieXRlcyADKAAwAzgCFMIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class ReadResponse(ProtocolBuffer.ProtocolMessage):
  has_data_ = 0
  data_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def data(self): return self.data_

  def set_data(self, x):
    self.has_data_ = 1
    self.data_ = x

  def clear_data(self):
    if self.has_data_:
      self.has_data_ = 0
      self.data_ = ""

  def has_data(self): return self.has_data_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_data()): self.set_data(x.data())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.ReadResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.ReadResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.ReadResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.ReadResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.ReadResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.ReadResponse', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_data_ != x.has_data_: return 0
    if self.has_data_ and self.data_ != x.data_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_data_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: data not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.data_))
    return n + 1

  def ByteSizePartial(self):
    n = 0
    if (self.has_data_):
      n += 1
      n += self.lengthString(len(self.data_))
    return n

  def Clear(self):
    self.clear_data()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.data_)

  def OutputPartial(self, out):
    if (self.has_data_):
      out.putVarInt32(10)
      out.putPrefixedString(self.data_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_data(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_data_: res+=prefix+("data: %s\n" % self.DebugFormatString(self.data_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kdata = 1

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "data",
  }, 1)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
  }, 1, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KHWFwcGhvc3RpbmcuZmlsZXMuUmVhZFJlc3BvbnNlExoEZGF0YSABKAIwCTgCowGqAQVjdHlwZbIBBENvcmSkARTCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3Jz"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class ReadKeyValueRequest(ProtocolBuffer.ProtocolMessage):
  has_filename_ = 0
  filename_ = ""
  has_start_key_ = 0
  start_key_ = ""
  has_max_bytes_ = 0
  max_bytes_ = 0
  has_value_pos_ = 0
  value_pos_ = 0

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def filename(self): return self.filename_

  def set_filename(self, x):
    self.has_filename_ = 1
    self.filename_ = x

  def clear_filename(self):
    if self.has_filename_:
      self.has_filename_ = 0
      self.filename_ = ""

  def has_filename(self): return self.has_filename_

  def start_key(self): return self.start_key_

  def set_start_key(self, x):
    self.has_start_key_ = 1
    self.start_key_ = x

  def clear_start_key(self):
    if self.has_start_key_:
      self.has_start_key_ = 0
      self.start_key_ = ""

  def has_start_key(self): return self.has_start_key_

  def max_bytes(self): return self.max_bytes_

  def set_max_bytes(self, x):
    self.has_max_bytes_ = 1
    self.max_bytes_ = x

  def clear_max_bytes(self):
    if self.has_max_bytes_:
      self.has_max_bytes_ = 0
      self.max_bytes_ = 0

  def has_max_bytes(self): return self.has_max_bytes_

  def value_pos(self): return self.value_pos_

  def set_value_pos(self, x):
    self.has_value_pos_ = 1
    self.value_pos_ = x

  def clear_value_pos(self):
    if self.has_value_pos_:
      self.has_value_pos_ = 0
      self.value_pos_ = 0

  def has_value_pos(self): return self.has_value_pos_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_filename()): self.set_filename(x.filename())
    if (x.has_start_key()): self.set_start_key(x.start_key())
    if (x.has_max_bytes()): self.set_max_bytes(x.max_bytes())
    if (x.has_value_pos()): self.set_value_pos(x.value_pos())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.ReadKeyValueRequest', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.ReadKeyValueRequest')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.ReadKeyValueRequest')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.ReadKeyValueRequest', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.ReadKeyValueRequest', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.ReadKeyValueRequest', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_filename_ != x.has_filename_: return 0
    if self.has_filename_ and self.filename_ != x.filename_: return 0
    if self.has_start_key_ != x.has_start_key_: return 0
    if self.has_start_key_ and self.start_key_ != x.start_key_: return 0
    if self.has_max_bytes_ != x.has_max_bytes_: return 0
    if self.has_max_bytes_ and self.max_bytes_ != x.max_bytes_: return 0
    if self.has_value_pos_ != x.has_value_pos_: return 0
    if self.has_value_pos_ and self.value_pos_ != x.value_pos_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_filename_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: filename not set.')
    if (not self.has_start_key_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: start_key not set.')
    if (not self.has_max_bytes_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: max_bytes not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.filename_))
    n += self.lengthString(len(self.start_key_))
    n += self.lengthVarInt64(self.max_bytes_)
    if (self.has_value_pos_): n += 1 + self.lengthVarInt64(self.value_pos_)
    return n + 3

  def ByteSizePartial(self):
    n = 0
    if (self.has_filename_):
      n += 1
      n += self.lengthString(len(self.filename_))
    if (self.has_start_key_):
      n += 1
      n += self.lengthString(len(self.start_key_))
    if (self.has_max_bytes_):
      n += 1
      n += self.lengthVarInt64(self.max_bytes_)
    if (self.has_value_pos_): n += 1 + self.lengthVarInt64(self.value_pos_)
    return n

  def Clear(self):
    self.clear_filename()
    self.clear_start_key()
    self.clear_max_bytes()
    self.clear_value_pos()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.filename_)
    out.putVarInt32(18)
    out.putPrefixedString(self.start_key_)
    out.putVarInt32(24)
    out.putVarInt64(self.max_bytes_)
    if (self.has_value_pos_):
      out.putVarInt32(32)
      out.putVarInt64(self.value_pos_)

  def OutputPartial(self, out):
    if (self.has_filename_):
      out.putVarInt32(10)
      out.putPrefixedString(self.filename_)
    if (self.has_start_key_):
      out.putVarInt32(18)
      out.putPrefixedString(self.start_key_)
    if (self.has_max_bytes_):
      out.putVarInt32(24)
      out.putVarInt64(self.max_bytes_)
    if (self.has_value_pos_):
      out.putVarInt32(32)
      out.putVarInt64(self.value_pos_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_filename(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_start_key(d.getPrefixedString())
        continue
      if tt == 24:
        self.set_max_bytes(d.getVarInt64())
        continue
      if tt == 32:
        self.set_value_pos(d.getVarInt64())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_filename_: res+=prefix+("filename: %s\n" % self.DebugFormatString(self.filename_))
    if self.has_start_key_: res+=prefix+("start_key: %s\n" % self.DebugFormatString(self.start_key_))
    if self.has_max_bytes_: res+=prefix+("max_bytes: %s\n" % self.DebugFormatInt64(self.max_bytes_))
    if self.has_value_pos_: res+=prefix+("value_pos: %s\n" % self.DebugFormatInt64(self.value_pos_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kfilename = 1
  kstart_key = 2
  kmax_bytes = 3
  kvalue_pos = 4

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "filename",
    2: "start_key",
    3: "max_bytes",
    4: "value_pos",
  }, 4)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.NUMERIC,
    4: ProtocolBuffer.Encoder.NUMERIC,
  }, 4, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KJGFwcGhvc3RpbmcuZmlsZXMuUmVhZEtleVZhbHVlUmVxdWVzdBMaCGZpbGVuYW1lIAEoAjAJOAIUExoJc3RhcnRfa2V5IAIoAjAJOAKjAaoBBWN0eXBlsgEEQ29yZKQBFBMaCW1heF9ieXRlcyADKAAwAzgCFBMaCXZhbHVlX3BvcyAEKAAwAzgBFMIBImFwcGhvc3RpbmcuZmlsZXMuRmlsZVNlcnZpY2VFcnJvcnM="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class ReadKeyValueResponse_KeyValue(ProtocolBuffer.ProtocolMessage):
  has_key_ = 0
  key_ = ""
  has_value_ = 0
  value_ = ""

  def __init__(self, contents=None):
    if contents is not None: self.MergeFromString(contents)

  def key(self): return self.key_

  def set_key(self, x):
    self.has_key_ = 1
    self.key_ = x

  def clear_key(self):
    if self.has_key_:
      self.has_key_ = 0
      self.key_ = ""

  def has_key(self): return self.has_key_

  def value(self): return self.value_

  def set_value(self, x):
    self.has_value_ = 1
    self.value_ = x

  def clear_value(self):
    if self.has_value_:
      self.has_value_ = 0
      self.value_ = ""

  def has_value(self): return self.has_value_


  def MergeFrom(self, x):
    assert x is not self
    if (x.has_key()): self.set_key(x.key())
    if (x.has_value()): self.set_value(x.value())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.ReadKeyValueResponse_KeyValue', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.ReadKeyValueResponse_KeyValue')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.ReadKeyValueResponse_KeyValue')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.ReadKeyValueResponse_KeyValue', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.ReadKeyValueResponse_KeyValue', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.ReadKeyValueResponse_KeyValue', s)


  def Equals(self, x):
    if x is self: return 1
    if self.has_key_ != x.has_key_: return 0
    if self.has_key_ and self.key_ != x.key_: return 0
    if self.has_value_ != x.has_value_: return 0
    if self.has_value_ and self.value_ != x.value_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    if (not self.has_key_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: key not set.')
    if (not self.has_value_):
      initialized = 0
      if debug_strs is not None:
        debug_strs.append('Required field: value not set.')
    return initialized

  def ByteSize(self):
    n = 0
    n += self.lengthString(len(self.key_))
    n += self.lengthString(len(self.value_))
    return n + 2

  def ByteSizePartial(self):
    n = 0
    if (self.has_key_):
      n += 1
      n += self.lengthString(len(self.key_))
    if (self.has_value_):
      n += 1
      n += self.lengthString(len(self.value_))
    return n

  def Clear(self):
    self.clear_key()
    self.clear_value()

  def OutputUnchecked(self, out):
    out.putVarInt32(10)
    out.putPrefixedString(self.key_)
    out.putVarInt32(18)
    out.putPrefixedString(self.value_)

  def OutputPartial(self, out):
    if (self.has_key_):
      out.putVarInt32(10)
      out.putPrefixedString(self.key_)
    if (self.has_value_):
      out.putVarInt32(18)
      out.putPrefixedString(self.value_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        self.set_key(d.getPrefixedString())
        continue
      if tt == 18:
        self.set_value(d.getPrefixedString())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    if self.has_key_: res+=prefix+("key: %s\n" % self.DebugFormatString(self.key_))
    if self.has_value_: res+=prefix+("value: %s\n" % self.DebugFormatString(self.value_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kkey = 1
  kvalue = 2

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "key",
    2: "value",
  }, 2)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
  }, 2, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KLmFwcGhvc3RpbmcuZmlsZXMuUmVhZEtleVZhbHVlUmVzcG9uc2VfS2V5VmFsdWUTGgNrZXkgASgCMAk4AqMBqgEFY3R5cGWyAQRDb3JkpAEUExoFdmFsdWUgAigCMAk4AqMBqgEFY3R5cGWyAQRDb3JkpAEUwgEiYXBwaG9zdGluZy5maWxlcy5GaWxlU2VydmljZUVycm9yc8oBLmFwcGhvc3RpbmcuZmlsZXMuUmVhZEtleVZhbHVlUmVzcG9uc2UuS2V5VmFsdWU="))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())

class ReadKeyValueResponse(ProtocolBuffer.ProtocolMessage):
  has_next_key_ = 0
  next_key_ = ""
  has_truncated_value_ = 0
  truncated_value_ = 0

  def __init__(self, contents=None):
    self.data_ = []
    if contents is not None: self.MergeFromString(contents)

  def data_size(self): return len(self.data_)
  def data_list(self): return self.data_

  def data(self, i):
    return self.data_[i]

  def mutable_data(self, i):
    return self.data_[i]

  def add_data(self):
    x = ReadKeyValueResponse_KeyValue()
    self.data_.append(x)
    return x

  def clear_data(self):
    self.data_ = []
  def next_key(self): return self.next_key_

  def set_next_key(self, x):
    self.has_next_key_ = 1
    self.next_key_ = x

  def clear_next_key(self):
    if self.has_next_key_:
      self.has_next_key_ = 0
      self.next_key_ = ""

  def has_next_key(self): return self.has_next_key_

  def truncated_value(self): return self.truncated_value_

  def set_truncated_value(self, x):
    self.has_truncated_value_ = 1
    self.truncated_value_ = x

  def clear_truncated_value(self):
    if self.has_truncated_value_:
      self.has_truncated_value_ = 0
      self.truncated_value_ = 0

  def has_truncated_value(self): return self.has_truncated_value_


  def MergeFrom(self, x):
    assert x is not self
    for i in xrange(x.data_size()): self.add_data().CopyFrom(x.data(i))
    if (x.has_next_key()): self.set_next_key(x.next_key())
    if (x.has_truncated_value()): self.set_truncated_value(x.truncated_value())

  if _net_proto___parse__python is not None:
    def _CMergeFromString(self, s):
      _net_proto___parse__python.MergeFromString(self, 'apphosting.files.ReadKeyValueResponse', s)

  if _net_proto___parse__python is not None:
    def _CEncode(self):
      return _net_proto___parse__python.Encode(self, 'apphosting.files.ReadKeyValueResponse')

  if _net_proto___parse__python is not None:
    def _CEncodePartial(self):
      return _net_proto___parse__python.EncodePartial(self, 'apphosting.files.ReadKeyValueResponse')

  if _net_proto___parse__python is not None:
    def _CToASCII(self, output_format):
      return _net_proto___parse__python.ToASCII(self, 'apphosting.files.ReadKeyValueResponse', output_format)


  if _net_proto___parse__python is not None:
    def ParseASCII(self, s):
      _net_proto___parse__python.ParseASCII(self, 'apphosting.files.ReadKeyValueResponse', s)


  if _net_proto___parse__python is not None:
    def ParseASCIIIgnoreUnknown(self, s):
      _net_proto___parse__python.ParseASCIIIgnoreUnknown(self, 'apphosting.files.ReadKeyValueResponse', s)


  def Equals(self, x):
    if x is self: return 1
    if len(self.data_) != len(x.data_): return 0
    for e1, e2 in zip(self.data_, x.data_):
      if e1 != e2: return 0
    if self.has_next_key_ != x.has_next_key_: return 0
    if self.has_next_key_ and self.next_key_ != x.next_key_: return 0
    if self.has_truncated_value_ != x.has_truncated_value_: return 0
    if self.has_truncated_value_ and self.truncated_value_ != x.truncated_value_: return 0
    return 1

  def IsInitialized(self, debug_strs=None):
    initialized = 1
    for p in self.data_:
      if not p.IsInitialized(debug_strs): initialized=0
    return initialized

  def ByteSize(self):
    n = 0
    n += 1 * len(self.data_)
    for i in xrange(len(self.data_)): n += self.lengthString(self.data_[i].ByteSize())
    if (self.has_next_key_): n += 1 + self.lengthString(len(self.next_key_))
    if (self.has_truncated_value_): n += 2
    return n

  def ByteSizePartial(self):
    n = 0
    n += 1 * len(self.data_)
    for i in xrange(len(self.data_)): n += self.lengthString(self.data_[i].ByteSizePartial())
    if (self.has_next_key_): n += 1 + self.lengthString(len(self.next_key_))
    if (self.has_truncated_value_): n += 2
    return n

  def Clear(self):
    self.clear_data()
    self.clear_next_key()
    self.clear_truncated_value()

  def OutputUnchecked(self, out):
    for i in xrange(len(self.data_)):
      out.putVarInt32(10)
      out.putVarInt32(self.data_[i].ByteSize())
      self.data_[i].OutputUnchecked(out)
    if (self.has_next_key_):
      out.putVarInt32(18)
      out.putPrefixedString(self.next_key_)
    if (self.has_truncated_value_):
      out.putVarInt32(24)
      out.putBoolean(self.truncated_value_)

  def OutputPartial(self, out):
    for i in xrange(len(self.data_)):
      out.putVarInt32(10)
      out.putVarInt32(self.data_[i].ByteSizePartial())
      self.data_[i].OutputPartial(out)
    if (self.has_next_key_):
      out.putVarInt32(18)
      out.putPrefixedString(self.next_key_)
    if (self.has_truncated_value_):
      out.putVarInt32(24)
      out.putBoolean(self.truncated_value_)

  def TryMerge(self, d):
    while d.avail() > 0:
      tt = d.getVarInt32()
      if tt == 10:
        length = d.getVarInt32()
        tmp = ProtocolBuffer.Decoder(d.buffer(), d.pos(), d.pos() + length)
        d.skip(length)
        self.add_data().TryMerge(tmp)
        continue
      if tt == 18:
        self.set_next_key(d.getPrefixedString())
        continue
      if tt == 24:
        self.set_truncated_value(d.getBoolean())
        continue
      if (tt == 0): raise ProtocolBuffer.ProtocolBufferDecodeError
      d.skipData(tt)


  def __str__(self, prefix="", printElemNumber=0):
    res=""
    cnt=0
    for e in self.data_:
      elm=""
      if printElemNumber: elm="(%d)" % cnt
      res+=prefix+("data%s <\n" % elm)
      res+=e.__str__(prefix + "  ", printElemNumber)
      res+=prefix+">\n"
      cnt+=1
    if self.has_next_key_: res+=prefix+("next_key: %s\n" % self.DebugFormatString(self.next_key_))
    if self.has_truncated_value_: res+=prefix+("truncated_value: %s\n" % self.DebugFormatBool(self.truncated_value_))
    return res


  def _BuildTagLookupTable(sparse, maxtag, default=None):
    return tuple([sparse.get(i, default) for i in xrange(0, 1+maxtag)])

  kdata = 1
  knext_key = 2
  ktruncated_value = 3

  _TEXT = _BuildTagLookupTable({
    0: "ErrorCode",
    1: "data",
    2: "next_key",
    3: "truncated_value",
  }, 3)

  _TYPES = _BuildTagLookupTable({
    0: ProtocolBuffer.Encoder.NUMERIC,
    1: ProtocolBuffer.Encoder.STRING,
    2: ProtocolBuffer.Encoder.STRING,
    3: ProtocolBuffer.Encoder.NUMERIC,
  }, 3, ProtocolBuffer.Encoder.MAX_TYPE)

  _STYLE = """"""
  _STYLE_CONTENT_TYPE = """"""
  _SERIALIZED_DESCRIPTOR = array.array('B')
  _SERIALIZED_DESCRIPTOR.fromstring(base64.decodestring("WidhcHBob3N0aW5nL2FwaS9maWxlcy9maWxlX3NlcnZpY2UucHJvdG8KJWFwcGhvc3RpbmcuZmlsZXMuUmVhZEtleVZhbHVlUmVzcG9uc2UTGgRkYXRhIAEoAjALOANKLmFwcGhvc3RpbmcuZmlsZXMuUmVhZEtleVZhbHVlUmVzcG9uc2VfS2V5VmFsdWUUExoIbmV4dF9rZXkgAigCMAk4ARQTGg90cnVuY2F0ZWRfdmFsdWUgAygAMAg4ARTCASJhcHBob3N0aW5nLmZpbGVzLkZpbGVTZXJ2aWNlRXJyb3Jz"))
  if _net_proto___parse__python is not None:
    _net_proto___parse__python.RegisterType(
        _SERIALIZED_DESCRIPTOR.tostring())



class _FileService_ClientBaseStub(_client_stub_base_class):
  """Makes Stubby RPC calls to a FileService server."""

  __slots__ = (
      '_protorpc_Open', '_full_name_Open',
      '_protorpc_Close', '_full_name_Close',
      '_protorpc_Append', '_full_name_Append',
      '_protorpc_AppendKeyValue', '_full_name_AppendKeyValue',
      '_protorpc_Stat', '_full_name_Stat',
      '_protorpc_Delete', '_full_name_Delete',
      '_protorpc_Read', '_full_name_Read',
      '_protorpc_ReadKeyValue', '_full_name_ReadKeyValue',
  )

  def __init__(self, rpc_stub):
    self._stub = rpc_stub

    self._protorpc_Open = pywraprpc.RPC()
    self._full_name_Open = self._stub.GetFullMethodName(
        'Open')

    self._protorpc_Close = pywraprpc.RPC()
    self._full_name_Close = self._stub.GetFullMethodName(
        'Close')

    self._protorpc_Append = pywraprpc.RPC()
    self._full_name_Append = self._stub.GetFullMethodName(
        'Append')

    self._protorpc_AppendKeyValue = pywraprpc.RPC()
    self._full_name_AppendKeyValue = self._stub.GetFullMethodName(
        'AppendKeyValue')

    self._protorpc_Stat = pywraprpc.RPC()
    self._full_name_Stat = self._stub.GetFullMethodName(
        'Stat')

    self._protorpc_Delete = pywraprpc.RPC()
    self._full_name_Delete = self._stub.GetFullMethodName(
        'Delete')

    self._protorpc_Read = pywraprpc.RPC()
    self._full_name_Read = self._stub.GetFullMethodName(
        'Read')

    self._protorpc_ReadKeyValue = pywraprpc.RPC()
    self._full_name_ReadKeyValue = self._stub.GetFullMethodName(
        'ReadKeyValue')

  def Open(self, request, rpc=None, callback=None, response=None):
    """Make a Open RPC call.

    Args:
      request: a OpenRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The OpenResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = OpenResponse
    return self._MakeCall(rpc,
                          self._full_name_Open,
                          'Open',
                          request,
                          response,
                          callback,
                          self._protorpc_Open)

  def Close(self, request, rpc=None, callback=None, response=None):
    """Make a Close RPC call.

    Args:
      request: a CloseRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The CloseResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = CloseResponse
    return self._MakeCall(rpc,
                          self._full_name_Close,
                          'Close',
                          request,
                          response,
                          callback,
                          self._protorpc_Close)

  def Append(self, request, rpc=None, callback=None, response=None):
    """Make a Append RPC call.

    Args:
      request: a AppendRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The AppendResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = AppendResponse
    return self._MakeCall(rpc,
                          self._full_name_Append,
                          'Append',
                          request,
                          response,
                          callback,
                          self._protorpc_Append)

  def AppendKeyValue(self, request, rpc=None, callback=None, response=None):
    """Make a AppendKeyValue RPC call.

    Args:
      request: a AppendKeyValueRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The AppendKeyValueResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = AppendKeyValueResponse
    return self._MakeCall(rpc,
                          self._full_name_AppendKeyValue,
                          'AppendKeyValue',
                          request,
                          response,
                          callback,
                          self._protorpc_AppendKeyValue)

  def Stat(self, request, rpc=None, callback=None, response=None):
    """Make a Stat RPC call.

    Args:
      request: a StatRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The StatResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = StatResponse
    return self._MakeCall(rpc,
                          self._full_name_Stat,
                          'Stat',
                          request,
                          response,
                          callback,
                          self._protorpc_Stat)

  def Delete(self, request, rpc=None, callback=None, response=None):
    """Make a Delete RPC call.

    Args:
      request: a DeleteRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The DeleteResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = DeleteResponse
    return self._MakeCall(rpc,
                          self._full_name_Delete,
                          'Delete',
                          request,
                          response,
                          callback,
                          self._protorpc_Delete)

  def Read(self, request, rpc=None, callback=None, response=None):
    """Make a Read RPC call.

    Args:
      request: a ReadRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The ReadResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = ReadResponse
    return self._MakeCall(rpc,
                          self._full_name_Read,
                          'Read',
                          request,
                          response,
                          callback,
                          self._protorpc_Read)

  def ReadKeyValue(self, request, rpc=None, callback=None, response=None):
    """Make a ReadKeyValue RPC call.

    Args:
      request: a ReadKeyValueRequest instance.
      rpc: Optional RPC instance to use for the call.
      callback: Optional final callback. Will be called as
          callback(rpc, result) when the rpc completes. If None, the
          call is synchronous.
      response: Optional ProtocolMessage to be filled in with response.

    Returns:
      The ReadKeyValueResponse if callback is None. Otherwise, returns None.
    """

    if response is None:
      response = ReadKeyValueResponse
    return self._MakeCall(rpc,
                          self._full_name_ReadKeyValue,
                          'ReadKeyValue',
                          request,
                          response,
                          callback,
                          self._protorpc_ReadKeyValue)


class _FileService_ClientStub(_FileService_ClientBaseStub):
  def __init__(self, rpc_stub_parameters, service_name):
    if service_name is None:
      service_name = 'FileService'
    _FileService_ClientBaseStub.__init__(self, pywraprpc.RPC_GenericStub(service_name, rpc_stub_parameters))
    self._params = rpc_stub_parameters


class _FileService_RPC2ClientStub(_FileService_ClientBaseStub):
  def __init__(self, server, channel, service_name):
    if service_name is None:
      service_name = 'FileService'
    if channel is not None:
      if channel.version() == 1:
        raise RuntimeError('Expecting an RPC2 channel to create the stub')
      _FileService_ClientBaseStub.__init__(self, pywraprpc.RPC_GenericStub(service_name, channel))
    elif server is not None:
      _FileService_ClientBaseStub.__init__(self, pywraprpc.RPC_GenericStub(service_name, pywraprpc.NewClientChannel(server)))
    else:
      raise RuntimeError('Invalid argument combination to create a stub')


class FileService(_server_stub_base_class):
  """Base class for FileService Stubby servers."""

  def __init__(self, *args, **kwargs):
    """Creates a Stubby RPC server.

    See BaseRpcServer.__init__ in rpcserver.py for detail on arguments.
    """
    if _server_stub_base_class is object:
      raise NotImplementedError('Add //net/rpc/python:rpcserver as a '
                                'dependency for Stubby server support.')
    _server_stub_base_class.__init__(self, 'apphosting.files.FileService', *args, **kwargs)

  @staticmethod
  def NewStub(rpc_stub_parameters, service_name=None):
    """Creates a new FileService Stubby client stub.

    Args:
      rpc_stub_parameters: an RPC_StubParameter instance.
      service_name: the service name used by the Stubby server.
    """

    if _client_stub_base_class is object:
      raise RuntimeError('Add //net/rpc/python as a dependency to use Stubby')
    return _FileService_ClientStub(rpc_stub_parameters, service_name)

  @staticmethod
  def NewRPC2Stub(server=None, channel=None, service_name=None):
    """Creates a new FileService Stubby2 client stub.

    Args:
      server: host:port or bns address.
      channel: directly use a channel to create a stub. Will ignore server
          argument if this is specified.
      service_name: the service name used by the Stubby server.
    """

    if _client_stub_base_class is object:
      raise RuntimeError('Add //net/rpc/python as a dependency to use Stubby')
    return _FileService_RPC2ClientStub(server, channel, service_name)

  def Open(self, rpc, request, response):
    """Handles a Open RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a OpenRequest that contains the client request
      response: a OpenResponse that should be modified to send the response
    """
    raise NotImplementedError


  def Close(self, rpc, request, response):
    """Handles a Close RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a CloseRequest that contains the client request
      response: a CloseResponse that should be modified to send the response
    """
    raise NotImplementedError


  def Append(self, rpc, request, response):
    """Handles a Append RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a AppendRequest that contains the client request
      response: a AppendResponse that should be modified to send the response
    """
    raise NotImplementedError


  def AppendKeyValue(self, rpc, request, response):
    """Handles a AppendKeyValue RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a AppendKeyValueRequest that contains the client request
      response: a AppendKeyValueResponse that should be modified to send the response
    """
    raise NotImplementedError


  def Stat(self, rpc, request, response):
    """Handles a Stat RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a StatRequest that contains the client request
      response: a StatResponse that should be modified to send the response
    """
    raise NotImplementedError


  def Delete(self, rpc, request, response):
    """Handles a Delete RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a DeleteRequest that contains the client request
      response: a DeleteResponse that should be modified to send the response
    """
    raise NotImplementedError


  def Read(self, rpc, request, response):
    """Handles a Read RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a ReadRequest that contains the client request
      response: a ReadResponse that should be modified to send the response
    """
    raise NotImplementedError


  def ReadKeyValue(self, rpc, request, response):
    """Handles a ReadKeyValue RPC call. You should override this.

    Args:
      rpc: a Stubby RPC object
      request: a ReadKeyValueRequest that contains the client request
      response: a ReadKeyValueResponse that should be modified to send the response
    """
    raise NotImplementedError

  def _AddMethodAttributes(self):
    """Sets attributes on Python RPC handlers.

    See BaseRpcServer in rpcserver.py for details.
    """
    rpcserver._GetHandlerDecorator(
        self.Open.im_func,
        OpenRequest,
        OpenResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.Close.im_func,
        CloseRequest,
        CloseResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.Append.im_func,
        AppendRequest,
        AppendResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.AppendKeyValue.im_func,
        AppendKeyValueRequest,
        AppendKeyValueResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.Stat.im_func,
        StatRequest,
        StatResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.Delete.im_func,
        DeleteRequest,
        DeleteResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.Read.im_func,
        ReadRequest,
        ReadResponse,
        None,
        'none')
    rpcserver._GetHandlerDecorator(
        self.ReadKeyValue.im_func,
        ReadKeyValueRequest,
        ReadKeyValueResponse,
        None,
        'none')


__all__ = ['FileServiceErrors','FileContentType','OpenRequest_CreateOptions','OpenRequest','OpenResponse','CloseRequest','CloseResponse','FileStat','StatRequest','StatResponse','AppendRequest','AppendResponse','AppendKeyValueRequest','AppendKeyValueResponse','DeleteRequest','DeleteResponse','ReadRequest','ReadResponse','ReadKeyValueRequest','ReadKeyValueResponse_KeyValue','ReadKeyValueResponse','FileService']
