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

from soc.logic import path_linkname


urlpatterns = patterns(
    # Home Page view
    '',
    (r'^$', 'soc.views.site.home.public'),
    
    # Home Page Site views
    (r'^site/home$', 'soc.views.site.home.public'),
    (r'^site/home/edit$', 'soc.views.site.home.edit'),

    # TODO(tlarsen): uncomment these when the view functions are committed
    # attempt to send User to their dashboard
    # (will display soc.views.user.roles.public() if "linkname" is not
    # current logged-in User)    
    # (r'^user/roles$',
    #  'soc.views.user.roles.dashboard'),
    # (r'^user/roles/(?P<linkname>[_0-9a-z]+)$',
    #  'soc.views.user.roles.dashboard'),
    
    # User Profile Site views
    (r'^site/user/lookup$', 'soc.views.site.user.profile.lookup'),
    (r'^site/user/profile$', 'soc.views.site.user.profile.create'),
    (r'^site/user/profile/%s$' % path_linkname.LINKNAME_ARG_PATTERN,
     'soc.views.site.user.profile.edit'),
    (r'^site/user/list$', 'soc.views.site.user.list.all'),

    # Document views
    (r'^docs/show/%s$' % path_linkname.PATH_LINKNAME_ARGS_PATTERN,
     'soc.views.docs.show.public'),
    
    # Document Site views
    (r'^site/docs/edit$', 'soc.views.site.docs.edit.create'),
    (r'^site/docs/edit/%s$' % path_linkname.PATH_LINKNAME_ARGS_PATTERN,
     'soc.views.site.docs.edit.edit'),
    (r'^site/docs/list$', 'soc.views.site.docs.list.all'),
    
    # Sponsor Group public view
    (r'^sponsor/profile/%s' % path_linkname.LINKNAME_ARG_PATTERN,
     'soc.views.sponsor.profile.public'),
    
    # Sponsor Group Site views
    (r'^site/sponsor/profile$', 'soc.views.site.sponsor.profile.edit'),
    (r'^site/sponsor/profile/%s' % path_linkname.LINKNAME_ARG_PATTERN,
     'soc.views.site.sponsor.profile.edit'),
    (r'^site/sponsor/list$', 'soc.views.site.sponsor.list.all'),
    
    # User Profile views
    (r'^user/profile$', 'soc.views.user.profile.edit'),
    (r'^user/profile/%s$' % path_linkname.LINKNAME_ARG_PATTERN,
     'soc.views.user.profile.edit'),

    # these are not really used...
    (r'^org/profile/(?P<program>ghop[_0-9a-z]+)/(?P<linkname>[_0-9a-z]+)/$',
     'soc.views.person.profile.edit',
     {'template': 'ghop/person/profile/edit.html'}),
    (r'^org/profile/(?P<program>[_0-9a-z]+)/(?P<linkname>[_0-9a-z]+)/$',
     'soc.views.person.profile.edit'),
)
