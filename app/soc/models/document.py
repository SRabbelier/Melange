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

from django.utils.translation import ugettext_lazy

import soc.models.work


class Document(soc.models.work.Work):
  """Model of a Document.
  
  Document is used for things like FAQs, front page text, etc.

  The specific way that the properties and relations inherited from Work
  are used with a Document are described below.

    work.title:  the title of the Document

    work.reviews:  reviews of the Document by Reviewers

    work.content:  the rich-text contents of the Document
  """
  pass