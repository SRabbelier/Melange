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
"""

__authors__ = [
    # alphabetical order by last name, please
    '"David Anderson" <dave@natulte.net>',
    ]

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
