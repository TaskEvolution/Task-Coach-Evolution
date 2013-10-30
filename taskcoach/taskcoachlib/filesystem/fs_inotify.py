'''
Task Coach - Your friendly task manager
Copyright (C) 2011 Task Coach developers <developers@taskcoach.org>

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

# inotify wrapper from this recipe: http://code.activestate.com/recipes/576375-low-level-inotify-wrapper/
# Slightly modified to handle timeout and use select(); cleanup error handling

import os, threading, time, select
from struct import unpack
from fcntl import ioctl
from termios import FIONREAD
from time import sleep
from ctypes import cdll, create_string_buffer, c_int, POINTER
from errno import errorcode
from taskcoachlib.filesystem import base

libc = cdll.LoadLibrary('libc.so.6')
libc.__errno_location.restype = POINTER(c_int)
def geterr():
    return errorcode[libc.__errno_location().contents.value]


class Inotify(object):
    def __init__(self):
        self.fd = libc.inotify_init()
        if self.fd == -1:
            raise OSError('inotify init: %s' % geterr())
        self.fd_read, self.fd_write = os.pipe()
        self.lock = threading.RLock()

    def do_read(self, fd):
        size_int = c_int()
        ioctl(fd, FIONREAD, size_int)
        size = size_int.value
        if size:
            return os.read(fd, size), size
        return None, 0

    def read(self, timeout=None):
        self.lock.acquire()
        try:
            result = []
            fds, _, _ = select.select([self.fd, self.fd_read], [], [], timeout)
            if self.fd in fds:
                data, size = self.do_read(self.fd)
                if size:
                    deb = 0
                    while deb < size:
                        fin = deb + 16
                        wd, mask, cookie, name_len = unpack('iIII', data[deb:fin])
                        deb, fin = fin, fin+name_len
                        name = unpack('%ds' % name_len, data[deb:fin])
                        name = name[0].rstrip('\0')
                        deb = fin
                        result.append((wd, mask, cookie, name))
            if self.fd_read in fds:
                self.do_read(self.fd_read)
            return result
        finally:
            self.lock.release()

    def stop(self):
        os.write(self.fd_write, 'X')

    def add_watch(self, path, mask):
        os.write(self.fd_write, 'X')
        self.lock.acquire()
        try:
            wd = libc.inotify_add_watch(self.fd, path, mask)
            if wd == -1:
                raise OSError('inotify add_watch: %s' % geterr())
            return wd
        finally:
            self.lock.release()

    def rm_watch(self, wd):
        os.write(self.fd_write, 'X')
        self.lock.acquire()
        try:
            ret = libc.inotify_rm_watch(self.fd, wd)
            if ret == -1:
                raise OSError('inotify rm_watch: %s' % geterr())
        finally:
            self.lock.release()

    def close(self):
        os.close(self.fd)
        os.close(self.fd_read)
        os.close(self.fd_write)


FLAGS = {
    'ACCESS'      : 0x00000001, # IN_ACCESS
    'MODIFY'      : 0x00000002, # IN_MODIFY
    'ATTRIB'      : 0x00000004, # IN_ATTRIB
    'WRITE'       : 0x00000008, # IN_CLOSE_WRITE
    'CLOSE'       : 0x00000010, # IN_CLOSE_NOWRITE
    'OPEN'        : 0x00000020, # IN_OPEN
    'MOVED_FROM'  : 0x00000040, # IN_MOVED_FROM
    'MOVED_TO'    : 0x00000080, # IN_MOVED_TO
    'CREATE'      : 0x00000100, # IN_CREATE
    'DELETE'      : 0x00000200, # IN_DELETE
    'DELETE_SELF' : 0x00000400, # IN_DELETE_SELF
    'MOVE_SELF'   : 0x00000800, # IN_MOVE_SELF
    'UNMOUNT'     : 0x00002000, # IN_UNMOUNT
    'Q_OVERFLOW'  : 0x00004000, # IN_Q_OVERFLOW
    'IGNORED'     : 0x00008000, # IN_IGNORED
    'ONLYDIR'     : 0x01000000, # IN_ONLYDIR
    'DONT_FOLLOW' : 0x02000000, # IN_DONT_FOLLOW
    'MASK_ADD'    : 0x20000000, # IN_MASK_ADD
    'ISDIR'       : 0x40000000, # IN_ISDIR
    'ONESHOT'     : 0x80000000, # IN_ONESHOT
}


def mask_str(mask):
    return ' | '.join(name for name, val in FLAGS.items() if val & mask)


class FilesystemNotifier(base.NotifierBase, threading.Thread):
    def __init__(self):
        super(FilesystemNotifier, self).__init__()

        self.wd = None
        self.notifier = Inotify()
        self.cancelled = False
        self.lock = threading.RLock()

        self.setDaemon(True)
        self.start()

    def run(self):
        try:
            while not self.cancelled:
                self.lock.acquire()
                try:
                    myName = self._filename
                finally:
                    self.lock.release()
                if myName is not None:
                    myName = myName.encode('UTF-8')
                    events = self.notifier.read()
                    for _, _, _, name in events:
                        if name == os.path.split(myName)[-1]:
                            if self._check(myName) and myName:
                                self.stamp = os.stat(myName).st_mtime
                                self.onFileChanged()
                                break
        except TypeError:
            # Interpreter termination (we're daemon)
            pass
        except:
            import traceback
            traceback.print_exc()

    def setFilename(self, filename):
        if self.notifier is not None:
            self.lock.acquire()
            try:
                if self.wd is not None:
                    self.notifier.rm_watch(self.wd)
                    self.wd = None
                super(FilesystemNotifier, self).setFilename(filename)
                if self._filename:
                    self.wd = self.notifier.add_watch(self._path.encode('UTF-8'),
                                FLAGS['MODIFY']|FLAGS['MOVED_TO'])
            finally:
                self.lock.release()

    def stop(self):
        if self.notifier is not None:
            self.cancelled = True
            self.notifier.stop()
            self.join()
            self.notifier.close()
            self.notifier = None

    def onFileChanged(self):
        raise NotImplementedError
