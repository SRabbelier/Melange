import pstats
import cPickle
import zlib
import re

class PickleStats(object):
    def __init__(self, stats):
        self.stats = stats

    def create_stats(self):
        "pstats.Stats checks for the existence of this method to see if it can load from an object"
        pass

def from_file(fileobj):
    "load ppstats from an open file object"
    stats = cPickle.load(fileobj)
    ps = PickleStats(stats)
    return Stats(ps)

def from_filename(filename):
    "load ppstats from a filename"
    fileobj = open(filename, 'rb')
    return from_file(fileobj)

def from_gz_file(fileobj):
    "load ppstats from an open file containing gzipped data"
    data = fileobj.read()
    stats = cPickle.loads(zlib.decompress(data))
    ps = PickleStats(stats)
    return Stats(ps)

def from_gz_filename(filename):
    "load ppstats from a file containing gzipped data, by filename"
    fileobj = open(filename, 'rb')
    return from_gz_file(fileobj)

def from_gz(gz_string):
    "load ppstats from a string of gzipped data"
    return Stats(PickleStats(cPickle.loads(zlib.decompress(gz_string))))

def from_stats(stats):
    "load ppstats from a stats object" 
    return Stats(PickleStats(stats))

def from_string(stats_string):
    return Stats(PickleStats(cPickle.loads(stats_string)))

class Stats(pstats.Stats):
    def __init__(self, *args, **kwargs):
        pstats.Stats.__init__(self, *args)
        self.replace_dirs = {}
        self.replace_regexes = {}

    def set_output(self, stream):
        "redirect output of print_stats to the file object <stream>"
        self.stream = stream

    def hide_directory(self, dirname, replacement=''):
        "replace occurences of <dirname> in filenames with <replacement>"
        self.replace_dirs[dirname] = replacement
        
    def hide_regex(self, pattern, replacement=''):
        "call re.sub(pattern, replacement) on each filename"
        self.replace_regexes[pattern] = replacement

    def func_strip_path(self, func_name):
        "take a filename, line, name tuple and mangle appropiately"
        filename, line, name = func_name

        for dirname in self.replace_dirs:
            filename = filename.replace(dirname, self.replace_dirs[dirname])

        for pattern in self.replace_regexes:
            filename = re.sub(pattern, self.replace_regexes[pattern], filename)

        return filename, line, name

    def strip_dirs(self):
        "strip irrelevant/redundant directories from filenames in profile data"
        func_std_string = pstats.func_std_string
        add_func_stats = pstats.add_func_stats

        oldstats = self.stats
        self.stats = newstats = {}
        max_name_len = 0
        for func, (cc, nc, tt, ct, callers) in oldstats.iteritems():
            newfunc = self.func_strip_path(func)
            if len(func_std_string(newfunc)) > max_name_len:
                max_name_len = len(func_std_string(newfunc))
            newcallers = {}
            for func2, caller in callers.iteritems():
                newcallers[self.func_strip_path(func2)] = caller

            if newfunc in newstats:
                newstats[newfunc] = add_func_stats(
                                        newstats[newfunc],
                                        (cc, nc, tt, ct, newcallers))
            else:
                newstats[newfunc] = (cc, nc, tt, ct, newcallers)
        old_top = self.top_level
        self.top_level = new_top = {}
        for func in old_top:
            new_top[self.func_strip_path(func)] = None

        self.max_name_len = max_name_len

        self.fcn_list = None
        self.all_callees = None
        return self

    def dump_stats_pickle(self):
        "return a string containing picked stats information (dump_stats uses marshall)"
        return cPickle.dumps(self.stats)

    def load_stats_pickle(self, pickle_string):
        "load from string returned by dump_stats_pickle"
        return self.load_stats(PickleStats(cPickle.load(pickle_string)))
