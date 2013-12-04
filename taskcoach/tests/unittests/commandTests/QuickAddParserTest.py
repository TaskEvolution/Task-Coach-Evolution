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

from CommandTestCase import CommandTestCase
from taskcoachlib.command import quickAddParser
from taskcoachlib.domain import date
import sys

class QuickAddParserTestCase(CommandTestCase):
    def setUp(self):
        super(QuickAddParserTestCase, self).setUp()

        
    def tearDown(self):
        super(QuickAddParserTestCase, self).tearDown()


class FindDatesTest(QuickAddParserTestCase):
    def testFindStartDate(self):
        testString = 'This is a date start[' + date.DateTime.now().replace( second=0, microsecond=0).strftime('%Y-%m-%d %H:%M') + ']'
        cmpDate=date.DateTime.now().replace( second=0, microsecond=0)
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M'))

        testString = 'This is a date start[' + date.DateTime.now().replace(second=0, microsecond=0).strftime('%Y-%m-%d %H:%M') + ']'
        cmpDate=(date.DateTime.now()+date.TimeDelta(days=1)).replace(second=0, microsecond=0)
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertNotEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M'))

        testString = 'This is a date start[2013-13-12]'
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date start[2013-12-32]'
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date start[2013-02-29]'
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date start[20131-12-24]'
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],None,
                        'Nej')
        testString = 'This is a date start[2013-121-24]'
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")
        testString = 'This is a date start[20131-12-241]'
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date start ' + date.DateTime.now().replace(second=0, microsecond=0).strftime('%Y-%m-%d %H:%M')
        cmpDate=date.DateTime.now().replace( second=0, microsecond=0)
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date Thursday 10:00'
        cmpDate=(date.DateTime.now()+date.TimeDelta(days=(3 - date.DateTime.now().weekday())%7+1)).replace(hour=10, minute=0, second=0, microsecond=0)
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date Thursday'
        cmpDate=(date.DateTime.now()+date.TimeDelta(days=(3 - date.DateTime.now().weekday())%7+1)).replace(hour=0, minute=0, second=0, microsecond=0)
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date 10:00'
        cmpDate=date.DateTime.today().replace(hour=10,minute=0,second=0,microsecond=0)
        answer=quickAddParser.Parser().findStartDate(testString)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

    def testFindEndDate(self):
        startDate=date.DateTime(2013,12,21,15,0)
        testString = 'This is a date end[2013-12-25 15:00]'
        cmpDate=(date.DateTime(2013,12,25,15,0))
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M')  if answer[0] is not None else 'None'
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M'))

        testString = 'This is a date end[' + date.DateTime.now().replace(second=0, microsecond=0).strftime('%Y-%m-%d %H:%M') + ']'
        cmpDate=(date.DateTime.now()+date.TimeDelta(days=1)).replace(second=0, microsecond=0)
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertNotEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M'))

        testString = 'This is a date end[2013-13-12]'
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date end[2013-12-32]'
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date end[2013-02-29]'
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],None,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                        + " Should be: None ")

        testString = 'This is a date end[20131-12-24]'
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],None,'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                                    + " Should be: " + startDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date end[2013-121-24]'
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],None,'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                                    + " Should be: " + startDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date end[20131-12-241]'
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],None,'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M') if answer[0] is not None else 'None'
                            + " Should be: " + startDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date 2013-12-25 10:00'
        cmpDate=date.DateTime(2013,12,25,10,0)
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date Thursday 10:00'
        cmpDate=date.DateTime(2013,12,26,10,0).replace(second=0, microsecond=0)
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date Thursday'
        cmpDate=cmpDate=date.DateTime(2013,12,26,0,0).replace(second=0, microsecond=0)
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

        testString = 'This is a date 21:00'
        cmpDate=startDate.replace(hour=21,minute=0)
        answer=quickAddParser.Parser().findEndDate(testString,startDate)
        self.assertEqual(answer[0],cmpDate,
                        'Parsed: ' + testString + ' Answer: ' + answer[0].strftime('%Y-%m-%d %H:%M:%S')
                        + " Cmpdate: " + cmpDate.strftime('%Y-%m-%d %H:%M:%S'))

class FindPriorityTest(QuickAddParserTestCase):
        def testFindPriority(self):
            testString = 'Priority 5'
            cmpPriority = 5
            answer = quickAddParser.Parser().findPriority(testString)
            self.assertEqual(answer[0],cmpPriority,"Input: " + testString + " Answer: " + str(answer[0]) + 'Expected: ' + str(cmpPriority))

            testString = 'Priority -5'
            cmpPriority = -5
            answer = quickAddParser.Parser().findPriority(testString)
            self.assertEqual(answer[0],cmpPriority,"Input: " + testString + " Answer: " + str(answer[0]) + 'Expected: ' + str(cmpPriority))

            testString = 'Priority fel'
            cmpPriority = 0
            answer = quickAddParser.Parser().findPriority(testString)
            self.assertEqual(answer[0],cmpPriority,"Input: " + testString + " Answer: " + str(answer[0]) + ' Expected: ' + str(cmpPriority))

            testString = 'Priority ' + str(sys.maxint)
            cmpPriority = sys.maxint
            answer = quickAddParser.Parser().findPriority(testString)
            self.assertEqual(answer[0],cmpPriority,"Input: " + testString + " Answer: " + str(answer[0]) + 'Expected: ' + str(cmpPriority))
