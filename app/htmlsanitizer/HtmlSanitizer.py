# -*- coding: UTF-8 -*-
"""
some input filters, for regularising the html fragments from screen scraping and 
browser-based editors into some semblance of sanity

TODO: turn the messy setting[method_name]=True filter syntax into a list of cleaning methods to invoke, so that they can be invoked in a specific order and multiple times.

AUTHORS:
Dan MacKinlay - https://launchpad.net/~dan-possumpalace
Collin Grady - http://launchpad.net/~collin-collingrady
Andreas Gustafsson - https://bugs.launchpad.net/~gson
Håkan W - https://launchpad.net/~hwaara-gmail
"""

import BeautifulSoup
import re
import sys

# Python 2.4 compatibility
try: any
except NameError:
    def any(iterable):
        for element in iterable:
            if element:
                return True
        return False

"""
html5lib compatibility. Basically, we need to know that this still works whether html5lib
is imported or not. Should run complete suites of tests for both possible configs -
or test in virtual environments, but for now a basic sanity check will do.
>>> if html5:
>>>     c=Cleaner(html5=False)
>>>     c(u'<p>foo</p>)
u'<p>foo</p>'
"""
try:
    import html5lib
    from html5lib import sanitizer, treebuilders
    parser = html5lib.HTMLParser(
        tree=treebuilders.getTreeBuilder("beautifulsoup"),
        tokenizer=sanitizer.HTMLSanitizer
    )
    html5 = True
except ImportError:
    html5 = False

ANTI_JS_RE=re.compile('j\s*a\s*v\s*a\s*s\s*c\s*r\s*i\s*p\s*t\s*:', re.IGNORECASE)
#These tags and attrs are sufficently liberal to let microformats through...
#it ruthlessly culls all the rdf, dublin core metadata and so on.
valid_tags = dict.fromkeys('p i em strong b u a h1 h2 h3 pre abbr br img dd dt ol ul li span sub sup ins del blockquote table tr td th address cite'.split()) #div?
valid_attrs = dict.fromkeys('href src rel title'.split())
valid_schemes = dict.fromkeys('http https'.split())
elem_map = {'b' : 'strong', 'i': 'em'}
attrs_considered_links = dict.fromkeys("src href".split()) #should include
#courtesy http://developer.mozilla.org/en/docs/HTML:Block-level_elements
block_elements = dict.fromkeys(["p", "h1","h2", "h3", "h4", "h5", "h6", "ol", "ul", "pre", "address", "blockquote", "dl", "div", "fieldset", "form", "hr", "noscript", "table"])

#convenient default filter lists.
paranoid_filters = ["strip_comments", "strip_tags", "strip_attrs",
  "strip_schemes", "rename_tags", "wrap_string", "strip_empty_tags", "strip_empty_tags", ]
complete_filters = ["strip_comments", "rename_tags", "strip_tags", "strip_attrs",
    "strip_cdata", "strip_schemes",  "wrap_string", "strip_empty_tags", "rebase_links", "reparse"]

#set some conservative default string processings
default_settings = {
    "filters" : paranoid_filters,
    "block_elements" : block_elements, #xml or None for a more liberal version
    "convert_entities" : "html", #xml or None for a more liberal version
    "valid_tags" : valid_tags,
    "valid_attrs" : valid_attrs,
    "valid_schemes" : valid_schemes,
    "attrs_considered_links" : attrs_considered_links,
    "elem_map" : elem_map,
    "wrapping_element" : "p",
    "auto_clean" : False,
    "original_url" : "",
    "new_url" : "",
    "html5" : html5
}
#processes I'd like but haven't implemented            
#"encode_xml_specials", "ensure complete xhtml doc", "ensure_xhtml_fragment_only"
# and some handling of permitted namespaces for tags. for RDF, say. maybe.

XML_ENTITIES = { u"'" : u"&apos;",
                 u'"' : u"&quot;",
                 u"&" : u"&amp;",
                 u"<" : u"&lt;",
                 u">" : u"&gt;"
               }
LINE_EXTRACTION_RE = re.compile(".+", re.MULTILINE)
BR_EXTRACTION_RE = re.compile("</?br ?/?>", re.MULTILINE)

class Stop:
    """
    handy class that we use as a stop input for our state machine in lieu of falling
    off the end of lists
    """
    pass


class Cleaner(object):
    r"""
    powerful and slow arbitrary HTML sanitisation. can deal (i hope) with most XSS
    vectors and layout-breaking badness.
    Probably overkill for content from trusted sources; defaults are accordingly
    set to be paranoid.
    >>> bad_html = '<p style="forbidden markup"><!-- XSS attach -->content</p'
    >>> good_html = u'<p>content</p>'
    >>> c = Cleaner()
    >>> c.string = bad_html
    >>> c.clean()
    >>> c.string == good_html
    True
    
    Also supports shorthand syntax:
    >>> c = Cleaner()
    >>> c(bad_html) == c(good_html)
    True
    """
    
    def __init__(self, string_or_soup="", *args,  **kwargs):
        self.settings=default_settings.copy()
        self.settings.update(kwargs)
        if args :
            self.settings['filters'] = args
        super(Cleaner, self).__init__(string_or_soup, *args, **kwargs)
        self.string = string_or_soup
    
    def __call__(self, string = None, **kwargs):
        """
        convenience method allowing one-step calling of an instance and returning
        a cleaned string.
        
        TODO: make this method preserve internal state- perhaps by creating a new
        instance.
        
        >>> s = 'input string'
        >>> c1 = Cleaner(s, auto_clean=True)
        >>> c2 = Cleaner("")
        >>> c1.string == c2(s)
        True
        
        """
        self.settings.update(kwargs)
        if not string == None :
            self.string = string
        self.clean()
        return self.string
    
    def _set_contents(self, string_or_soup):
        if isinstance(string_or_soup, BeautifulSoup.BeautifulSoup) :
            self._set_soup(string_or_soup)
        else :
            self._set_string(string_or_soup)
    
    def _set_string(self, html_fragment_string):
        if self.settings['html5']:
            s = parser.parse(html_fragment_string).body
        else:
            s = BeautifulSoup.BeautifulSoup(
                    html_fragment_string,
                    convertEntities=self.settings['convert_entities'])
        self._set_soup(s)
        
    def _set_soup(self, soup):
        """
        Does all the work of set_string, but bypasses a potential autoclean to avoid 
        loops upon internal string setting ops.
        """
        self._soup = BeautifulSoup.BeautifulSoup(
            '<rootrootroot></rootrootroot>'
        )
        self.root=self._soup.contents[0]
        
        if len(soup.contents) :
            backwards_soup = [i for i in soup.contents]
            backwards_soup.reverse()
        else :
            backwards_soup = []
        for i in backwards_soup :
            i.extract()
            self.root.insert(0, i)
    
    def set_string(self, string) :
        ur"""
            sets the string to process and does the necessary input encoding too
        really intended to be invoked as a property.
        note the godawful rootrootroot element which we need because the
        BeautifulSoup object has all the same methods as a Tag, but
        behaves differently, silently failing on some inserts and appends
        
        >>> c = Cleaner(convert_entities="html")
        >>> c.string = '&eacute;'
        >>> c.string
        u'\xe9'
        >>> c = Cleaner(convert_entities="xml")
        >>> c.string = u'&eacute;'
        >>> c.string
        u'&eacute;'
        """
        self._set_string(string)
        if len(string) and self.settings['auto_clean'] : self.clean()
        
    def get_string(self):
        return unicode(self.root.renderContents())
    
    string = property(get_string, set_string)
    
    def clean(self):
        """
        invoke all cleaning processes stipulated in the settings
        """
        for method in self.settings['filters'] :
            try :
                getattr(self, method)()
            except NotImplementedError :
                sys.stderr.write('Warning, called unimplemented method %s' % method + '\n')
    
    def strip_comments(self):
        r"""
        XHTML comments are used as an XSS attack vector. they must die.
        
        >>> c = Cleaner("", "strip_comments")
        >>> c('<p>text<!-- comment --> More text</p>')
        u'<p>text More text</p>'
        """
        for comment in self.root.findAll(
            text = lambda text: isinstance(text, BeautifulSoup.Comment)):
            comment.extract()
            
    def strip_cdata(self):
        for cdata in self.root.findAll(
          text = lambda text: isinstance(text, BeautifulSoup.CData)):
            cdata.extract()
    
    def strip_tags(self):
        r"""
        ill-considered tags break our layout. they must die.
        >>> c = Cleaner("", "strip_tags", auto_clean=True)
        >>> c.string = '<div>A <strong>B C</strong></div>'
        >>> c.string
        u'A <strong>B C</strong>'
        >>> c.string = '<div>A <div>B C</div></div>'
        >>> c.string
        u'A B C'
        >>> c.string = '<div>A <br /><div>B C</div></div>'
        >>> c.string
        u'A <br />B C'
        >>> c.string = '<p>A <div>B C</div></p>'
        >>> c.string
        u'<p>A B C</p>'
        >>> c.string = 'A<div>B<div>C<div>D</div>E</div>F</div>G'
        >>> c.string
        u'ABCDEFG'
        >>> c.string = '<div>B<div>C<div>D</div>E</div>F</div>'
        >>> c.string
        u'BCDEF'
        """
        # Beautiful Soup doesn't support dynamic .findAll results when the tree is
        # modified in place.
        # going backwards doesn't seem to help.
        # so find one at a time
        while True :
            next_bad_tag = self.root.find(
              lambda tag : not tag.name in (self.settings['valid_tags'])
            )
            if next_bad_tag :                
                self.disgorge_elem(next_bad_tag)
            else:
                break
    
    def strip_attrs(self):
        """
        preserve only those attributes we need in the soup
        >>> c = Cleaner("", "strip_attrs")
        >>> c('<div title="v" bad="v">A <strong title="v" bad="v">B C</strong></div>')
        u'<div title="v">A <strong title="v">B C</strong></div>'
        """
        for tag in self.root.findAll(True):
            tag.attrs = [(attr, val) for attr, val in tag.attrs
                         if attr in self.settings['valid_attrs']]
    
    def _all_links(self):
        """
        finds all tags with link attributes sequentially. safe against modification
        of said attributes in-place.
        """
        start = self.root
        while True: 
            tag = start.findNext(
              lambda tag : any(
                [(tag.get(i) for i in self.settings['attrs_considered_links'])]
              ))
            if tag: 
                start = tag
                yield tag
            else :
                break
            
    def strip_schemes(self):
        """
        >>> c = Cleaner("", "strip_schemes")
        >>> c('<img src="javascript:alert();" />')
        u'<img />'
        >>> c('<a href="javascript:alert();">foo</a>')
        u'<a>foo</a>'
        """
        for tag in self._all_links() :
            for key in self.settings['attrs_considered_links'] :
                scheme_bits = tag.get(key, u"").split(u':',1)
                if len(scheme_bits) == 1 : 
                    pass #relative link
                else:
		    if not scheme_bits[0] in self.settings['valid_schemes'] :
			del(tag[key])
    
    def br_to_p(self):
        """
        >>> c = Cleaner("", "br_to_p")
        >>> c('<p>A<br />B</p>')
        u'<p>A</p><p>B</p>'
        >>> c('A<br />B')
        u'<p>A</p><p>B</p>'
        """
        block_elems = self.settings['block_elements']
        block_elems['br'] = None
        block_elems['p'] = None
        
        while True :
            next_br = self.root.find('br')
            if not next_br: break
            parent = next_br.parent
            self.wrap_string('p', start_at=parent, block_elems = block_elems)
            while True:
                useless_br=parent.find('br', recursive=False)
                if not useless_br: break
                useless_br.extract()        
            if parent.name == 'p':
                self.disgorge_elem(parent)
    
    def rename_tags(self):
        """
        >>> c = Cleaner("", "rename_tags", elem_map={'i': 'em'})
        >>> c('<b>A<i>B</i></b>')
        u'<b>A<em>B</em></b>'
        """
        for tag in self.root.findAll(self.settings['elem_map']) :
            tag.name = self.settings['elem_map'][tag.name]
        
    def wrap_string(self, wrapping_element = None, start_at=None, block_elems=None):
        """
        takes an html fragment, which may or may not have a single containing element,
        and guarantees what the tag name of the topmost elements are.
        TODO: is there some simpler way than a state machine to do this simple thing?
        >>> c = Cleaner("", "wrap_string")
        >>> c('A <strong>B C</strong>D')
        u'<p>A <strong>B C</strong>D</p>'
        >>> c('A <p>B C</p>D')
        u'<p>A </p><p>B C</p><p>D</p>'
        """
        if not start_at : start_at = self.root
        if not block_elems : block_elems = self.settings['block_elements']
        e = (wrapping_element or self.settings['wrapping_element'])
        paragraph_list = []
        children = [elem for elem in start_at.contents]
        children.append(Stop())
        
        last_state = 'block'
        paragraph = BeautifulSoup.Tag(self._soup, e)
        
        for node in children :
            if isinstance(node, Stop) :
                state = 'end'
            elif hasattr(node, 'name') and node.name in block_elems:
                state = 'block'
            else:
                state = 'inline'
                
            if last_state == 'block' and state == 'inline':
                #collate inline elements
                paragraph = BeautifulSoup.Tag(self._soup, e)
                
            if state == 'inline' :
                paragraph.append(node)
                
            if ((state <> 'inline') and last_state == 'inline') :
                paragraph_list.append(paragraph)
                
            if state == 'block' :
                paragraph_list.append(node)
            
            last_state = state
        
        #can't use append since it doesn't work on empty elements...
        paragraph_list.reverse()
        for paragraph in paragraph_list:
            start_at.insert(0, paragraph)
        
    def strip_empty_tags(self):
        """
        strip out all empty tags
        TODO: depth-first search
        >>> c = Cleaner("", "strip_empty_tags")
        >>> c('<p>A</p><p></p><p>B</p><p></p>')
        u'<p>A</p><p>B</p>'
        >>> c('<p><a></a></p>')
        u'<p></p>'
        """
        tag = self.root
        while True:
            next_tag = tag.findNext(True)
            if not next_tag: break
            if next_tag.contents or next_tag.attrs:
                tag = next_tag
                continue
            next_tag.extract()
        
    def rebase_links(self, original_url="", new_url ="") :
        if not original_url : original_url = self.settings.get('original_url', '')
        if not new_url : new_url = self.settings.get('new_url', '')
        raise NotImplementedError
    
    # Because of its internal character set handling,
    # the following will not work in Beautiful soup and is hopefully redundant.
    # def encode_xml_specials(self, original_url="", new_url ="") :
    #     """
    #     BeautifulSoup will let some dangerous xml entities hang around
    #     in the navigable strings. destroy all monsters.
    #     >>> c = Cleaner(auto_clean=True, encode_xml_specials=True)
    #     >>> c('<<<<<')
    #     u'&lt;&lt;&lt;&lt;'
    #     """
    #     for string in self.root.findAll(text=True) :
    #         sys.stderr.write("root" +"\n")
    #         sys.stderr.write(str(self.root) +"\n")
    #         sys.stderr.write("parent" +"\n")
    #         sys.stderr.write(str(string.parent) +"\n")
    #         new_string = unicode(string)
    #         sys.stderr.write(string +"\n")
    #         for special_char in XML_ENTITIES.keys() :
    #             sys.stderr.write(special_char +"\n")
    #         string.replaceWith(
    #           new_string.replace(special_char, XML_ENTITIES[special_char])
    #         )
        
        
    def disgorge_elem(self, elem):
        """
        remove the given element from the soup and replaces it with its own contents
        actually tricky, since you can't replace an element with an list of elements
        using replaceWith
        >>> disgorgeable_string = '<body>A <em>B</em> C</body>'
        >>> c = Cleaner()
        >>> c.string = disgorgeable_string
        >>> elem = c._soup.find('em')
        >>> c.disgorge_elem(elem)
        >>> c.string
        u'<body>A B C</body>'
        >>> c.string = disgorgeable_string
        >>> elem = c._soup.find('body')
        >>> c.disgorge_elem(elem)
        >>> c.string
        u'A <em>B</em> C'
        >>> c.string = '<div>A <div id="inner">B C</div></div>'
        >>> elem = c._soup.find(id="inner")
        >>> c.disgorge_elem(elem)
        >>> c.string
        u'<div>A B C</div>'
        """
        if elem == self.root :
            raise AttributeError, "Can't disgorge root"  
                      
        # With in-place modification, BeautifulSoup occasionally can return
        # elements that think they are orphans
        # this lib is full of workarounds, but it's worth checking
        parent = elem.parent
        if parent == None: 
            raise AttributeError, "AAAAAAAAGH! NO PARENTS! DEATH!"
        
        i = None
        for i in range(len(parent.contents)) :
            if parent.contents[i] == elem :
                index = i
                break
                
        elem.extract()
        
        #the proceeding method breaks horribly, sporadically.
        # for i in range(len(elem.contents)) :
        #     elem.contents[i].extract()
        #     parent.contents.insert(index+i, elem.contents[i])
        # return
        self._safe_inject(parent, index, elem.contents)
        
    def _safe_inject(self, dest, dest_index, node_list):
        #BeautifulSoup result sets look like lists but don't behave right
        # i.e. empty ones are still True,
        if not len(node_list) : return
        node_list = [i for i in node_list]
        node_list.reverse()
        for i in node_list :
            dest.insert(dest_index, i)

        
class Htmlator(object) :
    """
    converts a string into a series of html paragraphs
    """
    settings = {
        "encode_xml_specials" : True,
        "is_plaintext" : True,
        "convert_newlines" : False,
        "make_links" : True,
        "auto_convert" : False,
        "valid_schemes" : valid_schemes,
    }
    def __init__(self, string = "",  **kwargs):
        self.settings.update(kwargs)
        super(Htmlator, self).__init__(string, **kwargs)
        self.string = string
    
    def _set_string(self, string):
        self.string = string
        if self.settings['auto_convert'] : self.convert()
        
    def _get_string(self):
        return unicode(self._soup)
    
    string = property(_get_string, _set_string)
    
    def __call__(self, string):
        """
        convenience method supporting one-step calling of an instance
        as a string cleaning function
        """
        self.string = string
        self.convert()
        return self.string
        
    def convert(self):
        for method in ["encode_xml_specials", "convert_newlines",
          "make_links"] :
            if self.settings(method) :
                getattr(self, method)()
    
    def encode_xml_specials(self) :
        for char in XML_ENTITIES.keys() :
            self.string.replace(char, XML_ENTITIES[char])
        
    def make_links(self):
        raise NotImplementedError
        
    def convert_newlines(self) :
        self.string = ''.join([
            '<p>' + line + '</p>' for line in LINE_EXTRACTION_RE.findall(self.string)
        ])
        
def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()


# def cast_input_to_soup(fn):
#     """
#     Decorate function to handle strings as BeautifulSoups transparently
#     """
#     def stringy_version(input, *args, **kwargs) :
#         if not isinstance(input,BeautifulSoup) :
#             input=BeautifulSoup(input)
#         return fn(input, *args, **kwargs)
#     return stringy_version
