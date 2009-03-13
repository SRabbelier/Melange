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

"""Logging facilities.

The public interface is basically an initialization function for the
underlying Python logging module. Logging always goes to the console,
and can optionally be configured to write to a transcript file, which
will store exactly what appears on screen (minus colors).
"""

__authors__ = [
    # alphabetical order by last name, please
    '"David Anderson" <dave@natulte.net>',
    ]

import logging

import util


class _ColorizingFormatter(logging.Formatter):
  """A logging formatter that colorizes based on log levels."""

  def format(self, record):
    msg = logging.Formatter.format(self, record)

    if record.levelno >= logging.WARNING:
      return util.colorize(msg, util.RED, bold=True)
    elif record.levelno == logging.INFO:
      return util.colorize(msg, util.GREEN)
    else:
      return msg


class _DecolorizingFormatter(logging.Formatter):
  """A logging formatter that strips color."""

  def format(self, record):
    return util.decolorize(logging.Formatter.format(self, record))


def init(logfile=None):
  """Initialize the logging subsystem.

  Args:
    logfile: The filename for the transcript file, if any.
  """

  root = logging.getLogger('')
  root.setLevel(logging.DEBUG)

  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)
  console.setFormatter(_ColorizingFormatter())
  root.addHandler(console)

  if logfile:
    transcript = logging.FileHandler(logfile, 'w')
    transcript.setLevel(logging.DEBUG)
    transcript.setFormatter(_DecolorizingFormatter())
    root.addHandler(transcript)


debug = logging.debug
info = logging.info
error = logging.error
