#! /usr/bin/env python2.5

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

"""gen_app_yaml.py [-f] [-o] (-i | APPLICATION_NAME)

A script to generate the app.yaml from the template with an application
name filled in.

Arguments:
  APPLICATION_NAME: the name to use for the application (no underscores)
"""

from __future__ import with_statement

__authors__ = [
    # alphabetical order by last name, please
    '"Dan Bentley" <dbentley@google.com>',
    ]


import os
import sys
from optparse import OptionParser


def generateAppYaml(application_name, force=False, override_version=None):
  """Generate the app.yaml file.

  Args:
    application_name: str, the name to write into the application filed
    force: bool, whether to overwrite an existing app.yaml
    override_version: str, the manual version to use
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

  contents = template_contents.replace(
      '# application: FIXME',
      'application: '+ application_name)

  if override_version:
    # find the "version" field
    stop = contents.find("version: ")
    # find the next \n after it
    end = contents.find("\n", stop)
    # insert new version
    app_yaml_contents = contents[:stop+9] + override_version + contents[end:]
  else:
    app_yaml_contents = contents

  with open(app_yaml_path, 'w') as outfile:
    outfile.write(app_yaml_contents)

  print "Wrote application name %s to %s." % (application_name, app_yaml_path)


def usage(msg):
  """Print an error message and the usage of the program; then quit.
  """

  sys.exit('Error: %s\n\n%s' % (msg, __doc__))


def main(args):
  """Main program.
  """

  parser = OptionParser(usage=__doc__)
  parser.add_option("-f", "--force", action="store_true", default=False,
                    help="Overwrite existing app.yaml")
  parser.add_option("-i", "--interactive", action="store_true", default=False,
                    help="Ask for the application name interactively")
  parser.add_option("-o", "--override-version",
                    help="Uses the specified version instead of the one from app.yaml.template")

  options, args = parser.parse_args(args)

  if options.interactive:
    if args:
      parser.error("Cannot combine application name with -i")
    sys.stdout.write("Application name: ")
    application_name = sys.stdin.readline().strip()
  else:
    if len(args) != 1:
      parser.error("No application name supplied.")
    application_name = args[0]

  generateAppYaml(application_name, force=options.force,
                  override_version=options.override_version)

if __name__ == '__main__':
  main(sys.argv[1:]) # strip off the binary name
