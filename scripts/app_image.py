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
"""

__authors__ = [
  # alphabetical order by last name, please
  '"Todd Larsen" <tlarsen@google.com>',
]


from trunk.scripts import svn_helper


def getRepoAppPath(repo, app):
  """Returns path to specified Melange app in the supplied svn repository.
  """
  return '%strunk/apps/%s' % (repo, app)


def getRepoThirdPartyPath(repo):
  """Returns path to third-party packages in the supplied svn repository.
  """
  return '%sthirdparty/' % repo


def getThirdPartyPackageNames(pkg_path, **kwargs):
  """Returns a list of third-party packages in the supplied URL.
  """
  return [pkg for pkg in svn_helper.lsDirs(pkg_path, **kwargs)
            if not pkg.startswith('_')]


def getRepoFrameworksPath(repo):
  """Returns path to Melange framework packages in the supplied svn repository.
  """
  return '%strunk/' % repo


def getFrameworksNames():
  """Returns a list of Melange framework packages (currently a static list).
  """
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
    * users/user/dest if dest was specified, or
    * users/user/src otherwise
  """
  if not branch:
    if dest:
      branch = 'users/%s%s' % (user, dest)
    else:
      branch = 'users/%s%s' % (user, src)

  return branch


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

  if verbose > 0:
    print 'Branching %s from:\n %s\nto:\n %s\n' % (app, repo_app, dest)

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

  if verbose > 0:
    print 'Branching third-party packages:\n %s\nfrom:\n %s\ninto:\n %s\n' % (
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

  if verbose > 0:
    print 'Branching framework components:\n %s\nfrom:\n %s\ninto:\n %s\n' % (
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

  if verbose > 0:
    print 'Exporting %s from:\n %s\nto:\n %s\n' % (app, repo_app, dest)

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

  if verbose > 0:
    print 'Exporting third-party packages:\n %s\nfrom:\n %s\ninto:\n  %s\n' % (
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

  if verbose > 0:
    print 'Exporting framework components:\n %s\nfrom:\n %s\ninto:\n %s\n' % (
        '  '.join(packages), framework_dir, dest)

  svn_helper.exportItems(framework_dir, dest, packages, **svn_kwargs)
