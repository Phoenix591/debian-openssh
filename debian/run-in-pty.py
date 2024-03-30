#! /usr/bin/python3

# Copyright (C) 2012-2024 Colin Watson <cjwatson@debian.org>.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject
# to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Run a subprocess with a controlling terminal."""

import os
import pty
import select
import sys

pid, master = pty.fork()
if pid == 0:  # child
    os.execvp(sys.argv[1], sys.argv[1:])

# parent
try:
    while True:
        rfds, _, _ = select.select([master], [], [])
        if master in rfds:
            data = os.read(master, 65536)
            # Check for EOF
            if not data:
                break
            os.write(1, data)
except (IOError, OSError):
    pass

pid, status = os.wait()
returncode = 0
if os.WIFSIGNALED(status):
    returncode = -os.WTERMSIG(status)
elif os.WIFEXITED(status):
    returncode = os.WEXITSTATUS(status)
else:
    # Should never happen
    raise RuntimeError("Unknown child exit status!")
os.close(master)
sys.exit(returncode)
