#!/usr/bin/env python
#
"""
Implementation of the command-line front-ends.
"""
# Copyright (C) 2009-2018  University of Zurich. All rights reserved.
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
#

from __future__ import print_function

import sys
import os

from clint.arguments import Args
from clint.textui import puts, colored, indent

__docformat__ = 'reStructuredText'


class ImctoolsScript(cli.app.CommandLineApp):
    def __init__(self, **extra_args):
        super(_Script, self).__init__(**extra_args)
        
