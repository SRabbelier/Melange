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
from soc.logic.helper import notifications
from soc.logic.models import club_app as club_app_logic
from soc.logic.models import user as user_logic
from soc.views import helper
from soc.views import out_of_band
from soc.views.helper import access
from soc.views.helper import decorators
from soc.views.helper import redirects
from soc.views.helper import lists as list_helper
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
    rights['create'] = [access.checkAgreesToSiteToS]
    rights['delete'] = [access.checkIsMyApplication(club_app_logic)]
    rights['edit'] = [access.checkIsMyApplication(club_app_logic)]
    rights['list'] = [access.checkAgreesToSiteToS]
    rights['public'] = [access.checkIsMyApplication(club_app_logic)]
    rights['review'] = [access.checkIsDeveloper]

    new_params = {}

    new_params['rights'] = rights
    new_params['logic'] = club_app_logic.logic

    new_params['create_template'] = 'soc/models/twoline_edit.html'
    new_params['edit_template'] = 'soc/models/twoline_edit.html'

    new_params['extra_dynaexclude'] = ['applicant', 'backup_admin', 'status',
        'created_on', 'last_modified_on']
    new_params['create_extra_dynafields'] = {
        'backup_admin_link_id': forms.CharField(
              label=soc.models.club_app.ClubApplication.backup_admin.verbose_name
              ),
        'clean_backup_admin_link_id': 
            cleaning.clean_existing_user_not_equal_to_current('backup_admin_link_id'),
        }

    patterns = [(r'^%(url_name)s/(?P<access_type>review)$',
        'soc.views.models.%(module_name)s.review_overview',
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

  @decorators.merge_params
  @decorators.check_access
  def list(self, request, access_type,
           page_name=None, params=None, filter=None):
    """Lists all notifications that the current logged in user has stored.

    for parameters see base.list()
    """

    # get the current user
    user_entity = user_logic.logic.getForCurrentAccount()

    is_developer = accounts.isDeveloper(user=user_entity)

    filter = {
        'status': 'needs review',
        }

    if not is_developer:
      # only select the applications for this user so construct a filter
      filter['applicant'] = user_entity

    # get all the pending applications

    pa_params = params.copy() # pending applications

    if is_developer:
      pa_params['list_description'] = ugettext_lazy(
          "An overview of all pending club applications.")
    else:
      pa_params['list_description'] = ugettext_lazy(
          "An overview of your pending club applications.")

    pa_list = list_helper.getListContent(
        request, pa_params, filter, 0)

    # get all the reviewed applications now

    # re-use the old filter, but set to only reviewed and accepted
    filter['status'] = 'accepted'

    aa_params = params.copy() # accepted applications

    if is_developer:
      aa_params['list_description'] = ugettext_lazy(
          "An overview of all accepted club applications.")
    else:
      aa_params['list_description'] = ugettext_lazy(
          "An overview of your accepted club applications.")

    aa_params['url_name'] = 'club'
    aa_params['list_action'] = (redirects.getApplicantRedirect, aa_params)

    aa_list = list_helper.getListContent(
        request, aa_params, filter, 1)

    # get all the reviewed applications that were denied

    # re use the old filter, but this time only for denied apps
    filter['status'] = 'rejected'

    da_params = params.copy() # denied applications

    if is_developer:
      da_params['list_description'] = ugettext_lazy(
          "An overview of all denied club applications.")
    else:
      da_params['list_description'] = ugettext_lazy(
          "An overview of your denied club applications.")

    da_list = list_helper.getListContent(
        request, da_params, filter, 2)

    contents = [pa_list, aa_list, da_list]

    if is_developer:
      # re use the old filter, but this time only for ignored apps
      filter['status'] = 'ignored'

      ia_params = params.copy() # ignored applications

      ia_params['list_description'] = ugettext_lazy(
          "An overview of all ignored club applications.")

      ia_list = list_helper.getListContent(
          request, ia_params, filter, 2)

      contents += [ia_list]

    # call the _list method from base to display the list
    return self._list(request, params, contents, page_name)

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
    # the status needs to be set accordingly
    fields['status'] = 'needs review'

  def _public(self, request, entity, context):
    """See base._public().
    """

    context['entity_type_url'] = self._params['url_name']

  @decorators.merge_params
  @decorators.check_access
  def review(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Handles the view containing the review of an application.

    accepted (true or false) in the GET data will mark
    the application accordingly.


    For params see base.View.public().
    """

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
    if 'status' in get_dict.keys():
      status_value = get_dict['status']

      if status_value in ['accepted', 'rejected', 'ignored']:
        # this application has been properly reviewed update the status
        fields = {'status' : status_value}

        self._logic.updateModelProperties(entity, fields)
        
        if status_value is 'accepted':
          # the application has been accepted send out a notification
          notifications.sendNewClubNotification(entity)

        return self.reviewOverview(request, access_type,
            page_name=page_name, params=params, **kwargs)

    # the application has not been reviewed so show the information
    # using the appropriate review template
    params['public_template'] = params['review_template']

    return super(View, self).public(request, access_type,
        page_name=page_name, params=params, **kwargs)

  @decorators.merge_params
  @decorators.check_access
  def reviewOverview(self, request, access_type,
             page_name=None, params=None, **kwargs):
    """Displays multiple lists of applications that are in different
    states of the application process.
    """

    params = dicts.merge(params, self._params)

    # only select the requests that haven't been reviewed yet
    filter = {'status' : 'needs review'}

    ur_params = params.copy()
    ur_params['list_description'] = ugettext_lazy('A list of all unhandled '
        'applications.')
    ur_params ['list_action'] = (redirects.getReviewRedirect, params)

    ur_list = helper.lists.getListContent(
        request, ur_params, filter, 0)

    # only select the requests that haven't been turned into a group yet
    filter['status'] = 'accepted'

    uh_params = params.copy()
    uh_params['list_description'] = ugettext_lazy('A list of all applications '
        'that have been accepted but not turned into a Club yet')
    uh_params ['list_action'] = (redirects.getReviewRedirect, params)

    uh_list = helper.lists.getListContent(
        request, uh_params, filter, 0)

    # only select the requests the have been rejected
    filter ['status'] = 'rejected'

    den_params = params.copy()
    den_params['list_description'] = ugettext_lazy('A list of all applications '
        'that have been ignored')
    den_params ['list_action'] = (redirects.getReviewRedirect, params)

    den_list = helper.lists.getListContent(
        request, den_params, filter, 0)

    # only select the request that have been ignored
    filter ['status'] = 'ignored'

    ign_params = params.copy()
    ign_params['list_description'] = ugettext_lazy('A list of all applications '
        'that have been ignored')
    ign_params ['list_action'] = (redirects.getReviewRedirect, params)

    ign_list = helper.lists.getListContent(
        request, ign_params, filter, 0)

    # fill contents with all the needed lists
    contents = [ur_list, uh_list, den_list, ign_list]

    # call the _list method from base to display the list
    return self._list(request, params, contents, page_name)

view = View()

create = view.create
delete = view.delete
edit = view.edit
list = view.list
public = view.public
export = view.export
review = view.review
review_overview = view.reviewOverview

