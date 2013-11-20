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

import wx, StringIO, os
import test
from taskcoachlib import persistence, gui, config, render
from taskcoachlib.domain import task, category, effort, date
    
    
class PDFWriterTestCase(test.wxTestCase):
    treeMode = 'Subclass responsibility'
    filename = 'Subclass responsibility'
    
    def setUp(self):
        super(PDFWriterTestCase, self).setUp()
        task.Task.settings = self.settings = config.Settings(load=False)
        self.fd = StringIO.StringIO()
        self.writer = persistence.PDFWriter(self.fd, self.filename)
        self.taskFile = persistence.TaskFile()
        self.task = task.Task('Task subject')
        self.taskFile.tasks().append(self.task)
        self.viewer = self.createViewer()
        
    def tearDown(self):
        super(PDFWriterTestCase, self).tearDown()
        self.taskFile.close()
        self.taskFile.stop()

    def __writeAndRead(self, selectionOnly):
        #self.writer.write(self.viewer, self.settings, selectionOnly, True)
        pdfText = self.writer.writeForTests(self.viewer, self.settings, selectionOnly)
        #return self.fd.getvalue()
        return pdfText
    
    def expectInPDF(self, *pdfFragments, **kwargs):
        selectionOnly = kwargs.pop('selectionOnly', False)
        pdf = self.__writeAndRead(selectionOnly)
        for pdfFragment in pdfFragments:
            self.failUnless(pdfFragment in pdf, 
                            '%s not in %s'%(pdfFragment, pdf))
    
    def expectNotInPDF(self, *pdfFragments, **kwargs):
        selectionOnly = kwargs.pop('selectionOnly', False)
        pdf = self.__writeAndRead(selectionOnly)
        for pdfFragment in pdfFragments:
            self.failIf(pdfFragment in pdf, '%s in %s'%(pdfFragment, pdf))

    def selectItem(self, items):
        self.viewer.widget.select(items)


class CommonTestsMixin(object):
        
    def testHeader(self):
        self.expectInPDF('<ol>', '</ol>')
        
    '''def testStyle(self):
        self.expectInPDF('    <style type="text/css">\n', '    </style>\n')'''
        
    def testBody(self):
        self.expectInPDF('<li>', '</li>')


class TaskWriterTestCase(PDFWriterTestCase):
    def createViewer(self):
        self.settings.set('taskviewer', 'treemode', self.treeMode)
        return gui.viewer.TaskViewer(self.frame, self.taskFile, self.settings)


class TaskTestsMixin(CommonTestsMixin):
    def testTaskSubject(self):
        self.expectInPDF('Task Name:')
        
    def testWriteSelectionOnly_SelectedChild(self):
        child = task.Task('Child')
        self.task.addChild(child)
        self.taskFile.tasks().append(child)
        self.selectItem([child])
        self.expectInPDF('Task Name:')

class TaskListTestsMixin(object):
    def testTaskDescription(self):
        self.task.setDescription('Task description')
        self.viewer.showColumnByName('description')
        self.expectInPDF('Description')
    
    def testCreationDateTime(self):
        self.viewer.showColumnByName('creationDateTime')
        self.expectInPDF(render.dateTime(self.task.creationDateTime(), 
                                          humanReadable=False))
        
    def testMissingCreationDateTime(self):
        self.viewer.showColumnByName('creationDateTime')
        self.taskFile.tasks().append(task.Task(creationDateTime=date.DateTime.min))
        self.taskFile.tasks().remove(self.task)
        self.expectNotInPDF('1/1/1')
        
    def testModificationDateTime(self):
        self.task.setModificationDateTime(date.DateTime(2012, 1, 1, 10, 0, 0))
        self.viewer.showColumnByName('modificationDateTime')
        self.expectInPDF(render.dateTime(self.task.modificationDateTime(),
                                          humanReadable=False))
        
    def testMissingModificationDateTime(self):
        self.viewer.showColumnByName('modificationDateTime')
        self.expectInPDF(render.dateTime(self.task.modificationDateTime(),
                                          humanReadable=False))
        self.expectNotInHTML('1/1/1')
    

class EffortWriterTestCase(CommonTestsMixin, PDFWriterTestCase):
    filename = 'filename'
    
    def setUp(self):
        super(EffortWriterTestCase, self).setUp()
        now = date.DateTime.now()
        self.task.addEffort(effort.Effort(self.task, start=now,
                                          stop=now + date.ONE_SECOND))

    def createViewer(self):
        return gui.viewer.EffortViewer(self.frame, self.taskFile, self.settings)

    def testTaskSubject(self):
        self.expectInPDF('subject')
        
    def testEffortDuration(self):
        self.expectInPDF('0:00:01')
        
class CategoryWriterTestsMixin(CommonTestsMixin):
    def testCategorySubject(self):
        self.expectInPDF('Category')
        
class CategoryWriterTestCase(PDFWriterTestCase):
    def setUp(self):
        super(CategoryWriterTestCase, self).setUp()
        self.category = category.Category('Category')
        self.taskFile.categories().append(self.category)

    def createViewer(self):
        return gui.viewer.CategoryViewer(self.frame, self.taskFile, 
                                         self.settings)

        
class CategoryWriterExportTest(CategoryWriterTestsMixin, CategoryWriterTestCase):
    filename = 'filename'

    
