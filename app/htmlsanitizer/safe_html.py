"""Copyright (c) 2002-2003, Benjamin Saller <bcsaller@ideasuite.com>, and
                        the respective authors.

Elements Copyright (c) 2001 Zope Foundation and Contributors.

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following disclaimer
      in the documentation and/or other materials provided with the
      distribution.
    * Neither the name of Archetypes nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."""

from sgmllib import SGMLParser, SGMLParseError
import re
from cgi import escape

# tag mapping: tag -> short or long tag
VALID_TAGS = {'code': 1, 'meter': 1, 'tbody': 1, 'img': 0, 'title': 1, 'tt': 1, 'tr': 1, 'li': 1, 'source': 1, 'tfoot': 1, 'th': 1, 'td': 1, 'dl': 1, 'blockquote': 1, 'big': 1, 'dd': 1, 'kbd': 1, 'dt': 1, 'p': 1, 'small': 1, 'output': 1, 'div': 1, 'em': 1, 'datalist': 1, 'hgroup': 1, 'meta': 0, 'video': 1, 'rt': 1, 'canvas': 1, 'rp': 1, 'sub': 1, 'section': 1, 'sup': 1, 'progress': 1, 'acronym': 1, 'base': 0, 'br': 0, 'address': 1, 'article': 1, 'strong': 1, 'ol': 1, 'caption': 1, 'dialog': 1, 'col': 1, 'h2': 1, 'h3': 1, 'h1': 1, 'h6': 1, 'h4': 1, 'h5': 1, 'header': 1, 'table': 1, 'span': 1, 'area': 0, 'mark': 1, 'dfn': 1, 'var': 1, 'cite': 1, 'thead': 1, 'head': 1, 'hr': 0, 'ruby': 1, 'b': 1, 'colgroup': 1, 'keygen': 1, 'ul': 1, 'del': 1, 'pre': 1, 'figure': 1, 'ins': 1, 'aside': 1, 'nav': 1, 'details': 1, 'u': 1, 'samp': 1, 'map': 1, 'a': 1, 'footer': 1, 'i': 1, 'q': 1, 'command': 1, 'time': 1, 'audio': 1, 'bdo': 1, 'abbr': 1}
NASTY_TAGS = {'style': 1, 'script': 1, 'object': 1, 'applet': 1, 'meta': 1, 'embed': 1, 'head': 1}

msg_pat = """
<div class="system-message">
<p class="system-message-title">System message: %s</p>
%s</d>
"""

def hasScript(s):
   """Dig out evil Java/VB script inside an HTML attribute.

   >>> hasScript('script:evil(1);')
   True
   >>> hasScript('expression:evil(1);')
   True
   >>> hasScript('http://foo.com/ExpressionOfInterest.doc')
   False
   """
   s = decode_htmlentities(s)
   s = ''.join(s.split()).lower()
   for t in ('script:', 'expression:', 'expression('):

      if t in s:
         return True
   return False

def decode_htmlentities(s):
   """ XSS code can be hidden with htmlentities """

   entity_pattern = re.compile("&#(?P<htmlentity>x?\w+)?;?")
   s = entity_pattern.sub(decode_htmlentity,s)
   return s

def decode_htmlentity(m):
   entity_value = m.groupdict()['htmlentity']
   if entity_value.lower().startswith('x'):
      try:
          return chr(int('0'+entity_value,16))
      except ValueError:
          return entity_value
   try:
      return chr(int(entity_value))
   except ValueError:
      return entity_value

class IllegalHTML(Exception): pass

class StrippingParser(SGMLParser):
    """Pass only allowed tags;  raise exception for known-bad.

    Copied from Products.CMFDefault.utils
    Copyright (c) 2001 Zope Corporation and Contributors. All Rights Reserved.
    """

    from htmlentitydefs import entitydefs # replace entitydefs from sgmllib

    def __init__(self, valid, nasty, remove_javascript, raise_error):
        SGMLParser.__init__( self )
        self.result = []
        self.valid = valid
        self.nasty = nasty
        self.remove_javascript = remove_javascript
        self.raise_error = raise_error
        self.suppress = False

    def handle_data(self, data):
        if self.suppress: return
        if data:
            self.result.append(escape(data))

    def handle_charref(self, name):
        if self.suppress: return
        self.result.append('&#%s;' % name)

    def handle_comment(self, comment):
        pass

    def handle_decl(self, data):
        pass

    def handle_entityref(self, name):
        if self.suppress: return
        if self.entitydefs.has_key(name):
            x = ';'
        else:
            # this breaks unstandard entities that end with ';'
            x = ''

        self.result.append('&%s%s' % (name, x))

    def unknown_starttag(self, tag, attrs):
        """ Delete all tags except for legal ones.
        """

        if self.suppress: return

        if self.valid.has_key(tag):
            self.result.append('<' + tag)

            remove_script = getattr(self,'remove_javascript',True)

            for k, v in attrs:
                if remove_script and k.strip().lower().startswith('on'):
                    if not self.raise_error: continue
                    else: raise IllegalHTML, 'Script event "%s" not allowed.' % k
                elif remove_script and hasScript(v):
                    if not self.raise_error: continue
                    else: raise IllegalHTML, 'Script URI "%s" not allowed.' % v
                else:
                    self.result.append(' %s="%s"' % (k, v))

            #UNUSED endTag = '</%s>' % tag
            if self.valid.get(tag):
                self.result.append('>')
            else:
                self.result.append(' />')
        elif self.nasty.has_key(tag):
            self.suppress = True
            if self.raise_error:
                raise IllegalHTML, 'Dynamic tag "%s" not allowed.' % tag
        else:
            # omit tag
            pass

    def unknown_endtag(self, tag):
        if self.nasty.has_key(tag) and not self.valid.has_key(tag):
            self.suppress = False
        if self.suppress: return
        if self.valid.get(tag):
            self.result.append('</%s>' % tag)
            #remTag = '</%s>' % tag

    def parse_declaration(self, i):
        """Fix handling of CDATA sections. Code borrowed from BeautifulSoup.
        """
        j = None
        if self.rawdata[i:i+9] == '<![CDATA[':
             k = self.rawdata.find(']]>', i)
             if k == -1:
                 k = len(self.rawdata)
             data = self.rawdata[i+9:k]
             j = k+3
             self.result.append("<![CDATA[%s]]>" % data)
        else:
            try:
                j = SGMLParser.parse_declaration(self, i)
            except SGMLParseError:
                toHandle = self.rawdata[i:]
                self.result.append(toHandle)
                j = i + len(toHandle)
        return j

    def getResult(self):
        return ''.join(self.result)

def scrubHTML(html, valid=VALID_TAGS, nasty=NASTY_TAGS,
              remove_javascript=True, raise_error=True):

    """ Strip illegal HTML tags from string text.
    """
    parser = StrippingParser(valid=valid, nasty=nasty,
                             remove_javascript=remove_javascript,
                             raise_error=raise_error)
    parser.feed(html)
    parser.close()
    return parser.getResult()
