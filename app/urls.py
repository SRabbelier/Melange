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
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
  ]


from django.conf.urls.defaults import *


urlpatterns = patterns(
    '',
    (r'^$', 'soc.views.site.home.public'),

    # attempt to send User to their dashboard
    # (will display soc.views.user.roles.public() if "linkname" is not
    # current logged-in User)    
    (r'^user/roles/(?P<linkname>[_0-9a-z]+)$',
     'soc.views.user.roles.dashboard'),

    (r'^user/profile$', 'soc.views.user.profile.edit'),
    (r'^user/profile/(?P<linkname>[_0-9a-z]+)$',
     'soc.views.user.profile.edit'),

    (r'^org/profile/(?P<program>ghop[_0-9a-z]+)/(?P<linkname>[_0-9a-z]+)/$',
     'soc.views.person.profile.edit',
     {'template': 'ghop/person/profile/edit.html'}),
    (r'^org/profile/(?P<program>[_0-9a-z]+)/(?P<linkname>[_0-9a-z]+)/$',
     'soc.views.person.profile.edit'),
)
