import re
#import taskcoachlib.domain.date.dateandtime
from taskcoachlib.domain import date
#Regex that finds a date within a text string

#todo Fix start and end time
# Matches: 31/12/2003 11:59:59 PM | 29-2-2004 | 01:45:02

class Parser(object):
	def findStartDate(self,line):

		m = re.search(r'start\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]',line,re.M|re.I)

		if m is not None:
			match = m.group(0)[6:-1]
			return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"), line.replace('start['+match+']',"").replace('Start['+match+']',""))
		else:
			return (None,line)

	def findEndDate(self,line):

		m = re.search(r'end\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]',line,re.M|re.I)

		if m is not None:
			match = m.group(0)[4:-1]
			return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"), line.replace('end['+match+']',"").replace('End['+match+']',""))
		else:
			return (None,line)

	# Matches: Priority #, Priority -#	
	def findPriority(self,line):
		m = re.search(r'Priority \d+|priority -\d+', line,re.M|re.I)
		if (m is not None):
			match = re.search(r'(-)?\d+$', m.group(),re.M|re.I).group(0)
			return (int(match),line.replace('Priority '+ match,"").replace('priority '+ match,""))
		else:
			return (0,line)

	def findActualStartDate(self,line):

		m = re.search(r'actual\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]',line,re.M|re.I)

		if m is not None:
			match = m.group(0)[7:-1]
			return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"), line.replace('actual['+match+']',"").replace('Actual['+match+']',""))
		else:
			return (None,line)

	def findCompletionDate(self,line):

		m = re.search(r'completion\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]',line,re.M|re.I)

		if m is not None:
			match = m.group(0)[11:-1]
			return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"), line.replace('completion['+match+']',"").replace('Completion['+match+']',""))
		else:
			return (None,line)
		
	# Matches: Reminder[1/12/2003 11:59:59 PM]	
	def findReminder(self,line):

		m = re.search(r'reminder\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\]',line,re.M|re.I)

		if m is not None:
			match = m.group(0)[9:-1]
			return (date.DateTime.strptime(match, "%Y-%m-%d %H:%M"), line.replace('reminder['+match+']',"").replace('Reminder['+match+']',""))
		else:
			return (None,line)

	# Matches: Category[cat1,cat2,cat3]
	def findCategory(self,line):
		m = re.search(r'Category\[(.*?)\]', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (m.group(0)[9:-1].split(','),line.replace(match,""))
		else:
			return (None,line)


	# Matches: Description[abcdefghijklmnopqrstuvwxyz]
	def findDescription(self,line):
		m = re.search(r'Description\[(.*?)\]', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match[12:-1],line.replace(match,""))
		else:
			return ('',line)
			
	"""# Matches: Hourly Fee=####:##
	def findHourlyFee(self,line):
		m = re.search(r'Hourly Fee (\d+):\d\d', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match.split()[-1],line.replace(match,""))
		else:
			return (0,line)
	# Matches: Fixed Fee=####:##
	def findFixedFee(self,line):
		m = re.search(r'Fixed Fee (\d+):\d\d', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match.split()[-1],line.replace(match,""))
		else:
			return (0,line)
			
	# Matches: Budget=####:##:##	
	def findBudget(self,line):
		m = re.search(r'Budget\[(\d+):\d\d:\d\d\]', line,re.M|re.I)
		if (m is not None):
			match=m.group()[7:-1]
			return (date.DateTime.strptime(match, "%H:%M:%S"), line.replace('Budget['+match+']',"").replace('budget['+match+']',""))
		else:
			return (None,line)
			
	# Matches: Pre[prereq1,prereq2,prereq3]		
	def findPrereq(self,line):
		m = re.search(r'Pre\[(.*?)\]', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match[4:-1].split(','),line.replace(match,""))
		else:
			return (None,line)"""
	
	
	
	#line= 'Watch a movie Pre[prereq1,prereq2,prereq3] 31/12/2003 08:00:00 PM to 31/12/2003 10:00:00 PM Description[abcdefghijklmnopqrstuvwxyz] Fixed Fee 10:00 Hourly Fee 100:00 Budget 1000:00:00 Category[cat1,cat2,cat3] Reminder[1/12/2003 11:59:59 PM] Completion[1/12/2003 11:59:59 PM] Actual[1/12/2003 11:59:59 PM] Priority 5'

	def getAnswers(self,line):
		#answer = self.findPrereq(line)
		#answerDict = {'Prerequisites': answer[0]}
		


		#answer=self.findFixedFee(answer[1])
		#answerDict['FixedFee']= answer[0]

		#answer=self.findHourlyFee(answer[1])
		#answerDict['HourlyFee']= answer[0]

		#answer=self.findBudget(answer[1])
		#answerDict['Budget']= answer[0]

		#answer=self.findCategory(answer[1])
		#answerDict['Categories']= answer[0]

		#answer=self.findReminder(answer[1])
		#answerDict['Reminder']= answer[0]
	
		answer=self.findDescription(line)
		answerDict = {'Description': answer[0]}
		
		answer=self.findCompletionDate(answer[1])
		answerDict['CompletionDate']= answer[0]

		answer=self.findActualStartDate(answer[1])
		answerDict['ActualStartDate']= answer[0]

		answer=self.findPriority(answer[1])
		answerDict['Priority']= answer[0]
		
		answer=self.findStartDate(answer[1])
		answerDict['StartDate']= answer[0]

		answer=self.findEndDate(answer[1])
		answerDict['EndDate']= answer[0]

		answerDict['Title']= re.sub(' +',' ',answer[1])

		print answerDict

		return answerDict

	#return re.findall(r'(\d[1-31] January|\d[1-28] Febrary|\d[1-31] March|\d[1-30] April|\d[1-31] May|\d[1-30] June|\d[1-31]
	# 					July|\d[1-31] August|\d[1-30] September|\d[1-31] October|\d[1-30] November|\d[1-31] December)',line)