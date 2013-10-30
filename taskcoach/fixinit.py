'''
Task Coach - Your friendly task manager
Copyright (C) 2012 Task Coach developers <developers@taskcoach.org>

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

import os


def visitDir(arg, dirname, names):
    try:
        names.remove('.svn')
    except:
        pass

    for name in names:
        if name == '__init__.py':
            fname = os.path.join(dirname, name)
            if os.stat(fname).st_size == 0:
                file(fname, 'wb').write('# Make this a package\n')


if __name__ == '__main__':
    os.path.walk(os.path.join('taskcoachlib', 'thirdparty'), visitDir, None)
