# -*- coding: utf-8 -*-

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

import test, StringIO
from taskcoachlib import persistence, config, gui
from taskcoachlib.domain import task, category, date


class TodoTxtWriterTestCase(test.wxTestCase):
    def setUp(self):
        self.settings = task.Task.settings = config.Settings(load=False)
        self.file = StringIO.StringIO()
        self.writer = persistence.TodoTxtWriter(self.file, 'whatever.tsk')
        self.settings.set('taskviewer', 'treemode', 'False')
        self.taskFile = persistence.TaskFile()
        self.viewer = gui.viewer.TaskViewer(self.frame, self.taskFile, self.settings)

    def testNoTasksAndCategories(self):
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('', self.file.getvalue())
        
    def testOneTask(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese'))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Get cheese\n', self.file.getvalue())
        
    def testTwoTasks(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese'))
        self.taskFile.tasks().append(task.Task(subject='Paint house'))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Get cheese\nPaint house\n', self.file.getvalue())
        
    def testNonAsciiSubject(self):
        self.taskFile.tasks().append(task.Task(subject='Call Jérôme'))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Call Jérôme\n', self.file.getvalue())

    def testSorting(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese'))
        self.taskFile.tasks().append(task.Task(subject='Paint house'))
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending(False)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Paint house\nGet cheese\n', self.file.getvalue())
        
    def testTaskPriorityIsWrittenAsLetter(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', priority=1))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('(A) Get cheese\n', self.file.getvalue())
        
    def testTaskPriorityHigherThanZIsIgnored(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', priority=27))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Get cheese\n', self.file.getvalue())
        
    def testStartDate(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', 
                                               plannedStartDateTime=date.DateTime(2027,1,23,15,34,12)))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('2027-01-23 Get cheese\n', self.file.getvalue())
        
    def testCompletionDate(self):
        self.taskFile.tasks().append(task.Task(subject='Get cheese', 
                                               completionDateTime=date.DateTime(2027,1,23,15,34,12)))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('X 2027-01-23 Get cheese\n', self.file.getvalue())
        
    def testContext(self):
        phone = category.Category(subject='@phone')
        self.taskFile.categories().append(phone)
        pizza = task.Task(subject='Order pizza')
        self.taskFile.tasks().append(pizza)
        phone.addCategorizable(pizza)
        pizza.addCategory(phone)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Order pizza @phone\n', self.file.getvalue())
        
    def testContextWithSpaces(self):
        at_home = category.Category(subject='@at home')
        self.taskFile.categories().append(at_home)
        dishes = task.Task(subject='Do dishes')
        self.taskFile.tasks().append(dishes)
        at_home.addCategorizable(dishes)
        dishes.addCategory(at_home)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Do dishes @at_home\n', self.file.getvalue())
        
    def testSubcontext(self):
        work = category.Category(subject='@Work')
        staff_meeting = category.Category(subject='Staff meeting')
        work.addChild(staff_meeting)
        self.taskFile.categories().append(work)
        discuss_proposal = task.Task(subject='Discuss the proposal')
        self.taskFile.tasks().append(discuss_proposal)
        discuss_proposal.addCategory(staff_meeting)
        staff_meeting.addCategorizable(discuss_proposal)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Discuss the proposal @Work->Staff_meeting\n', 
                         self.file.getvalue())

    def testMultipleContexts(self):
        phone = category.Category(subject='@phone')
        food = category.Category(subject='@food')
        self.taskFile.categories().extend([phone, food])
        pizza = task.Task(subject='Order pizza')
        self.taskFile.tasks().append(pizza)
        phone.addCategorizable(pizza)
        pizza.addCategory(phone)
        food.addCategorizable(pizza)
        pizza.addCategory(food)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Order pizza @food @phone\n', self.file.getvalue())
        
    def testProject(self):
        alive = category.Category(subject='+Stay alive')
        self.taskFile.categories().append(alive)
        pizza = task.Task(subject='Order pizza')
        self.taskFile.tasks().append(pizza)
        alive.addCategorizable(pizza)
        pizza.addCategory(alive)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Order pizza +Stay_alive\n', self.file.getvalue())
        
    def testIgnoreCategoriesThatAreNotAContextNorAProject(self):
        phone = category.Category(subject='phone')
        self.taskFile.categories().append(phone)
        pizza = task.Task(subject='Order pizza')
        self.taskFile.tasks().append(pizza)
        phone.addCategorizable(pizza)
        pizza.addCategory(phone)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Order pizza\n', self.file.getvalue())
         
    def testSubtask(self):
        self.viewer.sortBy('subject')
        self.viewer.setSortOrderAscending()
        project = task.Task(subject='Project')
        activity = task.Task(subject='Some activity')
        project.addChild(activity)
        self.taskFile.tasks().append(project)
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Project\nProject -> Some activity\n', self.file.getvalue())
        
    def testTaskWithDueDate(self):
        self.taskFile.tasks().append(task.Task(subject='Export due date',
                                               dueDateTime=date.DateTime(2011,1,1,16,50,10)))
        self.writer.write(self.viewer, self.settings, False)
        self.assertEqual('Export due date due:2011-01-01\n', self.file.getvalue())
        
    def testExportSelectionOnly(self):
        cheese = task.Task(subject='Get cheese')
        self.taskFile.tasks().append(cheese)
        self.taskFile.tasks().append(task.Task(subject='Paint house'))
        self.viewer.select([cheese])
        self.writer.write(self.viewer, self.settings, True)
        self.assertEqual('Get cheese\n', self.file.getvalue())