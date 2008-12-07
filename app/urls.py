# Copyright 2008 the Melange authors.
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

__authors__ = [
  '"Augie Fackler" <durin42@gmail.com>',
  '"Todd Larsen" <tlarsen@google.com>',
  '"Lennard de Rijk" <rijk0214@gmail.com>',
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from soc.views.sitemap import build


urlpatterns = build.getPatterns()

# define the error handlers
handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'
