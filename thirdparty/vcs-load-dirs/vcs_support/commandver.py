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

import util
vcssyn = None
vcsobj = None
vcscmd = None
darcs = False
svk = False
git = False
hg = False

def setscm(x):
    global darcs, svk, git, vcscmd, hg
    if (x == "darcs"):
        vcscmd = "darcs"
        darcs = True
    elif (x == "baz"):
        vcscmd = "baz"
    elif (x == "tla"):
        vcscmd = "tla"
    elif (x == "git"):
        vcscmd = "git"
        git = True
    elif (x == "hg"):
        vcscmd = "hg"
        hg = True
    elif (x == "svk"):
        vcscmd = "svk"
        svk = True
    else:
        print "Failed to determine VCS to use"
        sys.exit(2)
    print " VCSCMD: ", vcscmd

def isdarcs():
    global darcs
    return darcs

def issvk():
    global svk
    return svk

def isgit():
    global git
    return git

def ishg():
    global hg
    return hg

def getvcssyntax():
    global vcssyn, vcsobj
    if vcssyn != None:
        return vcssyn

    if isdarcs():
        vcssyn = 'darcs'
        vcsobj = Darcs()
    elif ishg():
        vcssyn = 'hg'
        vcsobj = Hg()
    elif isgit():
        vcssyn = 'Git'
        vcsobj = Git()
    elif util.getstdoutsafeexec(vcscmd, ['-V'])[0].find('tla-1.0.') != -1:
        vcssyn = '1.0'
        vcsobj = Tla10()
    elif util.getstdoutsafeexec(vcscmd, ['-V'])[0].find('tla-1.1.') != -1:
        vcssyn = '1.1'
        vcsobj = Tla11()
    elif util.getstdoutsafeexec(vcscmd, ['-V'])[0].find('tla-1.3.') != -1:
        vcssyn = '1.3'
        vcsobj = Tla13()
    elif util.getstdoutsafeexec(vcscmd, ['-V'])[0].find('baz Bazaar version 1.4.') != -1:
        vcssyn = 'baz1.4'
        vcsobj = Baz14()        
    elif util.getstdoutsafeexec(vcscmd, ['-V'])[0].find('This is svk') != -1:
        vcssyn = 'svk'
        vcsobj = Svk()
    else:
        vcssyn = '1.3'
        vcsobj = Tla13()
    return vcssyn

class Tla10:
    tagging_method = 'tagging-method'
    add = ['add-tag']
    move = 'move-tag'
    delete = ['delete-tag']
    update = 'update --in-place .'
    replay = 'replay --in-place .'
    commit = 'commit'
    importcmd = 'import'

class Tla11:
    tagging_method = 'id-tagging-method'
    add = ['add']
    move = 'move'
    delete = ['delete']
    update = 'update'
    replay = 'replay'
    commit = 'commit'
    importcmd = 'import'

class Tla13:
    tagging_method = 'id-tagging-method'
    add = ['add-id']
    move = 'move-id'
    delete = ['delete-id']
    update = 'update'
    replay = 'replay'
    commit = 'commit'
    importcmd = 'import'

class Baz14:
    tagging_method = 'id-tagging-method'
    add = ['add-id']
    move = 'move-id'
    delete = ['delete-id']
    update = 'update'
    replay = 'replay'
    commit = 'commit'    
    importcmd = 'import'

class Darcs:
    tagging_method = None
    add = ['add', '--case-ok']
    move = 'mv'
    delete = None
    update = 'pull'
    replay = 'pull'
    commit = 'record'

class Hg:
    tagging_method = None
    add = ['add']
    move = 'mv'
    delete = None
    update = 'pull'
    replay = 'pull'
    commit = 'commit'

class Git:
    tagging_method = None
    add = ['add']
    move = 'mv'
    delete = ['rm', '-r']
    update = 'checkout'
    replay = None 
    commit = 'commit'

class Svk:
	tagging_method = None
	add = ['add']
	move = 'mv'
	delete = ['rm']
	update = 'pull'
	replay = 'pull'
	commit = 'commit'

def cmd():
    global vcsobj
    getvcssyntax()
    return vcsobj
