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

"""This module contains the Document Model."""

__authors__ = [
  '"Pawel Solyga" <pawel.solyga@gmail.com>',
]


from google.appengine.ext import db

import polymodel

from django.utils.translation import ugettext_lazy

import soc.models.user
import soc.models.work


class Document(soc.models.work.Work):
  """Model of a Document.
  
  Document is used for things like FAQs, front page text, etc.

  The specific way that the properties and relations inherited from Work
  are used with a Document are described below.

    work.title:  the title of the Document

    work.abstract:  document summary displayed as a snippet in Document
      list views

    work.authors:  the Authors of the Work referred to by this relation
      are the authors of the Document

    work.reviews:  reviews of the Document by Reviewers
  """

  #: Required db.TextProperty containing the Document contents.
  #: Unlike the work.abstract, which is considered "public" information,
  #: the content is only to be displayed to Persons in Roles eligible to
  #: view them (which may be anyone, for example, with the site front page).
  content = db.TextProperty(verbose_name=ugettext_lazy('Content'))
  
  #: User who created this document.
  #: TODO(pawel.solyga): replace this with WorkAuthors relation
  user = db.ReferenceProperty(reference_class=soc.models.user.User,
                              required=True, collection_name='documents')

