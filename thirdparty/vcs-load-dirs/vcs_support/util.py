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

import os, sys, re

nulldev = None
verbose = 0

class ExecProblem(Exception):
    pass

def mainexec(program, args = [], child_stdout = None,
             child_stdin = None, child_stderr = None, wait = 1, closefds = []):
    """Runs the program as a sub-process, passing to it args if specified.
    The sub-process has its file descriptors adjusted as per the arguments.

    If wait is 1, wait until the child exits, then return the result code from
    os.waitpid().

    If wait is 0, return the PID immediately."""
    global verbose
    def setfds(source, dest):
        if source != None:
            if hasattr(source, 'fileno'):
                source = source.fileno()
            os.dup2(source, dest)
            
    pid = os.fork()
    if not pid:
        if verbose:
            print "Running: ", program, args
        setfds(child_stdin, 0)
        setfds(child_stdout, 1)
        setfds(child_stderr, 2)
        for fd in closefds:
            os.close(fd)
        os.execvp(program, (program,) + tuple(args))
        sys.exit(255)
    else:
        if wait:
            return os.waitpid(pid, 0)[1]
        else:
            return pid

def safeexec(program, args = [], child_stdout = None,
             child_stdin = None, child_stderr = None,
             expected = 0):
    """Calls mainexec() with the appropriate arguments, and raises
    an exception if the program died with a signal or returned an
    error code other than expected.  This function will always wait."""
    result = mainexec(program, args, child_stdout, child_stdin, child_stderr)
    return checkresult(result, expected)

def getstdoutsafeexec(program, args, expected = 0):
    pipes = os.pipe()
    pid = mainexec(program, args, child_stdout = pipes[1], wait  = 0)
    os.close(pipes[1])
    fd = os.fdopen(pipes[0], 'r')
    retval = fd.readlines()
    checkpid(pid, expected)
    os.close(pipes[0])
    return retval

def silentsafeexec(program, args, expected = 0):
    """Silently runs the specified program."""
    null = getnull()
    result = mainexec(program, args, null, null, null)
    return checkresult(result, expected)

def checkresult(result, expected):
    info = []
    if os.WIFSIGNALED(result):
        info.append("got signal %d" % os.WTERMSIG(result))
    if os.WIFEXITED(result):
        info.append("exited with code %d" % os.WEXITSTATUS(result))
    info = ",".join(info)
    if not os.WIFEXITED(result):
        raise ExecProblem, info
    if os.WEXITSTATUS(result) != expected:
        raise ExecProblem, info + " (expected exit code %d)" % expected
    return result

def checkpid(pid, expected):
    return checkresult(os.waitpid(pid, 0)[1], expected)

def getnull():
    global nulldev
    if not nulldev:
        nulldev = open("/dev/null", "w+")
    return nulldev

def chdircmd(newdir, func, *args, **kwargs):
    cwd = os.getcwd()
    os.chdir(newdir)
    try:
        return apply(func, args, kwargs)
    finally:
        os.chdir(cwd)

def maketree(path, addpath = None, ignore = [], res = None):
    thisdir = os.listdir(path)
    retval = []
    others = []
    if res == None:
        res = [re.compile(x) for x in ignore]
    for item in thisdir:
        skip = 0
        for retest in res:
            if retest.search(item):
                skip = 1
                break
        if skip:
            continue
        dirname = os.path.join(path, item)
        if os.path.isdir(dirname) and not os.path.islink(dirname):
            if addpath:
                retval.append(os.path.join(addpath, item) + '/')
            else:
                retval.append(item + '/')
            if addpath:
                newaddpath = os.path.join(addpath, item)
            else:
                newaddpath = item
            others.extend(maketree(dirname, newaddpath, res = res))
        else:
            if addpath:
                retval.append(os.path.join(addpath, item))
            else:
                retval.append(item)
    return sorttree(retval + others)

def sorttree(srctree, filesfirst = False):
    retval = []
    dirs = [x for x in srctree if x.endswith('/')]
    files = [x for x in srctree if not x.endswith('/')]
    dirs.sort()
    files.sort()
    if filesfirst:
        return files + dirs
    else:
        return dirs + files
    
        
def copyfrom(srcdir, destdir):
    pipes = os.pipe()
    verbargs = []
    #if verbose:
    #    verbargs.append('-v')
    readerpid = chdircmd(srcdir, mainexec, "tar", ["-cSpf", "-", "."],
                         child_stdout = pipes[1], wait = 0,
                         closefds = [pipes[0]])
    writerpid = chdircmd(destdir, mainexec, "tar", ["-xSpf", "-"] + verbargs,
                         child_stdin = pipes[0], wait = 0, closefds = [pipes[1]])
    os.close(pipes[0])
    os.close(pipes[1])
    checkpid(readerpid, 0)
    checkpid(writerpid, 0)
    
