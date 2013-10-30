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

# pylint: disable=C0103

# Edit these for every release:

version = '1.4.0'  # Current version number of the application
tskversion = 37  # Current version number of the task file format, changed to 37 for release 1.3.23.
release_day = '28'  # Day number of the release, 1-31, as string
release_month = 'August'  # Month of the release in plain English
release_year = '2013'  # Year of the release as string
release_status = 'stable'  # One of 'alpha', 'beta', 'stable'

# No editing needed below this line for doing a release.

import re, datetime
try:
    from taskcoachlib.meta.revision import revision  # pylint: disable=F0401,W0611
except ImportError:
    revision = None 

months = ['January', 'February', 'March', 'April', 'May', 'June', 
          'July', 'August', 'September', 'October', 'November', 'December']

if revision:  # Buildbot sets revision
    # Decrement version because this version isn't released yet. This
    # assumes that version components are < 100; 99 will actually mean
    # pre-major release
    # pylint: disable=W0141
    major, inter, minor = map(int, version.split('.'))
    numversion = major * 10000 + inter * 100 + minor
    numversion -= 1
    major = numversion // 10000
    inter = (numversion // 100) % 100
    minor = numversion % 100
    version = '.'.join(map(str, [major, inter, minor]))

    now = datetime.datetime.today()
    release_day = str(now.day)
    release_month = months[now.month-1]
    release_year = str(now.year)
    release_status = 'beta'
    version += '.' + revision

assert release_month in months  # Try to prevent typo's
release_month_nr = '%02d' % (months.index(release_month) + 1)
release_day_nr = '%02d' % int(release_day)
date = release_month + ' ' + release_day + ', ' + release_year

name = 'Task Coach'
description = 'Your friendly task manager'
long_description = '%(name)s is a free open source todo manager. It grew ' \
'out of frustration about other programs not handling composite tasks well. ' \
'In addition to flexible composite tasks, %(name)s has grown to include ' \
'prerequisites, prioritizing, effort tracking, category tags, budgets, ' \
'notes, and many other features. However, users are not forced to use all ' \
'these features; %(name)s can be as simple or complex as you need it to be. ' \
'%(name)s is available for Windows, Mac OS X, and GNU/Linux; and there is a ' \
'companion iOS app.' % dict(name=name)
keywords = 'task manager, todo list, pim, time registration, track effort'
author_first, author_last = 'Frank', 'Niessink'  # Needed for PAD file
author = '%s %s, Jerome Laheurte, and Aaron Wolf' % (author_first, author_last)
author_unicode = u'%s %s, Jérôme Laheurte, and Aaron Wolf' % (author_first, author_last)
author_email = 'developers@taskcoach.org'

filename = name.replace(' ', '')
filename_lower = filename.lower()

url = 'http://taskcoach.org/'  # Don't remove the trailing slash, other code is assuming it will be there
screenshot = url + 'screenshots/Windows/0.71.2-Windows_XP-Tasks_categories_and_effort.png'
icon = url + 'taskcoach.png'
pad = url + 'pad.xml'
version_url = url + 'version.txt'
message_url = url + 'messages.txt'
download = url + 'download.html'
dist_download_prefix = 'http://downloads.sourceforge.net/%s' % filename_lower
faq_url = 'https://answers.launchpad.net/taskcoach/+faqs'
sf_tracker_url = 'https://sourceforge.net/tracker/'
bug_report_url = sf_tracker_url + '?func=add&group_id=130831&atid=719134'
known_bugs_url = sf_tracker_url + '?group_id=130831&atid=719134&status=1'
support_request_url = sf_tracker_url + '?group_id=130831&atid=719135'
feature_request_url = 'http://taskcoach.uservoice.com'
translations_url = 'https://translations.launchpad.net/taskcoach'
donate_url = url + 'givesupport.html' 
i18n_url = url + 'i18n.html'

announcement_addresses = 'taskcoach@yahoogroups.com, python-announce-list@python.org'
bcc_announcement_addresses = 'johnhaller@portableapps.com'

copyright = 'Copyright (C) 2004-%s %s'%(release_year, author)  # pylint: disable=W0622
license_title = 'GNU General Public License'
license_version = '3'
license_title_and_version = '%s version %s'%(license_title, license_version) 
license = '%s or any later version'%license_title_and_version  # pylint: disable=W0622
license_title_and_version_abbrev = 'GPLv%s'%license_version
license_abbrev = '%s+'%license_title_and_version_abbrev
license_notice = '''%(name)s is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

%(name)s is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.''' % dict(name=name)

license_notice_html = '<p>%s</p>'%license_notice.replace('\n\n', '</p><p>')
license_notice_html = re.sub(r'<http([^>]*)>', r'<a href="http\1" target="_blank">http\1</a>', license_notice_html)

platform = 'Any'
pythonversion = '2.6'
wxpythonversionnumber = '2.8.9.2'
wxpythonversion = '%s-unicode' % wxpythonversionnumber

languages = {
    'English': None, 
    'Arabic': 'ar',
    'Basque': 'eu',
    'Belarusian': 'be',
    'Bosnian': 'bs',
    'Breton': 'br',
    'Bulgarian': 'bg',
    'Catalan': 'ca',
    'Chinese (Simplified)': 'zh_CN',
    'Chinese (Traditional)': 'zh_TW',
    'Czech': 'cs',
    'Danish': 'da',
    'Dutch': 'nl',
    'Esperanto': 'eo',
    'Estonian': 'et',
    'Finnish': 'fi',
    'French': 'fr', 
    'Galician': 'gl',
    'German': 'de',
    'German (Low)': 'nds',
    'Greek': 'el',
    'Hebrew': 'he',
    'Hindi': 'hi',
    'Hungarian': 'hu',
    'Indonesian': 'id',
    'Italian': 'it',
    'Japanese': 'ja',
    'Korean': 'ko',
    'Latvian': 'lv',
    'Lithuanian': 'lt',
    'Marathi': 'mr',
    'Mongolian': 'mn',
    'Norwegian (Bokmal)': 'nb',
    'Norwegian (Nynorsk)': 'nn',
    'Occitan': 'oc',
    'Papiamento': 'pap',
    'Persian': 'fa',
    'Polish': 'pl',
    'Portuguese': 'pt',
    'Portuguese (Brazilian)': 'pt_BR',
    'Romanian': 'ro',
    'Russian': 'ru',
    'Slovak': 'sk',
    'Slovene': 'sl',
    'Spanish': 'es',
    'Swedish': 'sv',
    'Telugu': 'te',
    'Thai': 'th',
    'Turkish': 'tr',
    'Ukranian': 'uk',
    'Vietnamese': 'vi'}
languages_list = ','.join(languages.keys())

def __createDict(localsDict):
    ''' Provide the local variables as a dictionary for use in string
        formatting. '''
    metaDict = {}  # pylint: disable=W0621
    for key in localsDict:
        if not key.startswith('__'):
            metaDict[key] = localsDict[key]
    return metaDict

metaDict = __createDict(locals())
