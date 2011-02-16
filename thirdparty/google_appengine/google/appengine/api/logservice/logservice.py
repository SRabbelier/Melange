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

"""
LogService API.

This module allows apps to flush logs and provide status messages.
"""


import sys

from google.appengine.api import api_base_pb
from google.appengine.api import apiproxy_stub_map
from google.appengine.api.logservice import log_service_pb
from google.appengine.runtime import apiproxy_errors

def Flush():
  """Flushes logs that have been generated via normal python logging."""
  request = log_service_pb.FlushRequest()
  response = api_base_pb.VoidProto()
  apiproxy_stub_map.MakeSyncCall('logservice', 'Flush', request, response)
  sys.stderr.truncate(0)

def SetStatus(status):
  """Indicates the process status."""
  request = log_service_pb.SetStatusRequest()
  request.status = status
  response = api_base_pb.VoidProto()
  apiproxy_stub_map.MakeSyncCall('logservice', 'SetStatus', request, response)
