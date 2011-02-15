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

"""Module containing the boiler plate required to construct GSoC views.
"""

__authors__ = [
  '"Madhusudan.C.S" <madhusudancs@gmail.com>',
  '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from soc.views.base import RequestHandler

from soc.modules.gsoc.views.helper.request_data import RequestData


class RequestHandler(RequestHandler):
  """Customization required by GSoC to handle HTTP requests.
  """

  def __call__(self, request, *args, **kwargs):
    """See soc.views.base.RequestHandler.__call__()
    """

    self.data = RequestData()
    self.data.populate(request, *args, **kwargs)

    return super(RequestHandler, self).__call__(request, *args, **kwargs)
