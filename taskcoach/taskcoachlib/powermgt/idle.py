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

import sys, threading, time
from taskcoachlib import operating_system
from ctypes import *


#==============================================================================
# Linux/BSD

if operating_system.isGTK():
    class XScreenSaverInfo(Structure):
        _fields_ = [('window', c_ulong),
                    ('state', c_int),
                    ('kind', c_int),
                    ('til_or_since', c_ulong),
                    ('idle', c_ulong),
                    ('event_mask', c_ulong)]

    class LinuxIdleQuery(object):
        def __init__(self):
            _x11 = CDLL('libX11.so.6')

            self.XOpenDisplay = CFUNCTYPE(c_ulong, c_char_p)(('XOpenDisplay', _x11))
            self.XCloseDisplay = CFUNCTYPE(c_int, c_ulong)(('XCloseDisplay', _x11))
            self.XRootWindow = CFUNCTYPE(c_ulong, c_ulong, c_int)(('XRootWindow', _x11))

            self.dpy = self.XOpenDisplay(None)

            _xss = CDLL('libXss.so.1')

            self.XScreenSaverAllocInfo = CFUNCTYPE(POINTER(XScreenSaverInfo))(('XScreenSaverAllocInfo', _xss))
            self.XScreenSaverQueryInfo = CFUNCTYPE(c_int, c_ulong, c_ulong, POINTER(XScreenSaverInfo))(('XScreenSaverQueryInfo', _xss))

            self.info = self.XScreenSaverAllocInfo()

        def __del__(self):
            self.XCloseDisplay(self.dpy)

        def getIdleSeconds(self):
            self.XScreenSaverQueryInfo(self.dpy, self.XRootWindow(self.dpy, 0), self.info)
            return 1.0 * self.info.contents.idle / 1000

    IdleQuery = LinuxIdleQuery

elif operating_system.isWindows():
    class LASTINPUTINFO(Structure):
        _fields_ = [('cbSize', c_uint), ('dwTime', c_uint)]

    class WindowsIdleQuery(object):
        def __init__(self):
            self.GetTickCount = windll.kernel32.GetTickCount
            self.GetLastInputInfo = windll.user32.GetLastInputInfo

            self.lastInputInfo = LASTINPUTINFO()
            self.lastInputInfo.cbSize = sizeof(self.lastInputInfo)

        def getIdleSeconds(self):
            self.GetLastInputInfo(byref(self.lastInputInfo))
            return (1.0 * self.GetTickCount() - self.lastInputInfo.dwTime) / 1000

    IdleQuery = WindowsIdleQuery

elif operating_system.isMac():
    # When running from source, select the right binary...

    if not hasattr(sys, 'frozen'):
        import struct, os

        if struct.calcsize('L') == 8:
            _subdir = 'ia64'
        else:
            _subdir = 'ia32'

        sys.path.insert(0, os.path.join(os.path.split(__file__)[0],
                                        '..', '..', 'extension', 'macos', 'bin-%s' % _subdir))

    import _idle
    class MacIdleQuery(_idle.Idle):
        def getIdleSeconds(self):
            return self.get()

    IdleQuery = MacIdleQuery


#==============================================================================
#

class IdleNotifier(IdleQuery):
    STATE_NONE            = 0
    STATE_IDLE            = 1
    STATE_OFF             = 0x80 # Used as bitmask

    def __init__(self):
        super(IdleNotifier, self).__init__()

        self.state = self.STATE_NONE
        self.lastActivity = time.time()
        self.evtStop = threading.Event()

        self.thr = threading.Thread(target=self._run)
        self.thr.setDaemon(True)
        self.thr.start()

    def stop(self):
        self.evtStop.set()
        self.thr.join()

    def poweroff(self):
        """
        Call this when the computer goes to sleep.
        """
        self.state |= self.STATE_OFF

    def poweron(self):
        """
        Call this when the computer resumes from sleep.
        """
        if self.state & self.STATE_OFF:
            self.state &= ~self.STATE_OFF
            if self.getMinIdleTime() != 0 and time.time() - self.lastActivity >= self.getMinIdleTime():
                if self.state == self.STATE_NONE:
                    self.sleep()
                self.wake()

            self.lastDelta = 0
            self.lastActivity = time.time()
            self.state = self.STATE_NONE

    def getMinIdleTime(self):
        """
        Should return the minimum time in seconds before going idle.
        """
        raise NotImplementedError

    def sleep(self):
        """
        Called when the min idle time has elapsed without any user
        input.
        """

    def wake(self):
        """
        Called when the computer is not idle any more.
        """

    def _run(self):
        while not self.evtStop.isSet():
            if self.state == self.STATE_NONE:
                delta = self.getIdleSeconds()
                self.lastActivity = time.time() - delta
                self.lastDelta = delta
                if self.getMinIdleTime() != 0 and delta >= self.getMinIdleTime():
                    self.state = self.STATE_IDLE
                    self.sleep()
            elif self.state == self.STATE_IDLE:
                delta = self.getIdleSeconds()
                if delta < self.lastDelta:
                    self.state = self.STATE_NONE
                    self.wake()
                    self.lastActivity = time.time() - delta
                    self.lastDelta = delta

            # Ideally this would be self.evtStop.wait(1) but on some
            # platforms it's a busy wait.
            time.sleep(1)


if __name__ == '__main__':
    class Test(IdleNotifier):
        def getMinIdleTime(self):
            return 10

        def sleep(self):
            print 'Going idle'

        def wake(self):
            print 'Waking'

    test = Test()
    raw_input('...')

    test.stop()
