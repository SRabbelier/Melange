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

"""Views relevant to the Person role.
"""

__authors__ = [
  '"Augie Fackler" <durin42@gmail.com>',
  ]


from google.appengine.api import users
from google.appengine.ext.db import djangoforms
from django import http
from django import shortcuts
from django import newforms as forms

from soc.models import person


class ProfileForm(djangoforms.ModelForm):
  class Meta:
    """Inner Meta class that defines some behavior for the form.

    """
    #: the db.Model subclass for which the form will gather information.
    model = person.Person
    #: the list of model fields which will *not* be gathered by the form.
    exclude = ['user', ]


def profile(request, template='soc/person/profile.html'):
  """View for a Person to modify the properties of a PersonModel.

  Args:
    request: the standard django request object.
    template: the template path to use for rendering the template.

  Returns:
    A subclass of django.http.HttpResponse which either contains the form to
    be filled out, or a redirect to the correct view in the interface.
  """
  user = users.get_current_user()
  if not user:
    return http.HttpResponseRedirect(users.create_login_url(request.path))
  form = ProfileForm()
  if request.method=='POST':
    form = ProfileForm(request.POST)
    if not form.errors:
      return http.HttpResponse('This would update the model')
  return shortcuts.render_to_response(
      template, dictionary={'template': template, 'form': form, 'user': user})
