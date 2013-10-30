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

import re, codecs
from taskcoachlib.domain import task, category, date
from taskcoachlib import patterns


class TodoTxtReader(object):
    def __init__(self, taskList, categoryList):
        self.__taskList = taskList
        self.__tasksBySubject = self.__createSubjectCache(taskList)
        self.__categoryList = categoryList
        self.__categoriesBySubject = self.__createSubjectCache(categoryList)

    def read(self, filename):
        with codecs.open(filename, 'r', 'utf-8') as fp:
            self.readFile(fp)
    
    @patterns.eventSource    
    def readFile(self, fp, now=date.Now, event=None):
        todoTxtRE = self.compileTodoTxtRE()
        keyValueRE = self.compileKeyValueRE()
        for line in fp:
            line = line.strip()
            if line:
                self.processLine(line, todoTxtRE, keyValueRE, now, event)
            
    def processLine(self, line, todoTxtRE, keyValueRE, now, event):
        # First, process all key:value pairs. These are additional metadata not
        # defined by the todo.txt format  at
        # https://github.com/ginatrapani/todo.txt-cli/wiki/The-Todo.txt-Format
        dueDateTime = date.DateTime()
        for key, value in re.findall(keyValueRE, line):
            if key == 'due':
                dueDateTime = self.dateTime(value)
        line = re.sub(keyValueRE, '', line) # Remove all key:value pairs
        
        # Now, process the "official" todo.txt format using a RE that should 
        # match the line completely.
        match = todoTxtRE.match(line)
        priority = self.priority(match)    
        completionDateTime = self.completionDateTime(match, now)
        plannedStartDateTime = self.plannedStartDateTime(match)
        categories = self.categories(match, event)
       
        recursiveSubject = match.group('subject')
        subjects = recursiveSubject.split('->')
        newTask = None
        for subject in subjects:
            newTask = self.findOrCreateTask(subject.strip(), newTask, event)
        
        newTask.setPriority(priority)
        newTask.setPlannedStartDateTime(plannedStartDateTime)
        newTask.setCompletionDateTime(completionDateTime)
        newTask.setDueDateTime(dueDateTime)
        for eachCategory in categories:
            newTask.addCategory(eachCategory, event=event)
            eachCategory.addCategorizable(newTask, event=event)        
                
    @staticmethod
    def priority(match):
        priorityText = match.group('priority')
        return ord(priorityText) + 1 - ord('A') if priorityText else 0
    
    @classmethod
    def completionDateTime(cls, match, now):
        if match.group('completed'):
            completionDateText = match.group('completionDate')
            return cls.dateTime(completionDateText) if completionDateText else now()
        else:
            return date.DateTime()
        
    @classmethod
    def plannedStartDateTime(cls, match):
        startDateText = match.group('startDate')
        return cls.dateTime(startDateText) if startDateText else date.DateTime()
    
    @staticmethod
    def dateTime(dateText):
        year, month, day = dateText.split('-')
        return date.DateTime(int(year), int(month), int(day), 0, 0, 0)
      
    def categories(self, match, event):
        ''' Transform both projects and contexts into categories. Since Todo.txt
            allows multiple projects for one task, but Task Coach does not allow
            for tasks to have more than one parent task, we cannot transform 
            projects into parent tasks. '''
        categories = []
        contextsAndProjects = match.group('contexts_and_projects_pre') + \
                              match.group('contexts_and_projects_post')
        contextsAndProjects = contextsAndProjects.strip()
        if contextsAndProjects:        
            for contextOrProject in contextsAndProjects.split(' '):
                recursiveSubject = contextOrProject.strip()
                categoryForTask = None
                for subject in recursiveSubject.split('->'):
                    categoryForTask = self.findOrCreateCategory(subject, categoryForTask, event)
                categories.append(categoryForTask)
        return categories
        
    def findOrCreateCategory(self, subject, parent, event):
        return self.findOrCreateCompositeItem(subject, parent, 
            self.__categoriesBySubject, self.__categoryList, category.Category, 
            event)
        
    def findOrCreateTask(self, subject, parent, event):
        return self.findOrCreateCompositeItem(subject, parent, 
            self.__tasksBySubject, self.__taskList, task.Task, event)
    
    def findOrCreateCompositeItem(self, subject, parent, subjectCache, 
                                  itemContainer, itemClass, event):
        if (subject, parent) in subjectCache:
            return subjectCache[(subject, parent)]           
        newItem = itemClass(subject=subject)
        if parent:
            newItem.setParent(parent)
            parent.addChild(newItem, event=event)
        itemContainer.append(newItem, event=event)
        subjectCache[(subject, parent)] = newItem
        return newItem        
    
    @staticmethod
    def compileTodoTxtRE():
        priorityRE = r'(?:\((?P<priority>[A-Z])\) )?'
        completedRe = r'(?P<completed>[Xx] )?'
        completionDateRE = r'(?:(?<=[xX] )(?P<completionDate>\d{4}-\d{1,2}-\d{1,2}) )?'
        startDateRE = r'(?:(?P<startDate>\d{4}-\d{1,2}-\d{1,2}) )?' 
        contextsAndProjectsPreRE = r'(?P<contexts_and_projects_pre>(?: ?[@+][^\s]+)*)'
        subjectRE = r'(?P<subject>.*?)'
        contextsAndProjectsPostRE = r'(?P<contexts_and_projects_post>(?: [@+][^\s]+)*)'
        return re.compile('^' + priorityRE + completedRe + completionDateRE + \
                          startDateRE + contextsAndProjectsPreRE + subjectRE + \
                          contextsAndProjectsPostRE + '$')
        
    @staticmethod
    def compileKeyValueRE():
        return re.compile(' (?P<key>\S+):(?P<value>\S+)')
    
    @staticmethod
    def __createSubjectCache(itemContainer):
        cache = dict()
        for item in itemContainer:
            cache[(item.subject(), item.parent())] = item
        return cache

        