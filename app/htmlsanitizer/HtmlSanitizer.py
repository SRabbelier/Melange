# -*- coding: UTF-8 -*-
import safe_html

class Cleaner(object):
    
    def __init__(self, auto_clean=False):
        self.auto_clean = auto_clean
        self.dirty = None
    
    def _set_string(self, value):
        self._string = value
        self.dirty = True
    
    def _get_string(self):
        if self.auto_clean and self.dirty:
            self.clean()
            self.dirty = False
        return self._string
    
    string = property(_get_string, _set_string)
    
    def clean(self):
        self._string = safe_html.scrubHTML(self._string)
