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

Steps (currently done by hand, but too be scripted in the future) to make
a release:

1) set RELEASE_TAG in this file to a "release candidate" release string that
   ends in "rc"

2) commit this file *by itself* in its own commit

3) use 'svn cp' to create a release branch in /branches/ with exactly the
   same name as the contents of the RELEASE_TAG string

4) set RELEASE_TAG back to None in /trunk/


To finalize a release candidate in a release branch for a push to the live
web site:

1) in the release branch, change RELEASE_TAG to remove the trailing "rc"

2) commit this file in the release branch *by itself* in its own commit

3) use 'svn cp' to create a tag in /tags/ with exactly the same name as the
   contents of the RELEASE_TAG string

4) put the release branch in a state where it is ready for additional patches
   after the tag by setting the end of the RELEASE_TAG string to "p0"


To re-release a previously-tagged release branch after a patch for a push to
the live web site:

1) increment the "patch suffix" of the RELEASE_TAG string to the next integer
   (for example, "p0" becomes "p1", so the first tagged patch release will
   always be "p1", not "p0", which is just a placeholder)

2) (same as #2 for a release candidate)

3) (same as #3 for a release candidate)

4) (there is no step 4)
"""

__authors__ = [
  '"Todd Larsen" <tlarsen@google.com>',
  ]


RELEASE_TAG = "0.3-20090219rc"

