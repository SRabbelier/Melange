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

"""Views for Club App profiles.
"""

__authors__ = [
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    '"Lennard de Rijk" <ljvderijk@gmail.com>',
  ]


from django import forms
from django.utils.translation import ugettext_lazy

from soc.logic import accounts
from soc.logic import cleaning
from soc.logic import dicts
from soc.logic.models import user as user_logic
from soc.models import group_app as group_app_model
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import redirects
from soc.views.models import group_app

import soc.logic.dicts


class View(group_app.View):
  """View methods for the Club Application model.
  """

  def __init__(self, params=None):
    """Defines the fields and methods required for the base View class
    to provide the user with list, public, create, edit and delete views.

    Params:
      params: a dict with params for this View
    """

    rights = {}
    rights['create'] = [access.checkIsUser]
    rights['delete'] = [access.checkIsMyApplication]
    rights['edit'] = [access.checkIsMyApplication]
    rights['list'] = [access.checkIsUser]
    rights['public'] = [access.checkIsMyApplication]
    rights['review'] = [access.checkIsDeveloper]

    new_params = {}

    new_params['rights'] = rights

    new_params['create_template'] = 'soc/models/twoline_edit.html'
    new_params['edit_template'] = 'soc/models/twoline_edit.html'

    new_params['extra_dynaexclude'] = ['applicant', 'backup_admin',
        'reviewed', 'accepted', 'application_completed']
    new_params['create_extra_dynafields'] = {
        'backup_admin_link_id': forms.CharField(
              label=group_app_model.GroupApplication.backup_admin.verbose_name
              ),
        'clean_backup_admin_link_id': cleaning.clean_existing_user('backup_admin_link_id'),
        }

    patterns = [(r'^%(url_name)s/(?P<access_type>review)$',
        'soc.views.models.%(module_name)s.showReviewOverview',
        'Review %(name_plural)s'),
        (r'^%(url_name)s/(?P<access_type>review)/%(lnp)s$',
          'soc.views.models.%(module_name)s.review',
          'Review %(name_short)s')]

    new_params['extra_django_patterns'] = patterns

    new_params['name'] = "Club Application"
    new_params['name_plural'] = "Club Applications"
    new_params['name_short'] = "Club App"
    new_params['url_name'] = "club_app"

    new_params['sidebar_additional'] = [
        ('/%(url_name)s/review' % new_params,
         'Review %(name_plural)s' % new_params, 'review')]

    new_params['review_template'] = 'soc/club_app/review.html'

    params = dicts.merge(params, new_params)

    super(View, self).__init__(params=params)

  def list(self, request, access_type,
           page_name=None, params=None, filter=None):
    """Lists all notifications that the current logged in user has stored.

    for parameters see base.list()
    """

    params = dicts.merge(params, self._params)

    # get the current user
    user_entity = user_logic.logic.getForCurrentAccount()

    is_developer = accounts.isDeveloper(user=user_entity)

    if is_developer:
      filter = {}
    else:
      # only select the applications for this user so construct a filter
      filter = {'applicant': user_entity}

    if is_developer:
      params['list_description'] = ugettext_lazy(
          "An overview all club applications.")
    else:
      params['list_description'] = ugettext_lazy(
          "An overview of your club applications.")

    # use the generic list method with the filter. The access check in this
    # method will trigger an errorResponse when user_entity is None
    return super(View, self).list(request, access_type,
        page_name, params, filter)

  def _editGet(self, request, entity, form):
    """See base.View._editGet().
    """

    form.fields['backup_admin_link_id'].initial = entity.backup_admin.link_id

  def _editPost(self, request, entity, fields):
    """See base.View._editPost().
    """

    fields['backup_admin'] = fields['backup_admin_link_id']

    if not entity:
      fields['applicant'] = user_logic.logic.getForCurrentAccount()

    # the application has either been created or edited so
    # the review status needs to be set accordingly
    fields['reviewed'] = False
    fields['accepted'] = False

  def _public(self, request, entity, context):
    """See base._public().
    """

    context['entity_type_url'] = self._params['url_name']

  def review(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Handles the view containing the review of an application.

    accepted (true or false) in the GET data will mark
    the application accordingly.


    For params see base.View.public().
    """

    params = dicts.merge(params, self._params)

    try:
      access.checkAccess(access_type, request, rights=params['rights'])
    except out_of_band.Error, error:
      return helper.responses.errorResponse(error, request)

    # create default template context for use with any templates
    context = helper.responses.getUniversalContext(request)
    context['page_name'] = page_name
    entity = None

    try:
      key_fields = self._logic.getKeyFieldsFromDict(kwargs)
      entity = self._logic.getIfFields(key_fields)
    except out_of_band.Error, error:
      return helper.responses.errorResponse(
          error, request, template=params['error_public'], context=context)

    get_dict = request.GET

    # check to see if we can make a decision for this application
    if 'accepted' in get_dict.keys():
      accepted_value = get_dict['accepted']

      fields = {'reviewed' : False}

      if accepted_value == 'true':
        # the application has been accepted
        fields['accepted'] = True
        fields['reviewed'] = True
      elif accepted_value == 'false':
        # the application has been denied
        fields['accepted'] = False
        fields['reviewed'] = True

      if fields['reviewed']:
        # the application has either been denied or accepted
        # mark it as reviewed and update accordingly
        application = self._logic.getFromFields(link_id=kwargs['link_id'])
        self._logic.updateModelProperties(application, fields)

        return self.showReviewOverview(request, access_type,
            page_name=page_name, params=params, **kwargs)

    # the application has not been reviewed so show the information
    # using the appropriate review template
    params['public_template'] = params['review_template']

    return super(View, self).public(request, access_type,
        page_name=page_name, params=params, **kwargs)


  def showReviewOverview(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays multiple lists of applications that are in different
    states of the application process.
    """

    params = dicts.merge(params, self._params)

    # only select the requests that haven't been reviewed yet
    filter = {'reviewed' : False}

    ur_params = params.copy()
    ur_params['list_description'] = ugettext_lazy('A list of all unhandled '
        'applications.')
    ur_params ['list_action'] = (redirects.getReviewRedirect, params)

    ur_list = helper.lists.getListContent(
        request, ur_params, filter, 0)

    # only select the requests that haven't been turned into a group yet
    filter = {'accepted' : True,
        'application_completed' : False}

    uh_params = params.copy()
    uh_params['list_description'] = ugettext_lazy('A list of all applications '
        'that have been accepted but not turned into a Club yet')
    uh_params ['list_action'] = (redirects.getReviewRedirect, params)

    uh_list = helper.lists.getListContent(
        request, uh_params, filter, 0)

    #only select the requests the have been denied
    filter = {'reviewed' : True,
        'accepted' : False}

    den_params = params.copy()
    den_params['list_description'] = ugettext_lazy('A list of all applications '
        'that have been denied')
    den_params ['list_action'] = (redirects.getReviewRedirect, params)

    den_list = helper.lists.getListContent(
        request, den_params, filter, 0)

    # fill contents with all the needed lists
    contents = [ur_list, uh_list, den_list]

    # call the _list method from base to display the list
    return self._list(request, params, contents, page_name)

view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
review = view.review
showReviewOverview = view.showReviewOverview
