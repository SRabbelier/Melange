#!/usr/bin/python2.5
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

"""Common validation helper functions.
"""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


import re

from google.appengine.api import urlfetch

import feedparser

from soc.logic import path_linkname


def isFeedURLValid(feed_url=None):
  """Returns True if provided url is valid ATOM or RSS.

  Args:
    feed_url: ATOM or RSS feed url
  """
  if feed_url:
    result = urlfetch.fetch(feed_url)
    if result.status_code == 200:
      parsed_feed = feedparser.parse(result.content)
      if parsed_feed.version and (parsed_feed.version != ''):
        return True
  return False


def isLinkNameFormatValid(link_name):
  """Returns True if link_name is in a valid format.

  Args:
    link_name: link name used in URLs for identification
  """
  if path_linkname.LINKNAME_REGEX.match(link_name):
    return True
  return False