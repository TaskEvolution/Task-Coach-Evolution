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

import test, wx
from taskcoachlib.domain import date


class SchedulerTest(test.TestCase):    
    def setUp(self):
        super(SchedulerTest, self).setUp()
        self.scheduler = date.Scheduler()

    def callback(self):
        pass
        
    def testScheduleAtDateTime(self):
        futureDate = date.Tomorrow()
        self.scheduler.schedule(self.callback, futureDate)
        self.failUnless(self.scheduler.is_scheduled(self.callback))
        self.scheduler._process_jobs(futureDate)
        wx.Yield()
        self.failIf(self.scheduler.is_scheduled(self.callback))

    def testUnschedule(self):
        futureDate = date.Tomorrow()
        self.scheduler.schedule(self.callback, futureDate)
        self.scheduler.unschedule(self.callback)
        self.failIf(self.scheduler.is_scheduled(self.callback))
        self.scheduler._process_jobs(futureDate)
        wx.Yield()

    def testScheduleAtPastDateTime(self):
        pastDate = date.Yesterday()
        self.scheduler.schedule(self.callback, pastDate)
        self.failIf(self.scheduler.is_scheduled(self.callback))
        self.scheduler._process_jobs(pastDate)
        wx.Yield()
        self.failIf(self.scheduler.is_scheduled(self.callback))
