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

"""Various utilities.

Current contents:
 - Text colorization using ANSI color codes
 - A class to construct and manage paths under a root path.
"""

__authors__ = [
    # alphabetical order by last name, please
    '"David Anderson" <dave@natulte.net>',
    ]

import os.path


# The magic escape sequence understood by modern terminal emulators to
# configure fore/background colors and other basic text display
# settings.
_ANSI_ESCAPE = '\x1b[%dm'


# Some intrnal non-color settings that we use.
_RESET = 0  # Reset to terminal defaults.
_BOLD = 1   # Brighter colors.


# ANSI color codes.
RED = 31
GREEN = 32
WHITE = 37


def _ansi_escape(code):
    return _ANSI_ESCAPE % code


def colorize(text, color, bold=False):
    """Colorize some text using ANSI color codes.

    Note that while ANSI color codes look good in a terminal they look
    like noise in log files unless viewed in an ANSI color capable
    viewer (such as 'less -R').

    Args:
      text: The text to colorize.
      color: One of the color symbols from this module.
      bold: If True, make the color brighter.

    Returns:
      The input text string, appropriately sprinkled with color
      codes. Colors are reset to terminal defaults after the input
      text.
    """
    bold = _ansi_escape(_BOLD) if bold else ''
    return '%s%s%s%s' % (bold, _ansi_escape(color),
                         text, _ansi_escape(_RESET))


class Paths(object):
    """A helper to construct and check paths under a given root."""

    def __init__(self, root):
        """Initializer.

        Args:
          root: The root of all paths this instance will consider.
        """
        self._root = os.path.abspath(
            os.path.expandvars(os.path.expanduser(root)))

    def path(self, path=''):
        """Construct and return a path under the path root.

        Args:
          path: The desired path string relative to the root.

        Returns:
          The absolute path corresponding to the relative input path.
        """
        assert not os.path.isabs(path)
        return os.path.abspath(os.path.join(self._root, path))

    def exists(self, path=''):
        """Check for the existence of a path under the path root.

        Does not discriminate on the path type (ie. it could be a
        directory, a file, a symbolic link...), just checks for the
        existence of the path.

        Args:
          path: The path string relative to the root.

        Returns:
          True if the path exists, False otherwise.
        """
        return os.path.exists(self.path(path))
