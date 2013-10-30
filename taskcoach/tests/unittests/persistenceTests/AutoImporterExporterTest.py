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

from taskcoachlib import persistence, config
from taskcoachlib.domain import task
import test
import os
from unittests import dummy


class AutoExporterTestCase(test.TestCase):
    def setUp(self):
        task.Task.settings = self.settings = config.Settings(load=False)
        self.exporter = persistence.AutoImporterExporter(self.settings)
        self.taskFile = persistence.TaskFile()
        self.tskFilename = 'autoexport.tsk'
        self.txtFilename = 'autoexport.txt'
        self.taskFile.setFilename(self.tskFilename)
        
    def tearDown(self):
        super(AutoExporterTestCase, self).tearDown()
        del self.exporter
        for filename in self.tskFilename, self.tskFilename + '.delta', self.txtFilename:
            try:
                os.remove(filename)
            except OSError:
                pass
        
    def testAddOneTaskWhenAutoSaveIsOn(self):
        self.settings.set('file', 'autoexport', '["Todo.txt"]')
        self.settings.set('file', 'autosave', 'True')
        autosaver = persistence.AutoSaver(self.settings)
        self.taskFile.tasks().append(task.Task(subject='Some task'))
        autosaver.on_idle(dummy.Event())
        self.assertEqual('Some task\n', file(self.txtFilename, 'r').read())
        
    def testAddOneTaskAndSaveManually(self):
        self.settings.set('file', 'autoexport', '["Todo.txt"]')
        self.taskFile.tasks().append(task.Task(subject='Whatever'))
        self.taskFile.save()
        self.assertEqual('Whatever\n', file(self.txtFilename, 'r').read())
        
    def testImportOneTaskWhenSavingManually(self):
        self.settings.set('file', 'autoimport', '["Todo.txt"]')
        with file(self.txtFilename, 'w') as todoTxtFile:
            todoTxtFile.write('Imported task\n')
        self.taskFile.save()
        self.assertEqual('Imported task', 
                         list(self.taskFile.tasks())[0].subject())
        
    def testImportOneTaskWhenAutoSaving(self):
        self.settings.set('file', 'autoimport', '["Todo.txt"]')
        self.settings.set('file', 'autosave', 'True')
        autosaver = persistence.AutoSaver(self.settings)
        with file(self.txtFilename, 'w') as todoTxtFile:
            todoTxtFile.write('Imported task\n')
        self.taskFile.tasks().append(task.Task(subject='Some task'))
        autosaver.on_idle(dummy.Event())
        self.assertEqual(2, len(self.taskFile.tasks()))

    def testImportAfterReadingTaskFile(self):
        self.taskFile.save()
        self.settings.set('file', 'autoimport', '["Todo.txt"]')
        with file(self.txtFilename, 'w') as todoTxtFile:
            todoTxtFile.write('Imported task\n')
        self.taskFile.load()
        self.assertEqual('Imported task', 
                         list(self.taskFile.tasks())[0].subject())
        
    def testSaveWithAutoImportWhenFileToImportDoesNotExist(self):
        self.settings.set('file', 'autoimport', '["Todo.txt"]')
        self.taskFile.tasks().append(task.Task(subject='Whatever'))
        self.taskFile.save()
