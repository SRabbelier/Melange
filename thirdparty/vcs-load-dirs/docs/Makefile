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
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

MASTERBASE := vcs_load_dirs
TOPNODE := vcs_load_dirs
BASICDEPS := $(MASTERBASE).sgml
#DOINDEX := yes
DOINDEX := no
HTMLARGS := -s local
PSARGS := -s local=printlocal

all: ps
ps: $(MASTERBASE).ps
html: html/index.html
text: $(MASTERBASE).txt

manpages: tla_load_dirs.1 darcs_load_dirs.1 baz_load_dirs.1 svk_load_dirs.1 git_load_dirs.1 hg_load_dirs.1
%.1: %.sgml
	docbook2man $<

darcs_load_dirs.1: vcs_load_dirs.1
	sed -e s/vcs_load_dirs/darcs_load_dirs/g \
	    -e s/VCS_LOAD_DIRS/DARCS_LOAD_DIRS/g < $< > $@

hg_load_dirs.1: vcs_load_dirs.1
	sed -e s/vcs_load_dirs/hg_load_dirs/g \
	    -e s/VCS_LOAD_DIRS/HG_LOAD_DIRS/g < $< > $@

tla_load_dirs.1: vcs_load_dirs.1
	sed -e s/vcs_load_dirs/tla_load_dirs/g \
	    -e s/VCS_LOAD_DIRS/TLA_LOAD_DIRS/g < $< > $@

baz_load_dirs.1: vcs_load_dirs.1
	sed -e s/vcs_load_dirs/baz_load_dirs/g \
	    -e s/VCS_LOAD_DIRS/BAZ_LOAD_DIRS/g < $< > $@

svk_load_dirs.1: vcs_load_dirs.1
	sed -e s/vcs_load_dirs/svk_load_dirs/g \
		-e s/VCS_LOAD_DIRS/SVK_LOAD_DIRS/g < $< > $@

git_load_dirs.1: vcs_load_dirs.1
	sed -e s/vcs_load_dirs/git_load_dirs/g \
		-e s/VCS_LOAD_DIRS/GIT_LOAD_DIRS/g < $< > $@

include sgml-common/Makefile.common

realclean: clean
	-rm -rf *.links *.refs *.1
