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

"""Generic cleaning methods
"""

__authors__ = [
    '"Todd Larsen" <tlarsen@google.com>',
    '"Sverre Rabbelier" <sverre@rabbelier.nl>',
    ]


from django import forms

from soc.logic import validate
from soc.logic.models import user as user_logic


def clean_new_link_id(logic):
  """Clean method for new link_id's

  Returns a clean method that checks if the specified link_id is
  in the proper format, and verifies that the link_id is not already in
  in use by another entity of the same type.
  """

  def wrapped(self):
    # convert to lowercase for user comfort
    link_id = self.cleaned_data.get('link_id').lower()
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
    if logic.getFromFields(link_id=link_id):
      raise forms.ValidationError("This link ID is already in use.")
    return link_id

  return wrapped


def clean_link_id(self):
  # convert to lowercase for user comfort
  link_id = self.cleaned_data.get('link_id').lower()
  if not validate.isLinkIdFormatValid(link_id):
    raise forms.ValidationError("This link ID is in wrong format.")
  return link_id


def clean_existing_user(field_name):
  """Check if the field_name field is a valid user.
  """

  def wrapped(self):
    link_id = self.cleaned_data.get(field_name).lower()
  
    if not validate.isLinkIdFormatValid(link_id):
      raise forms.ValidationError("This link ID is in wrong format.")
  
    user_entity = user_logic.logic.getForFields({'link_id' : link_id}, unique=True)
  
    if not user_entity:
      # user does not exist
      raise forms.ValidationError("This user does not exist.")
  
    return user_entity
  return wrapped


def clean_feed_url(self):
  feed_url = self.cleaned_data.get('feed_url')

  if feed_url == '':
    # feed url not supplied (which is OK), so do not try to validate it
    return None
  
  if not validate.isFeedURLValid(feed_url):
    raise forms.ValidationError('This URL is not a valid ATOM or RSS feed.')

  return feed_url
