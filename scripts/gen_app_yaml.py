#! /usr/bin/python2.5

# Copyright 2009 the Melange authors.
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

"""A script to generate the app.yaml from the template with an application
name filled in.

Usage:
  gen_app_yaml.py [-f] APPLICATION_NAME

Arguments:
  APPLICATION_NAME: the name to use for the application (no underscores)

Flags:
  -f:  overwrite an existing app.yaml (default=false)
"""

from __future__ import with_statement

__authors__ = [
    # alphabetical order by last name, please
    '"Dan Bentley" <dbentley@google.com>',
    ]

import os
import sys


def generateAppYaml(application_name, force=False):
  """Generate the app.yaml file.

  Args:
    application_name: str, the name to write into the application filed
    force: bool, whether to overwrite an existing app.yaml
  """
  scripts_directory = os.path.dirname(__file__)
  app_dir = os.path.abspath(os.path.join(scripts_directory, '../app'))
  template_path = os.path.join(app_dir, 'app.yaml.template')
  app_yaml_path = os.path.join(app_dir, 'app.yaml')
  if not os.path.exists(template_path):
    sys.exit("Template file %s non-existent. Corrupt client?" % template_path)
  if os.path.exists(app_yaml_path):
    if not force:
      sys.exit("%s exists; exiting. To overwrite, pass -f on the command-line"
               % app_yaml_path)
  with open(template_path) as infile:
    template_contents = infile.read()
  app_yaml_contents = template_contents.replace(
      '# application: FIXME',
      'application: '+ application_name)
  with open(app_yaml_path, 'w') as outfile:
    outfile.write(app_yaml_contents)
  # TODO(dbentley): should this be done via logging?
  print "Wrote application name %s to %s." % (application_name, app_yaml_path)


def usage(msg):
  """Print an error message and the usage of the program; then quit.
  """
  sys.exit('Error: %s\n\n%s' % (msg, __doc__))


def main(args):
  args = args[1:] # strip off the binary name
  if not args:
    usage("No arguments supplied.")
  if args[0] == '-f':
    force = True
    args = args[1:]
  else:
    force = False
  if len(args) != 1:
    usage("No application name supplied.")
  application_name = args[0]
  generateAppYaml(application_name, force=force)


if __name__ == '__main__':
  main(sys.argv)
