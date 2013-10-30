#!/usr/bin/python

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>

Task Coach is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Task Coach is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import os, shutil


def nuke():
    sin, sout = os.popen4('svn st --no-ignore')

    for line in sout:
        if line.startswith('?') or line.startswith('I'):
            filename = line[7:].strip()
            if filename != '.buildbot-sourcedata':
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
                print 'Removed', filename

    sout.close()
    sin.close()


if __name__ == '__main__':
    nuke()
