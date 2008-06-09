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

"""Functions used by multiple scripts to form Google App Engine images.

These utility functions are used by multiple scripts for creating and managing
Google App Engine "uploadable image" directories produced by combining a
specific Melange application (for example: trunk/apps/proto, trunk/apps/gsoc,
trunk/apps/ghop, etc.), the SoC framework in trunk/soc, and any /thirdparty/
packages, such as thirdparty/django.

The directory layout expected by Google App Engine is (approximately):
  <app>/
        app.yaml
        index.yaml
        content/     (a static content directory for the Melange application)
        main.py      (a WSGI wrapper for Django-based Google App Engine apps)
        settings.py  (application-specific Django settings)
        urls.py      (application-specific URL handler mappings)

The application itself can have application-specific code and templates, so
there is an additional subdirectory with the same name as the application
(to disambiguate modules in the Melange application with same-named modules
in the SoC framework):
  <app>/
        <app>/
              models/, templates/, views/, etc.

Google App Engine assumes that the root of package paths is <app>/, so all
packages are placed in sub-directories of <app>/, and the SoC framework
is considered a package:
  <app>/
        soc/
            models/, templates/, views/, etc.

For Django template based applications (which Melange applications are),
include the django distribution directory (which is one of the /thirdparty/
packages) and some Django-specific files:
  <app>/
        django/
               core/, db/, dispatch/, etc.

Any other /thirdparty/ packages would be included in the the Google App Engine
"uploadable image" directory similarly to Django above.


A NOTE ABOUT DIRECTORY NAMES RETURNED BY FUNCTIONS IN THIS MODULE

The functions in this module return directory names with a trailing / svn path
separator.  This is done by convention only (svn_helper functions normalize
the path names of directories in this same way).  The trailing separator is
kept to make it easier to combine paths (since the caller can always assume
directories end with the / separator) and to make it easier to distinguish
directories from files in human-readable output.

Some pysvn Client methods accept directories named this way, others raise
exceptions and expect a "canonical" form that does not include the trailing
/ separator.  This does not seem to be documented in the pysvn documentation,
so the trailing separator is removed in svn_helper when necessary.
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


import sys

from trunk.scripts import svn_helper


def getRepoAppPath(repo, app):
  """Returns path to specified Melange app in the supplied svn repository.

  Args:
    repo: SVN repository URL
    app: Melange application name (expected to exist in trunk/apps)
  """
  # see note about directory names ending with / svn path separators in the
  # module __doc__ string
  return svn_helper.formatDirPath('%strunk/apps/%s' % (
      svn_helper.formatDirPath(repo), app))


def getRepoThirdPartyPath(repo):
  """Returns path to third-party packages in the supplied svn repository.

  Args:
    repo: SVN repository URL
  """
  # see note about directory names ending with / svn path separators in the
  # module __doc__ string
  return '%sthirdparty/' % svn_helper.formatDirPath(repo)


def getThirdPartyPackageNames(pkg_path, **svn_kwargs):
  """Returns a list of third-party packages in the supplied URL.

  Args:
    pkg_path: full SVN URL path to the directory containing third-party
      packages, usually the path formed by calling getRepoThirdPartyPath()
    **svn_kwargs: keyword arguments passed through to svn_helper.lsDirs()
      (for "advanced users")

  Returns:
    A list of third-party packages found in pkg_path.  Third-party "packages"
    are all of the directories is the pkg_path  directory (but not individual
    files in pkg_path) that do *not* begin with an underscore (_).  Individual
    files and directories beginning with underscores in the pkg_path directory
    are omitted from the results.
  """
  return [pkg for pkg in svn_helper.lsDirs(pkg_path, **svn_kwargs)
            if not pkg.startswith('_')]


def getRepoFrameworksPath(repo):
  """Returns path to Melange framework packages in the supplied svn repository.

  Args:
    repo: SVN repository URL
  """
  # see note about directory names ending with / svn path separators in the
  # module __doc__ string
  return '%strunk/' % svn_helper.formatDirPath(repo)


def getFrameworksNames():
  """Returns a list of Melange framework packages (currently a constant list).
  """
  # see note about directory names ending with / svn path separators in the
  # module __doc__ string
  return ['soc/']


def formDefaultAppBranchPath(branch, user, src, dest):
  """Returns a relative path to a to-be-created App Image branch.

  Args:
    branch: explicit branch name, if it was specified (or None, '', etc.
      instead, if it was not)
    user: subdirectory of /users/ representing a particular contributor
    src: sub-directory name of the specific Melange application to branch
    dest: alternate destination sub-directory name of the Melange application
      in its new, branched location, if it was specified (or None, '', etc.
      instead, if it was not)

  Returns:
    * branch if it was specified ("non-False"), or
    * users/user/dest/ if dest was specified, or
    * users/user/src/ otherwise
  """
  if not branch:
    if dest:
      branch = 'users/%s%s' % (svn_helper.formatDirPath(user), dest)
    else:
      branch = 'users/%s%s' % (svn_helper.formatDirPath(user), src)

  return svn_helper.formatDirPath(branch)


def verbosePrint(verbose, fmt_str, *fmt_args, **fmt_kwargs):
  """If verbosity level greater than zero, print out formatted string.

  Since app_image.py is a utility module most often used by scripts, many
  of its functions print to stdout.  For cases when printed output may not
  be desired, functions should supply a 'verbose' parameter to disable
  output.  The functions in app_image.py use this function to implement
  that selective printing capability.

  Args:
    verbose: verbosity level integer, any value greater than 0 enables
      output
    fmt_str: required format string
    *fmt_args: if present, positional arguments supplied to fmt_str
    **fmt_kwargs: if *fmt_args is not present, named arguments supplied to
      fmt_str, which is expected to contain named format specifiers, for
      example: '%(foo)s'
  """
  if verbose > 0:
    if not fmt_args:
      fmt_args = fmt_kwargs

    print fmt_str % fmt_args


def branchFromSrcApp(app, repo, dest, verbose=1, **svn_kwargs):
  """Branch one Melange app in /trunk/apps/ to form basis of App Engine image.

  Args:
    app: Melange application name in /trunk/apps/
    repo: svn repository root URL
    dest: working copy destination path of the image branch
    verbose: print status if greater than 0; default is 1
    **svn_kwargs: keyword arguments passed on to svn_helper.branchDir()
  """
  repo_app = getRepoAppPath(repo, app)

  verbosePrint(verbose, 'Branching %s from:\n %s\nto:\n %s\n',
               app, repo_app, dest)

  svn_helper.branchDir(repo_app, dest, **svn_kwargs)


def branchFromThirdParty(repo, dest, verbose=1, **svn_kwargs):
  """Branch all subdirectories in /thirdparty/ into a new App Engine image.

  Subdirectories (except for those with names beginning with underscores) in
  /thirdparty/ represent third-party packages that are to be placed in each
  Google App Engine "image" branch.  Files in the root of /thirdparty/ (that
  is, not in a package) and, as previously mentioned, subdrectories beginning
  with underscores, are *not* branched.

  Args:
    repo: svn repository root URL
    dest: working copy destination path of the image branch
    verbose: print status if greater than 0; default is 1
    **svn_kwargs: keyword arguments passed on to svn_helper.branchItems()
  """
  pkg_dir = getRepoThirdPartyPath(repo)
  packages = getThirdPartyPackageNames(pkg_dir)

  verbosePrint(verbose,
      'Branching third-party packages:\n %s\nfrom:\n %s\ninto:\n %s\n',
      '  '.join(packages), pkg_dir, dest)

  svn_helper.branchItems(pkg_dir, dest, packages, **svn_kwargs)


def branchFromFramework(repo, dest, verbose=1, **svn_kwargs):
  """Branch the SoC framework into a new App Engine image branch.

  The SoC framework current consists of only the contents of /trunk/soc/.

  Args:
    repo: svn repository root URL
    dest: working copy destination path of the image branch
    verbose: print status if greater than 0; default is 1
    **svn_kwargs: keyword arguments passed on to svn_helper.branchItems()
  """
  framework_dir = getRepoFrameworksPath(repo)
  packages = getFrameworksNames()

  verbosePrint(verbose,
      'Branching framework components:\n %s\nfrom:\n %s\ninto:\n %s\n',
      '  '.join(packages), framework_dir, dest)

  svn_helper.branchItems(framework_dir, dest, packages, **svn_kwargs)


def exportFromSrcApp(app, repo, dest, verbose=1, **svn_kwargs):
  """Export one Melange app in /trunk/apps/ to form basis of App Engine image.

  Args:
    app: Melange application name in /trunk/apps/
    repo: svn repository root URL
    dest: local filesystem destination path of the exported image
    verbose: print status if greater than 0; default is 1
    **svn_kwargs: keyword arguments passed on to svn_helper.exportDir()
  """
  repo_app = getRepoAppPath(repo, app)

  verbosePrint(verbose, 'Exporting %s from:\n %s\nto:\n %s\n',
               app, repo_app, dest)

  svn_helper.exportDir(repo_app, dest, **svn_kwargs)


def exportFromThirdParty(repo, dest, verbose=1, **svn_kwargs):
  """Export all subdirectories in /thirdparty/ into a new App Engine image.

  Subdirectories (except for those with names beginning with underscores) in
  /thirdparty/ represent third-party packages that are to be placed in each
  Google App Engine "image".  Files in the root of /thirdparty/ (that is,
  not in a package) and, as previously mentioned, subdirectories beginning
  with underscores, are *not* exported.

  Args:
    repo: svn repository root URL
    dest: local filesystem destination path of the exported image
    verbose: print status if greater than 0; default is 1
    **svn_kwargs: keyword arguments passed on to svn_helper.exportItems()
  """
  pkg_dir = getRepoThirdPartyPath(repo)
  packages = getThirdPartyPackageNames(pkg_dir)

  verbosePrint(verbose,
      'Exporting third-party packages:\n %s\nfrom:\n %s\ninto:\n  %s\n',
      '  '.join(packages), pkg_dir, dest)

  svn_helper.exportItems(pkg_dir, dest, packages, **svn_kwargs)


def exportFromFramework(repo, dest, verbose=1, **svn_kwargs):
  """Export the SoC framework into a new App Engine image.

  The SoC framework current consists of only the contents of /trunk/soc/.

  Args:
    repo: svn repository root URL
    dest: local filesystem destination path of the exported image
    verbose: print status if greater than 0; default is 1
    **svn_kwargs: keyword arguments passed on to svn_helper.exportItems()
  """
  framework_dir = getRepoFrameworksPath(repo)
  packages = getFrameworksNames()

  verbosePrint(verbose,
      'Exporting framework components:\n %s\nfrom:\n %s\ninto:\n %s\n',
      '  '.join(packages), framework_dir, dest)

  svn_helper.exportItems(framework_dir, dest, packages, **svn_kwargs)
