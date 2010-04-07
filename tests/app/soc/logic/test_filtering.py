#!/usr/bin/env python2.5
# -*- coding: UTF-8 -*-
#
# Copyright 2010 the Melange authors.
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


__authors__ = [
  '"Matthew Wilkes" <matthew@matthewwilkes.co.uk>',
  ]

import unittest

from htmlsanitizer import HtmlSanitizer


class FilteringTest(unittest.TestCase):
  """Tests to check HTML filtering works correctly.
  """

  #def test_newlines_preserved_unchanged_normally(self):
  #  """ Test that newline is preserved  in paragraphs. """
  #  dirty = u'''<p>\r\n</p>'''
  #  expected = u'''<p>\n</p>'''
  #
  #  cleaner = HtmlSanitizer.Cleaner()
  #  cleaner.string = dirty
  #  cleaner.clean()
  #  self.assertEqual(cleaner.string, expected)
  #
  #def test_newlines_preserved_if_needed_to_be_wrapped(self):
  #  """ Test that when wrapped in <p /> tags newlines are preserved
  #  (albeit normalised)."""
  #  dirty = u'''\n\n'''
  #  expected = u'''<p>\n</p>'''
  #
  #  cleaner = HtmlSanitizer.Cleaner()
  #  cleaner.string = dirty
  #  cleaner.clean()
  #  self.assertEqual(cleaner.string, expected)
  #
  #def test_newlines_wrapped_together_if_in_filtered_tags(self):
  #  """ Test that when tags are filtered their contents is preserved (albeit
  #  with normalised whitespace). """
  #  dirty = u'''<div>\n</div><div>\n</div>'''
  #  expected = u'''<p>\n</p>'''
  #
  #  cleaner = HtmlSanitizer.Cleaner()
  #  cleaner.string = dirty
  #  cleaner.clean()
  #  self.assertEqual(cleaner.string, expected)

  def test_elements_that_compare_equal_arent_reordered(self):
    """ Test that ordering is preserved with multiple identical tags.
    If two elements have the same contents they compare equal. You can
    abuse the insert method in beautiful soup to reorder tags, as if a
    subelement is reinserted it will be moved to the position passed to
    insert. Unfortunately, this gets confused if elements compare equal,
    which results in only the first one being moved and all others left in
    place. If all elements are 'moved' then this has the effect of the
    other equal tags being left at the end of the stream.
    """
    dirty = u'''<div>\n<h1>One</h1>\n<div>\n<h2>Repeat</h2>\n</div>\n</div>\n<div>\n<h1>Two</h1>\n<div>\n<h2>Repeat</h2>\n</div>\n</div>'''
    expected = u'''<div>\n<h1>One</h1>\n<div>\n<h2>Repeat</h2>\n</div>\n</div>\n<div>\n<h1>Two</h1>\n<div>\n<h2>Repeat</h2>\n</div>\n</div>'''

    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = dirty
    cleaner.clean()
    self.assertEqual(cleaner.string, expected)

  def test_break_tags_are_preserved(self):
    """ Test that <br /> tags are preserved when wrapped. """
    dirty = u'''Hello.<br />Goodbye.'''
    expected = u'''Hello.<br />Goodbye.'''

    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = dirty
    cleaner.clean()
    self.assertEqual(cleaner.string, expected)

  def test_no_extra_paragraphs_are_inserted(self):
    """Test that no extra paragraph tags are inserted"""
    dirty = u'''<p>Bob</p>\n<p>Hello Bob</p>'''
    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = dirty
    cleaner.clean()
    self.assertEqual(dirty, cleaner.string)

  def test_xss_gets_filtered(self):
    """Test that the XSS as described in [0] gets filtered.

    [0] http://stackoverflow.com/questions/699468/python-html-sanitizer-scrubber-filter/812785#812785
    """
    from HTMLParser import HTMLParseError

    dirty = u'''<<script>script> alert("Haha, I hacked your page."); </</script>script>'''
    cleaner = HtmlSanitizer.Cleaner()
    try:
      cleaner.string = dirty
      cleaner.clean()
      self.fail("Invalid html should generate an error message.")
    except Exception, msg:
      pass

  def test_anchor_tags_are_preserved(self):
    """Test that anchor tags are preserved"""
    dirty = u'''<p><a name="there"></a></p>'''
    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = dirty
    cleaner.clean()
    self.assertEqual(dirty, cleaner.string)

  def test_partial_quoted_tags_are_no_problem(self):
    """If some partial HTML is quoted it should be treated as text and not
    subject to validation errors.
    """
    dirty = u'''<p>&lt;a href=&quot;http://www.example.com&quot;</p>'''
    expected = u'''<p>&lt;a href=&quot;http://www.example.com&quot;</p>'''

    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = dirty
    cleaner.clean()
    self.assertEqual(cleaner.string, expected)

  def test_hr_tags_are_preserved(self):
    """Test that hr tags are preserved"""
    dirty = u'''<p><hr /></p>'''
    cleaner = HtmlSanitizer.Cleaner()
    cleaner.string = dirty
    cleaner.clean()
    self.assertEqual(dirty, cleaner.string)
