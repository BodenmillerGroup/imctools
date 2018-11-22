#! /usr/bin/env python
#
"""
This is the main entry point for command `gc3utils`:command: -- a
simple command-line frontend to distributed resources

This is a generic front-end code; actual implementation of commands
can be found in `gc3utils.commands`:mod:
"""
# Copyright (C) 2009-2012  University of Zurich. All rights reserved.
#
# Includes parts adapted from the ``bzr`` code, which is
# copyright (C) 2005, 2006, 2007, 2008, 2009 Canonical Ltd
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA


# stdlib imports
import os
import os.path
import sys

def usage():
    """
    Should print out the list of all
    supported scripts.
    """

def main():
    """
    Generic front-end function to invoke the commands in `gc3utils/commands.py`
    """

    # program name
    PROG = os.path.basename(sys.argv[0])

    # find command as function in the `commands.py` module
    PROG.replace('-', '_')
    import imctools.scripts.scripts
    try:
        cmd = getattr(imctools.scripts.scripts, 'run_' + PROG)
    except AttributeError:
        sys.stderr.write(
            "Cannot find command '%s' in imctools.script; aborting now.\n" % PROG)
        return 1
    rc = cmd().run()
    return rc
