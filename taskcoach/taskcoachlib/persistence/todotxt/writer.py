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

import re
from taskcoachlib.domain import date


class TodoTxtWriter(object):
    def __init__(self, fd, filename):
        self.__fd = fd
        self.__filename = filename
        self.__maxDateTime = date.DateTime()
        
    def write(self, viewer, settings, selectionOnly, **kwargs):
        tasks = viewer.visibleItems()
        if selectionOnly:
            tasks = [task for task in tasks if viewer.isselected(task)]
        return self.writeTasks(tasks)
    
    def writeTasks(self, tasks):
        count = 0
        for task in tasks:
            count += 1
            self.__fd.write(self.priority(task.priority()) + \
                            self.completionDate(task.completionDateTime()) + \
                            self.startDate(task.plannedStartDateTime()) + \
                            task.subject(recursive=True) + \
                            self.contextsAndProjects(task) + \
                            self.dueDate(task.dueDateTime()) + '\n')
        return count
                
    @staticmethod
    def priority(priorityNumber):
        return '(%s) '%chr(ord('A') + priorityNumber - 1) if 1 <= priorityNumber <= 26 else ''

    @classmethod
    def startDate(cls, plannedStartDateTime):
        return '%s '%cls.dateTime(plannedStartDateTime) if cls.isActualDateTime(plannedStartDateTime) else ''
    
    @classmethod
    def dueDate(cls, dueDateTime):
        return ' due:%s'%cls.dateTime(dueDateTime) if cls.isActualDateTime(dueDateTime) else ''
        
    @classmethod
    def completionDate(cls, completionDateTime):
        return 'X ' + '%s '%cls.dateTime(completionDateTime) if cls.isActualDateTime(completionDateTime) else ''
        
    @staticmethod
    def dateTime(dateTime):
        ''' Todo.txt doesn't support time, just dates, so ignore the time part. '''
        return dateTime.date().strftime('%Y-%m-%d')

    @staticmethod
    def isActualDateTime(dateTime, maxDateTime=date.DateTime()):
        return dateTime != maxDateTime

    @classmethod
    def contextsAndProjects(cls, task):
        subjects = []
        for category in task.categories():
            subject = category.subject(recursive=True).strip()
            if subject and subject[0] in ('@', '+'):
                subject = re.sub(r' -> ', '->', subject)
                subject = re.sub(r'\s+', '_', subject)
                subjects.append(subject)
        return ' ' + ' '.join(sorted(subjects)) if subjects else ''
