import re
#Regex that finds a date within a text string

#todo Fix start and end time
# Matches: 31/12/2003 11:59:59 PM | 29-2-2004 | 01:45:02

class Parser:
	def findDate(line):
		m = re.search(r'(?=\d)(?:(?:31(?!.(?:0?[2469]|11))|(?:30|29)(?!.0?2)|29(?=.0?2.(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|'+
		r'[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))(?:\x20|$))|(?:2[0-8]|1\d|0?[1-9]))([-./])(?:1[012]|0?[1-9])\1(?:1[6-9]|[2-9]\d)?'+
		r'\d\d(?:(?=\x20\d)\x20|$))?(((0?[1-9]|1[012])(:[0-5]\d){0,2}(\x20[AP]M))|([01]\d|2[0-3])(:[0-5]\d){1,2})?'+
		r'\sto\s'+
		r'(?=\d)(?:(?:31(?!.(?:0?[2469]|11))|'+
		r'(?:30|29)(?!.0?2)|29(?=.0?2.(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))(?:\x20|$))|'+
		r'(?:2[0-8]|1\d|0?[1-9]))([-./])(?:1[012]|0?[1-9])\1(?:1[6-9]|[2-9]\d)?\d\d(?:(?=\x20\d)\x20|$))?(((0?[1-9]|1[012])(:[0-5]\d){0,2}(\x20[AP]M))'+
		r'|([01]\d|2[0-3])(:[0-5]\d){1,2})?', line,re.M|re.I)
	
		if m is not None:
			match = m.group(0)
			return (match.split('to'), line.replace(match,""))
		else:
			return re.findall(r'(\d[1-31] January|\d[1-28] Febrary|\d[1-31] March|\d[1-30] April|\d[1-31] May|\d[1-30] June|\d[1-31]'+
	 						r'July|\d[1-31] August|\d[1-30] September|\d[1-31] October|\d[1-30] November|\d[1-31] December)',line)	
	

	# Matches: Priority #, Priority -#	
	def findPriority(line):
		m = re.search(r'Priority \d+|priority -\d+', line,re.M|re.I)
		if (m is not None):
			match = re.search(r'(-)?\d+$', m.group(),re.M|re.I).group(0)
			return (match,line.replace('Priority '+ match,""))

	# Matches: Actual[1/12/2003 11:59:59 PM]	
	def findActualStartDate(line):
		m = re.search(r'Actual\[(?=\d)(?:(?:31(?!.(?:0?[2469]|11))|(?:30|29)(?!.0?2)|29(?=.0?2.(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))(?:\x20|$))|(?:2[0-8]|1\d|0?[1-9]))([-./])(?:1[012]|0?[1-9])\1(?:1[6-9]|[2-9]\d)?\d\d(?:(?=\x20\d)\x20|$))?(((0?[1-9]|1[012])(:[0-5]\d){0,2}(\x20[AP]M))|([01]\d|2[0-3])(:[0-5]\d){1,2})?\]', line,re.M|re.I)
		if m is not None:
			match=m.group(0)
			return (match[18:-1],line.replace(match,""))

	# Matches: Completion[1/12/2003 11:59:59 PM]
	def findCompletionDate(line):
		m = re.search(r'Completion\[(?=\d)(?:(?:31(?!.(?:0?[2469]|11))|(?:30|29)(?!.0?2)|29(?=.0?2.(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))(?:\x20|$))|(?:2[0-8]|1\d|0?[1-9]))([-./])(?:1[012]|0?[1-9])\1(?:1[6-9]|[2-9]\d)?\d\d(?:(?=\x20\d)\x20|$))?(((0?[1-9]|1[012])(:[0-5]\d){0,2}(\x20[AP]M))|([01]\d|2[0-3])(:[0-5]\d){1,2})?\]', line,re.M|re.I)
		if m is not None:
			match=m.group(0)
			return (match[11:-1],line.replace(match,""))
		
	# Matches: Reminder[1/12/2003 11:59:59 PM]	
	def findReminder(line):
		m = re.search(r'Reminder\[(?=\d)(?:(?:31(?!.(?:0?[2469]|11))|(?:30|29)(?!.0?2)|29(?=.0?2.(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00)))(?:\x20|$))|(?:2[0-8]|1\d|0?[1-9]))([-./])(?:1[012]|0?[1-9])\1(?:1[6-9]|[2-9]\d)?\d\d(?:(?=\x20\d)\x20|$))?(((0?[1-9]|1[012])(:[0-5]\d){0,2}(\x20[AP]M))|([01]\d|2[0-3])(:[0-5]\d){1,2})?\]', line,re.M|re.I)
		if m is not None:
			match=m.group(0)
			return (match[9:-1],line.replace(match,""))

	# Matches: Category[cat1,cat2,cat3]
	def findCategory(line):
		m = re.search(r'Category\[(.*?)\]', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (m.group(0)[9:-1].split(','),line.replace(match,""))

	# Matches: Budget=####:##:##	
	def findBudget(line):
		m = re.search(r'Budget (\d+):\d\d:\d\d', line,re.M|re.I)
		if (m is not None):
			match=m.group()
			return (match[7:],line.replace(match,""))

	# Matches: Hourly Fee=####:##
	def findHourlyFee(line):
		m = re.search(r'Hourly Fee (\d+):\d\d', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match.split()[-1],line.replace(match,""))

	# Matches: Fixed Fee=####:##
	def findFixedFee(line):
		m = re.search(r'Fixed Fee (\d+):\d\d', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match.split()[-1],line.replace(match,""))

	# Matches: Description[abcdefghijklmnopqrstuvwxyz]
	def findDescription(line):
		m = re.search(r'Description\[(.*?)\]', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match[12:-1],line.replace(match,""))

	# Matches: Pre[prereq1,prereq2,prereq3]		
	def findPrereq(line):
		m = re.search(r'Pre\[(.*?)\]', line,re.M|re.I)
		if (m is not None):
			match=m.group(0)
			return (match[4:-1].split(','),line.replace(match,""))
	#line= 'Watch a movie Pre[prereq1,prereq2,prereq3] 31/12/2003 08:00:00 PM to 31/12/2003 10:00:00 PM Description[abcdefghijklmnopqrstuvwxyz] Fixed Fee 10:00 Hourly Fee 100:00 Budget 1000:00:00 Category[cat1,cat2,cat3] Reminder[1/12/2003 11:59:59 PM] Completion[1/12/2003 11:59:59 PM] Actual[1/12/2003 11:59:59 PM] Priority 5'

	def getAnswers(line):
		answer = findPrereq(line)
		answerDict = {'Prerequisites': answer[0]}
		answer=findDescription(answer[1])
		answerDict['Description']= answer[0]

		answer=findFixedFee(answer[1])
		answerDict['Fixed fee']= answer[0]

		answer=findHourlyFee(answer[1])
		answerDict['Hourly fee']= answer[0]

		answer=findBudget(answer[1])
		answerDict['Budget']= answer[0]

		answer=findCategory(answer[1])
		answerDict['Categories']= answer[0]

		answer=findReminder(answer[1])
		answerDict['Reminder']= answer[0]

		answer=findCompletionDate(answer[1])
		answerDict['Completion date']= answer[0]

		answer=findActualStartDate(answer[1])
		answerDict['Actual Start date']= answer[0]

		answer=findPriority(answer[1])
		answerDict['Priority']= answer[0]

		answer=findDate(answer[1])
		answerDict['Start/End date']= answer[0]

		answerDict['Title']= re.sub(' +',' ',answer[1])

		print answerDict

		return answerDict

	#return re.findall(r'(\d[1-31] January|\d[1-28] Febrary|\d[1-31] March|\d[1-30] April|\d[1-31] May|\d[1-30] June|\d[1-31]
	# 					July|\d[1-31] August|\d[1-30] September|\d[1-31] October|\d[1-30] November|\d[1-31] December)',line)