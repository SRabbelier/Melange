#!/usr/bin/python2.5
#
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

from __future__ import with_statement

"""User prompting and file access utilities."""

__authors__ = [
    # alphabetical order by last name, please
    '"David Anderson" <dave@natulte.net>',
    ]

import error
import log


class Error(error.Error):
  pass


class FileAccessError(Error):
  """An error occured while accessing a file."""
  pass


def getString(prompt):
  """Prompt for and return a string."""
  prompt += ' '
  log.stdout.write(prompt)
  log.stdout.flush()

  response = sys.stdin.readline()
  log.terminal_echo(prompt + response.strip())
  if not response:
    raise error.AbortedByUser('Aborted by ctrl+D')

  return response.strip()


def confirm(prompt, default=False):
  """Ask a yes/no question and return the answer.

  Will reprompt the user until one of "yes", "no", "y" or "n" is
  entered. The input is case insensitive.

  Args:
    prompt: The question to ask the user.
    default: The answer to return if the user just hits enter.

  Returns:
    True if the user answered affirmatively, False otherwise.
  """
  if default:
    question = prompt + ' [Yn]'
  else:
    question = prompt + ' [yN]'
  while True:
    answer = getString(question)
    if not answer:
      return default
    elif answer in ('y', 'yes'):
      return True
    elif answer in ('n', 'no'):
      return False
    else:
      log.error('Please answer yes or no.')


def getNumber(prompt):
  """Prompt for and return a number.

  Will reprompt the user until a number is entered.
  """
  while True:
    value_str = getString(prompt)
    try:
      return int(value_str)
    except ValueError:
      log.error('Please enter a number. You entered "%s".' % value_str)


def getChoice(intro, prompt, choices, done=None, suggest=None):
  """Prompt for and return a choice from a menu.

  Will reprompt the user until a valid menu entry is chosen.

  Args:
    intro: Text to print verbatim before the choice menu.
    prompt: The prompt to print right before accepting input.
    choices: The list of string choices to display.
    done: If not None, the list of indices of previously
      selected/completed choices.
    suggest: If not None, the index of the choice to highlight as
      the suggested choice.

  Returns:
    The index in the choices list of the selection the user made.
  """
  done = set(done or [])
  while True:
    print intro
    print
    for i, entry in enumerate(choices):
      done_text = ' (done)' if i in done else ''
      indent = '--> ' if i == suggest else '    '
      print '%s%2d. %s%s' % (indent, i+1, entry, done_text)
    print
    choice = getNumber(prompt)
    if 0 < choice <= len(choices):
      return choice-1
    log.error('%d is not a valid choice between %d and %d' %
              (choice, 1, len(choices)))
    print


def fileToLines(path):
  """Read a file and return it as a list of lines."""
  try:
    with file(path) as f:
      return f.read().split('\n')
  except (IOError, OSError), e:
    raise FileAccessError(str(e))


def linesToFile(path, lines):
  """Write a list of lines to a file."""
  try:
    with file(path, 'w') as f:
      f.write('\n'.join(lines))
  except (IOError, OSError), e:
    raise FileAccessError(str(e))
