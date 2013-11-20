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

import wx, cgi, StringIO
from taskcoachlib.domain import task


def viewer2pdf(viewer, settings, selectionOnly=False, columns=None, tasks=None):
    converter = Viewer2PDFConverter(viewer, settings)
    columns = columns or viewer.visibleColumns()
    tasks = viewer.visibleItems()
    if selectionOnly:
    	tasks = [task for task in tasks if viewer.isselected(task)]
    else:
        tasks = viewer.visibleItems()
    
    return converter(columns, tasks)


class Viewer2PDFConverter(object):
    ''' Class to convert the visible contents of a viewer into Text which is later converter
    to a PDF file.''' 

    def __init__(self, viewer, settings):
        super(Viewer2PDFConverter, self).__init__()
        self.viewer = viewer
        self.settings = settings
        self.count = 0
        
    def __call__(self, columns, tasks):
        ''' Create text.'''
        lines = self.pdf(columns, tasks)
        return lines, self.count
    
    def pdf(self, columns, tasks, level=0):
        ''' Returns all text, consisting of header and body. 
        pdfContent = self.pdfHeader(level+1, tasks) + \
                      self.pdfBody(columns, level+1, tasks) '''
        pdfContent = self.pdfBody(columns, level+1, tasks)
        
        return pdfContent

    def pdfHeader(self, level, tasks):
        ''' Return the text header <head>. '''
        pdfHeaderContent = "<center><h1>Tasks</h1></center>"
        return pdfHeaderContent

    def pdfBody(self, columns, level, tasks):
        ''' Returns the text's body section'''
        
        pdfBodyContent = "<ol>"

        
        '''Iterate through the tasks and its selected columns and print these to plain text 
        including html tags to make it more readable. '''

        for task in tasks:
            for column in columns:
                if column.render(task, humanReadable=False):
                    if column.name() == 'subject':
                        pdfBodyContent = pdfBodyContent + "<li><b>Task Name: </b>" + task.subject() + "</i></li>"
                    else:
                        colContent = column.render(task, humanReadable=False)
                        #pdfBodyContent = pdfBodyContent + "<ul><li>"
                        pdfBodyContent = pdfBodyContent + "<ul><ul><li><i>" + column.header() + "</i>: " +  str(colContent) + "</li></ul></ul>"
                        #pdfBodyContent = pdfBodyContent + ": <i>"
                        #pdfBodyContent = pdfBodyContent + "<i>" +  str(colContent) + "</i>"
                        #pdfBodyContent = pdfBodyContent + "</i></li></ul>"
                        
                        
        #Return the completely created text document which are to be created to a pdf document. 
        return pdfBodyContent + "</ol>"