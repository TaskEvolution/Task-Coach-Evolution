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

import re, generator, os
from taskcoachlib.domain import date
from xhtml2pdf import pisa
from reportlab.pdfbase import _fontdata_enc_winansi
from reportlab.pdfbase import _fontdata_enc_macroman
from reportlab.pdfbase import _fontdata_enc_standard
from reportlab.pdfbase import _fontdata_enc_symbol
from reportlab.pdfbase import _fontdata_enc_zapfdingbats
from reportlab.pdfbase import _fontdata_enc_pdfdoc
from reportlab.pdfbase import _fontdata_enc_macexpert
from reportlab.pdfbase import _fontdata_widths_courier
from reportlab.pdfbase import _fontdata_widths_courierbold
from reportlab.pdfbase import _fontdata_widths_courieroblique
from reportlab.pdfbase import _fontdata_widths_courierboldoblique
from reportlab.pdfbase import _fontdata_widths_helvetica
from reportlab.pdfbase import _fontdata_widths_helveticabold
from reportlab.pdfbase import _fontdata_widths_helveticaoblique
from reportlab.pdfbase import _fontdata_widths_helveticaboldoblique
from reportlab.pdfbase import _fontdata_widths_timesroman
from reportlab.pdfbase import _fontdata_widths_timesbold
from reportlab.pdfbase import _fontdata_widths_timesitalic
from reportlab.pdfbase import _fontdata_widths_timesbolditalic
from reportlab.pdfbase import _fontdata_widths_symbol
from reportlab.pdfbase import _fontdata_widths_zapfdingbats


class PDFWriter(object):

#Export to PDF
#author: Erik Ivarsson 

    def __init__(self, fd, filename):
        self.__fd = fd
        self.__filename = filename
        
    def write(self, viewer, settings, selectionOnly, columns = None):

        textToPdf, count = generator.viewer2pdf(viewer, settings, selectionOnly, columns)
        #print textToPdf
        
        self.__fd.close()
        resultFile = open(self.__filename, "w+b")
        pisa.CreatePDF(textToPdf, resultFile)
        resultFile.close()
        
        return count

    def writeForTests(self, viewer, settings, selectionOnly, columns = None):
        '''Only difference is that we do not return the count, but the text in this methid for the writeForTests
        to function'''
        textToPdf, count = generator.viewer2pdf(viewer, settings, selectionOnly, columns)
        print textToPdf
        
        self.__fd.close()
        resultFile = open(self.__filename, "w+b")
        pisa.CreatePDF(textToPdf, resultFile)
        resultFile.close()
        
        return textToPdf

    