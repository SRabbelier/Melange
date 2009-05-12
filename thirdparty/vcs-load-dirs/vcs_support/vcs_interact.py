# Copyright (C) 2003-2007 John Goerzen
# <jgoerzen@complete.org>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import sys, os
import util
from commandver import isdarcs
from tempfile import mkdtemp

class interaction:
    def __init__(self, wcobj, importdir, docommit, log = '', verbose = 0,
                 summary = None):
        self.wcobj = wcobj
        self.log = log
        self.docommit = docommit
        self.verb = verbose
        self.summary = summary

        if os.path.isdir(importdir):
            self.importdir = os.path.abspath(importdir)
            self.importfile = None
            self.tmpdir = None

        else:                           # Not a dir, try to unpack an archive.
            self.importfile = os.path.abspath(importdir)
            # mkdtemp returns an absolute path
            self.importdir = mkdtemp("-vcs-load-dirs", ",,unpack-", "..")
            self.tmpdir = self.importdir

            try:
                if self.verb:
                    print "Unpacking archive..."

                if self.importfile.endswith(".tar.gz"):
                    util.chdircmd(self.importdir, util.safeexec, "tar",
                                  ["-zxf", self.importfile])

                elif self.importfile.endswith(".tar.bz2"):
                    util.chdircmd(self.importdir, util.safeexec, "tar",
                                  ["-jxf", self.importfile])
                elif self.importfile.endswith(".zip"):
                    util.chdircmd(self.importdir, util.safeexec, "unzip",
                                  [self.importfile])
                else:
                    raise IOError, "Unknown archive file type"

                # Many tarballs expand into just one single directory.
                # Check to see if that's the case.

                dents = os.listdir(self.importdir)
                if len(dents) == 1 and os.path.isdir(self.importdir + "/" +
                                                     dents[0]):
                    self.importdir = self.importdir + "/" + dents[0]
            except:
                self.cleanup()
                raise

    def cleanup(self):
        if not (self.tmpdir is None):
            util.safeexec("rm", ["-rf", self.tmpdir])
            self.tmpdir = None

    def updateimportfiles(self):
        if self.verb:
            print "Scanning upstream tree..."
        self.importfiles = util.maketree(self.importdir)

    def updatewcfiles(self):
        if self.verb:
            print "Scanning working copy tree..."
        self.wcfiles = self.wcobj.gettree()

    def update(self):
        self.updatewcfiles()
        self.updatechangedfiles()

    def updatechangedfiles(self):
        if self.verb:
            print "Calculating changes..."
        wcfilehash = {}
        for x in self.wcfiles:
            wcfilehash[x] = 1
        importfilehash = {}
        for x in self.importfiles:
            importfilehash[x] = 1
        
        self.addedfiles = [x for x in self.importfiles if not wcfilehash.has_key(x)]
        self.deletedfiles = [x for x in self.wcfiles if not importfilehash.has_key(x)]
        

    def main(self):
        def readloop():
            for command in sys.stdin.readline().strip().split(','):
                command = command.strip()
                if command == 'q':
                    return 0
                if command == 'r':
                    return 1
                src, dest = command.split(' ')
                src = int(src, 16)
                dest = int(dest, 16)
                self.mv(self.deletedfiles[src], self.addedfiles[dest])
            return 1

        self.updateimportfiles()
        needsupdate = 1
        
        while 1:
            self.update()
            if self.wcobj.fsonly:
                # Don't show this interface if we're not talking to the VCS
                break
            if not (len(self.addedfiles) and len(self.deletedfiles)):
                # Just ran update; don't do it again.
                needsupdate = 0
                break

            counter = 0
            print "%3s %-35s %3s %-35s" % ('Num', 'Source Files', 'Num',
                                             'Destination Files',)
            print "%s %s %s %s" % ("-" * 3, "-" * 35, "-" * 3, "-" * 35)
            while counter < max(len(self.addedfiles), len(self.deletedfiles)):
                addfile = ''
                delfile = ''
                if counter < len(self.addedfiles):
                    addfile = self.addedfiles[counter]
                if counter < len(self.deletedfiles):
                    delfile = self.deletedfiles[counter]
                print "%3x %-35s %3x %-35s" % (counter, delfile, counter, addfile)
                counter += 1
            print "Syntax: src dest [,src dest [,...]] to move, q to accept, r to redraw:"
            sys.stdout.write("Command: ")
            sys.stdout.flush()
            try:
                if not readloop():
                    break
            except ValueError:
                print "Error handling input; please try again."
            except IndexError:
                print "Error handling input; please try again."

        self.catchup(needsupdate)
        
    def catchup(self, needsupdate = 1):
        if self.verb:
            print " *** Processing changes."
        if needsupdate:
            self.update()
        if self.verb:
            print "Deleting %d files" % len(self.deletedfiles)
        if isdarcs():
            for file in util.sorttree(self.deletedfiles, filesfirst = True):
                self.delfile(file)
        else:
            for file in self.deletedfiles:
                self.delfile(file)

        if self.verb:
            print "Copying upstream directory to working copy..."
        util.copyfrom(self.importdir, self.wcobj.wcpath)

        if self.verb:
            print "Adding %d files" % len(self.addedfiles)
        self.addedfiles.sort() # Make sure top-level dirs added before files
        for file in self.addedfiles:
            self.addfile(file)
        self.writelog()
        if self.docommit:
            self.wcobj.commit()

    def writelog(self):
        logtext = ""
        if not (self.importfile is None):
            importname = self.importfile
        else:
            importname = self.importdir
            
        if self.summary:
            summary = self.summary
        else:
            summary = "Imported %s" % os.path.basename(importname)
        logtext += "Imported %s\ninto %s\n\n" % \
                   (os.path.basename(importname),
                   self.wcobj.gettreeversion())
        logtext += self.log
        self.wcobj.makelog(summary, logtext)
        

    def addfile(self, file):
        self.wcobj.addtag(file)

    def delfile(self, file):
        self.wcobj.deltag(file)
        self.wcobj.delfile(file)
    
        
    def mv(self, src, dest):
        print "%s -> %s" % (src, dest)
        self.wcobj.movefile(src, dest)
        self.wcobj.movetag(src, dest)

