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

"""ProspectiveSearch Admin API.

Admin functions (private to this module) for prospective search.

Functions defined in this module:
  list_topics: Lists topics that have subscriptions, for a specified app_id.
"""




from google.appengine.api import apiproxy_stub_map
from google.appengine.api.prospective_search import prospective_search_pb


def list_topics(app_id, max_results, topic_start):
  """List topics, over-riding app_id.

  Args:
    app_id: if not None, use this app_id.
    max_results: maximum number of topics to return.
    topic_start: if not None, start listing topics from this one.
  Returns:
    List of topics (strings), or an empty list if the caller is not an
      administrator and the app_id does not match the app_id of the application.
  """

  request = prospective_search_pb.ListTopicsRequest()
  request.set_max_results(max_results)
  if app_id:
    request.set_app_id(app_id)
  if topic_start:
    request.set_topic_start(topic_start)
  response = prospective_search_pb.ListTopicsResponse()

  resp = apiproxy_stub_map.MakeSyncCall('matcher', 'ListTopics',
                                        request, response)
  if resp is not None:
    response = resp

  topics = []
  for topic in response.topic_list():
    topics.append(topic)
  return topics
