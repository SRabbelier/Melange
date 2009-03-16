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
import sys

import util


# A logging level that is even lower than DEBUG. We use this level to
# log to file only, when we need to replay something output by
# bypassing the logging system.
_TERMINAL_ECHO = 5


# Pull in the functions from the logging module, for ease of use
debug = logging.debug
info = logging.info
error = logging.error
raw = debug  # Used for logging raw output like subprocess stdout data.


# Save the actual out/err streams before init() replaces them. Users
# of the logging system can use these files if they need to bypass the
# logging system for some reason.
stdout = sys.stdout
stderr = sys.stderr


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


class FileLikeLogger(object):
  """A file-like object that logs anything written to it."""

  def __init__(self):
    self._buffer = []

  def _getBuffer(self):
    data, self._buffer = ''.join(self._buffer), []
    return data

  def close(self):
    self.flush()

  def flush(self):
    raw(self._getBuffer())

  def write(self, str):
    lines = str.split('\n')
    self.writelines(lines[0:-1])
    self._buffer.append(lines[-1])

  def writelines(self, lines):
    if not lines:
      return
    lines[0] = self._getBuffer() + lines[0]
    for line in lines:
      raw(line)


def init(logfile=None):
  """Initialize the logging subsystem.

  Args:
    logfile: The filename for the transcript file, if any.
  """

  root = logging.getLogger('')
  root.setLevel(_TERMINAL_ECHO)

  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)
  console.setFormatter(_ColorizingFormatter())
  root.addHandler(console)

  if logfile:
    transcript = logging.FileHandler(logfile, 'w')
    transcript.setLevel(_TERMINAL_ECHO)
    transcript.setFormatter(_DecolorizingFormatter())
    root.addHandler(transcript)

  # Redirect sys.stdout and sys.stderr to logging streams. This will
  # force everything that is output in this process, even through
  # 'print', to go to both the console and the transcript (if active).
  sys.stdout = FileLikeLogger()
  sys.stderr = FileLikeLogger()


def terminal_echo(text, *args, **kwargs):
  """Echo a message written manually to the terminal.

  This function should be used when you want to echo into the logging
  system something that you manually wrote to the real
  stdout/stderr.

  For example, when asking the user for input, you would output the
  raw prompt to the terminal manually, read the user's response, and
  then echo both the prompt and the answer back into the logging
  system for recording.
  """
  logging.log(_TERMINAL_ECHO, text, *args, **kwargs)
