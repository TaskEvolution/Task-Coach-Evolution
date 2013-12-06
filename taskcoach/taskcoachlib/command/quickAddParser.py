import re
from taskcoachlib.domain import date

class Parser(object):
    def findStartDate(self, line):
        try:
            startdate = None
            m = re.search(r'start\[(19|20)\d\d([- /.])(0[1-9]|1[012])\2(0[1-9]|[12][0-9]|3[01])\]', line, re.M | re.I)

            if m is not None:
                match = m.group(0)[6:-1]
                return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"),
                        line.replace('start[' + match + ']', "",1).replace('Start[' + match + ']', "",1))
            else:
                m = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', line, re.M | re.I)

                if m is not None:
                    day = 0
                    match = m.group(0)

                    if match.lower() == 'tuesday':
                        day = 1
                    elif match.lower() == 'wednesday':
                        day = 2
                    elif match.lower() == 'thursday':
                        day = 3
                    elif match.lower() == 'friday':
                        day = 4
                    elif match.lower() == 'saturday':
                        day = 5
                    elif match.lower() == 'sunday':
                        day = 6
                    startdate = (date.DateTime.now() + date.TimeDelta(days=(day - date.DateTime.now().weekday())%7+1)).replace(hour=0,minute=0,second=0,microsecond=0)
                    line = line.replace(match, "",1)

                m = re.search(r'(19|20)\d\d([- /.])(0[1-9]|1[012])\2(0[1-9]|[12][0-9]|3[01])', line, re.M | re.I)

                if m is not None:
                    match = m.group(0)
                    startdate=date.DateTime.strptime(match, "%Y-%m-%d")
                    line = line.replace(match, "",1)

                m = re.search(r'\d{1,2}:\d{1,2}', line, re.M | re.I)

                if m is not None:
                    match = m.group(0)
                    tmpDate=date.DateTime.strptime(match, "%H:%M")
                    if(startdate is None):
                        startdate=date.DateTime.today().replace(hour=tmpDate.hour,minute=tmpDate.minute,second=0,microsecond=0)
                    else:
                        startdate=startdate.replace().replace(hour=tmpDate.hour,minute=tmpDate.minute,second=0,microsecond=0)
                    line = line.replace(match, "",1)

                return (startdate,line)
        except ValueError:
            return (None,line)


    def findEndDate(self, line,startdate):
        enddate=None
        try:
            m = re.search(r'end\[(19|20)\d\d([- /.])(0[1-9]|1[012])\2(0[1-9]|[12][0-9]|3[01])\]', line, re.M | re.I)
            if m is not None:
                match = m.group(0)[4:-1]
                return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"),
                        line.replace('end[' + match + ']', "",1).replace('Start[' + match + ']', "",1))
            else:
                m = re.search(r'(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', line, re.M | re.I)

                if m is not None:
                    day = 0
                    match = m.group(0)

                    if match.lower() == 'tuesday':
                        day = 1
                    elif match.lower() == 'wednesday':
                        day = 2
                    elif match.lower() == 'thursday':
                        day = 3
                    elif match.lower() == 'friday':
                        day = 4
                    elif match.lower() == 'saturday':
                        day = 5
                    elif match.lower() == 'sunday':
                        day = 6
                    enddate = startdate + date.TimeDelta(days=(day - startdate.weekday())%7+1)
                    enddate=enddate.replace(hour=0,minute=0)
                    line = line.replace(match, "",1)

                m = re.search(r'(19|20)\d\d([- /.])(0[1-9]|1[012])\2(0[1-9]|[12][0-9]|3[01])', line, re.M | re.I)

                if m is not None:
                    match = m.group(0)
                    enddate=date.DateTime.strptime(match, "%Y-%m-%d")
                    line = line.replace(match, "",1)

                m = re.search(r'\d{1,2}:\d{1,2}', line, re.M | re.I)

                if m is not None:
                    match = m.group(0)
                    tmpDate=date.DateTime.strptime(match, "%H:%M")
                    if(enddate is None):
                        enddate=startdate.replace(hour=tmpDate.hour,minute=tmpDate.minute)
                    else:
                        enddate=enddate.replace().replace(hour=tmpDate.hour,minute=tmpDate.minute)
                    line = line.replace(match, "",1)

                return (enddate,line)
        except ValueError:
            return (None,line)

    # Matches: Priority #, Priority -#
    def findPriority(self, line):
        m = re.search(r'Priority \d+|priority -\d+', line, re.M | re.I)
        if (m is not None):
            match = re.search(r'(-)?\d+$', m.group(), re.M | re.I).group(0)
            return (int(match), line.replace('Priority ' + match, "").replace('priority ' + match, ""))
        else:
            return (0, line)


    def findActualStartDate(self, line):
        m = re.search(r'actual\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]', line, re.M | re.I)

        if m is not None:
            match = m.group(0)[7:-1]
            return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"),
                    line.replace('actual[' + match + ']', "").replace('Actual[' + match + ']', ""))
        else:
            return (None, line)


    def findCompletionDate(self, line):
        m = re.search(r'completion\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]', line, re.M | re.I)

        if m is not None:
            match = m.group(0)[11:-1]
            return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"),
                    line.replace('completion[' + match + ']', "").replace('Completion[' + match + ']', ""))
        else:
            return (None, line)

    # Matches: Reminder[1/12/2003 11:59:59 PM]
    def findReminder(self, line):
        m = re.search(r'reminder\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]', line, re.M | re.I)

        if m is not None:
            match = m.group(0)[9:-1]
            return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"),
                    line.replace('reminder[' + match + ']', "").replace('Reminder[' + match + ']', ""))
        else:
            return (None, line)

    # Matches: Category[cat1,cat2,cat3]
    def findCategories(self, line):
        m = re.search(r'Category\[(.*?)\]', line, re.M | re.I)
        if (m is not None):
            match = m.group(0)
            return (m.group(0)[9:-1].split(','), line.replace(match, ""))
        else:
            return ([], line)


    # Matches: Description[abcdefghijklmnopqrstuvwxyz]
    def findDescription(self, line):
        m = re.search(r'Description\[(.*?)\]', line, re.M | re.I)
        if (m is not None):
            match = m.group(0)
            return (match[12:-1], line.replace(match, ""))
        else:
            return ('', line)

    def getAnswers(self, line):

        answer = self.findDescription(line)
        answerDict = {'Description': answer[0]}

        answer = self.findCategories(answer[1])
        answerDict['Categories'] = answer[0]

        answer = self.findCompletionDate(answer[1])
        answerDict['CompletionDate'] = answer[0]

        answer = self.findActualStartDate(answer[1])
        answerDict['ActualStartDate'] = answer[0]

        answer = self.findPriority(answer[1])
        answerDict['Priority'] = answer[0]

        answer = self.findStartDate(answer[1])
        answerDict['StartDate'] = answer[0]

        answer = self.findEndDate(answer[1],answer[0])
        answerDict['EndDate'] = answer[0]

        answerDict['Title'] = re.sub(' +', ' ', answer[1])

        print answerDict

        return answerDict