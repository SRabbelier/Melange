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


from optparse import OptionParser
from vcs_support import util, commandver
import sys

def run(darcsdefault):
    version = '1.1.4'

    parser = OptionParser(usage="usage: %prog [options] vendor_source_dir",
                          version=version)
    parser.add_option("-w", "--wc", dest="wc", default=".",
                      help="Set working copy to WC (defaults to current directory)", metavar="WC")
    parser.add_option("-l", "--log", dest="changelog", metavar="FILE", default=None,
                      help="Get changelog text from FILE")
    parser.add_option("-L", "--log-message", dest="logtext", metavar="TEXT",
                      default='', help="Log with TEXT")
    parser.add_option("-s", "--summary", dest="summary", metavar="MSG",
                      default=None, help="Set log summary message to MSG, overriding the default")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=False, help="Show more status information")
    parser.add_option("-f", "--fs-changes-only", action="store_true",
                      dest="fsonly", default=False,
                      help="Disable interactivity and issue no add/rm/mv commands to VCS, use with -n")
    parser.add_option("-n", "--no-commit", action="store_false", dest="docommit",
                      default=True, help="Do not commit the changes.")

    (options, args) = parser.parse_args()
    util.verbose = options.verbose

    log = options.logtext + "\n"
    if options.changelog:
        fd = open(options.changelog, "r")
        log += fd.read()
        fd.close()

    if len(args) != 1:
        parser.error("Failed to specify a path to import.")

    commandver.setscm(darcsdefault)

    from vcs_support import vcs_wc, vcs_interact

    wc = vcs_wc.wc(options.wc, verbose = options.verbose,
                   fsonly = options.fsonly)
    if not wc.gettaggingmethod() in ['explicit', 'tagline']:
        print "Working directory uses unsupported tagging method %s" % \
              wc.gettaggingmethod()
        sys.exit(1)


    iobj = vcs_interact.interaction(wc, args[0], options.docommit, log = log,
                                    verbose = options.verbose,
                                    summary = options.summary)
    try:
        iobj.main()
    finally:
        iobj.cleanup()
    
