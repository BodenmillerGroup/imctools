#! /usr/bin/env python
"""Exceptions specific to the `imctools` package.

In addition to the exceptions listed here, `imctools`:mod: functions
try to use Python builtin exceptions with the same meaning they have
in core Python, namely:

* `TypeError` is raised when an argument to a function or method has an
  incompatible type or does not implement the required protocol (e.g.,
  a number is given where a sequence is expected).

* `ValueError`is  raised when an argument to a function or method has
  the correct type, but fails to satisfy other constraints in the
  function contract (e.g., a positive number is required, and `-1` is
  passed instead).

* `AssertionError` is raised when some internal assumption regarding
  state or function/method calling contract is violated.  Informally,
  this indicates a bug in the software.

"""
# Copyright (C) 2018-2019 University of Zurich. All rights reserved.
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
__docformat__ = 'reStructuredText'

from warnings import warn

## base error classes

class Error(Exception):

    """
    Base class for all error-level exceptions in GC3Pie.

    Generally, this indicates a non-fatal error: depending on the
    nature of the task, steps could be taken to continue, but users
    *must* be aware that an error condition occurred, so the message
    is sent to the logs at the ERROR level.

    Exceptions indicating an error condition after which the program
    cannot continue and should immediately stop, should use the
    `FatalError`:class: base class.
    """

    def __init__(self, msg, do_log=False):
        if do_log:
            gc3libs.log.error(msg)
        Exception.__init__(self, msg)

class RecoverableError(Error):

    """
    Used to mark transient errors: retrying the same action at a later
    time could succeed.

    This exception should *never* be instanciated: it is only to be used
    in `except` clauses to catch "try again" situations.
    """
    pass


class UnrecoverableError(Error):

    """
    Used to mark permanent errors: there's no point in retrying the same
    action at a later time, because it will yield the same error again.

    This exception should *never* be instanciated: it is only to be used
    in `except` clauses to exclude "try again" situations.
    """
    pass


class FatalError(UnrecoverableError):

    """
    A fatal error: execution cannot continue and program should report
    to user and then stop.

    The message is sent to the logs at CRITICAL level
    when the exception is first constructed.

    This is the base class for all fatal exceptions.
    """

    def __init__(self, msg, do_log=True):
        if do_log:
            gc3libs.log.critical(msg)
        Exception.__init__(self, msg)


class AcquisitionError(FatalError):
    """An error with the acquisition"""
    pass
