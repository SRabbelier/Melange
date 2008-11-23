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

"""Release tag string for display in templates (and possibly other uses).

Set RELEASE_TAG to a release string, commit that change as the *only* change
in the commit, and then use 'svn copy' on the revision produced by committing
the updated RELEASE_TAG to create a tags/ release directory of the same name
as the string value.

After creating the tag, set RELEASE_TAG to None until the next release.
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]

# previous RELEASE_TAG = '0.0a20081123'

RELEASE_TAG = None

