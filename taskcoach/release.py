#!/usr/bin/env python

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

# Sanity check
import sys
PYTHONEXE = 'python'

if sys.platform == 'darwin':
    import struct, os, subprocess
    if len(struct.pack('L', 0)) == 8:
        print 'Running 64-bits Python on Darwin; relaunching with 32-bits Python.'
        sys.exit(os.system('python-32 %s' % ' '.join(sys.argv)))
    output = subprocess.check_output(['getconf', 'LONG_BIT']).strip()
    if output == '64':
        PYTHONEXE = 'python-32'

import struct
if sys.platform == 'darwin' and len(struct.pack('L', 0)) == 8:
    raise RuntimeError('Please use python-32 to run this script')


HELP_TEXT = '''
Release steps:
  - Get latest translations from Launchpad:
    * Go to https://translations.launchpad.net/taskcoach/<major.minor>/+export
    * Wait for the confirmation email from Launchpad and copy the URL
    * Run 'cd i18n.in && python make.py <url>' to update the translations
    * Run 'make languagetests' to test the translations
    * When all tests pass, run 'svn commit -m "Updated translations"' 
  - Run 'make reallyclean' to remove old packages.
  - Run 'make alltests'.
  - Run 'python release.py release' to build the distributions, upload and download them
    to/from Sourceforge, generate MD5 digests, generate the website, upload the 
    website to the Dreamhost and Hostland websites, announce the release on 
    Twitter, Identi.ca, Freecode and PyPI (Python Package Index), mark the bug reports
    on SourceForge fixed-and-released, send the 
    announcement email, mark .dmg and .exe files as default downloads for their
    platforms, and to tag the release in Subversion.
  - Create branch if feature release.
  - Merge recent changes to the trunk.
  - Add release to Sourceforge bug tracker and support request groups.
  - Mark feature requests on Uservoice completed.
  - If new release branch, update the buildbot masters configuration.
'''

import ftplib
import smtplib
import httplib
import urllib
import urllib2
import cookielib
import os
import glob
import sys
import getpass
import hashlib
import base64
import ConfigParser
import codecs
import optparse
import taskcoachlib.meta
import oauth2 as oauth
import time
import shutil
import zipfile
import subprocess

try:
    import simplejson as json
except ImportError:
    import json


# pylint: disable=W0621,W0613


def progress(func):
    ''' Decorator to print out a message when a release step starts and print
        a message when the release step is finished. '''
    def inner(*args, **kwargs):
        step = func.__name__.replace('_', ' ')
        print step[0].upper() + step[1:] + '...'
        func(*args, **kwargs)
        print 'Done %s.' % step
    return inner


class Settings(ConfigParser.SafeConfigParser, object):
    def __init__(self):
        super(Settings, self).__init__()
        self.set_defaults()
        self.filename = os.path.expanduser('~/.tcreleaserc')
        self.read(self.filename)

    def set_defaults(self):
        defaults = dict(sourceforge=['username', 'password', 'consumer_key',
                                     'consumer_secret', 'oauth_token',
                                     'oauth_token_secret', 'api_key'],
                        smtp=['hostname', 'port', 'username', 'password',
                              'sender_name', 'sender_email_address'],
                        dreamhost=['hostname', 'username', 'password', 
                                   'folder'],
                        hostland=['hostname', 'username', 'password', 'folder'],
                        pypi=['username', 'password'],
                        twitter=['consumer_key', 'consumer_secret',
                                 'oauth_token', 'oauth_token_secret'],
                        identica=['username', 'password'],
                        freecode=['auth_code'],
                        buildbot=['username', 'password'])
        for section in defaults:
            self.add_section(section)
            for option in defaults[section]:
                self.set(section, option, 'ask')

    def get(self, section, option):  # pylint: disable=W0221
        value = super(Settings, self).get(section, option)
        if value == 'ask':
            get_input = getpass.getpass if option == 'password' else raw_input
            value = get_input('%s %s: ' % (section, option)).strip()
            self.set(section, option, value)
            self.write(file(self.filename, 'w'))
        return value


class HelpFormatter(optparse.IndentedHelpFormatter):
    ''' Don't mess up the help text formatting. '''
    def format_epilog(self, epilog):
        return epilog


class SFAPIError(Exception):
    pass


class SourceforgeAPI(object):
    def __init__(self, settings, options):
        consumer_key = settings.get('sourceforge', 'consumer_key')
        consumer_secret = settings.get('sourceforge', 'consumer_secret')
        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        oauth_token = settings.get('sourceforge', 'oauth_token')
        oauth_token_secret = settings.get('sourceforge', 'oauth_token_secret')
        token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
        self.client = oauth.Client(consumer, token)
        self.verbose = options.verbose
        self.dry_run = options.dry_run

    def __apply(self, func, data=None):
        url = 'https://sourceforge.net/rest/p/taskcoach/' + func
        if data is None:
            response, content = self.client.request(url)
            ok = 200
        else:
            response, content = self.client.request(url, method='POST', body=urllib.urlencode(data))
            ok = 302
        if response.status != ok:
            raise SFAPIError(response.status)
        if data is None:
            return json.loads(content)

    def fix(self, id_):
        if self.dry_run:
            print 'Skipping marking #%s fixed' % id_
        else:
            ticketData = self.__apply('bugs/%s' % id_)['ticket']
            # Status: fixed; priority: 1
            data = [('ticket_form.status', 'fixed')]
            for name, value in ticketData.get('custom_fields', dict()).items():
                if name == '_priority':
                    value = '1'
		if name == '_milestone': # WTF?
		    data.append(('ticket_form._milestone', value))
		else:
		    data.append(('ticket_form.custom_fields.%s' % name, value))
            self.__apply('bugs/%s/save' % id_, data=data)

            # Canned response
            self.__apply('bugs/_discuss/thread/%s/new' % ticketData['discussion_thread']['_id'],
                         data=[('text', '''A fix was made and checked into the source code repository of Task Coach. The fix will be part of the next release. You will get another notification when that release is available with the request to install the new release and confirm that your issue has indeed been fixed.

If you like, you can download a recent build from http://www.fraca7.net/TaskCoach-packages/latest_bugfixes.py to test the fix.

Because a fix has been made for this bug report, the priority of this report has been lowered to 1 and its resolution has been set to 'Fixed'.
Thanks, Task Coach development team''')])

            if self.verbose:
                print 'Bug #%s fixed.' % id_

    def release(self, id_):
        if self.dry_run:
            print 'Skipping marking #%s released.' % id_
        else:
            try:
                ticketData = self.__apply('bugs/%s' % id_)['ticket']
                self.__apply('bugs/%s/save' % id_, data=[('ticket_form.status', 'fixed-and-released')])
                self.__apply('bugs/_discuss/thread/%s/new' % ticketData['discussion_thread']['_id'],
                             data=[('text', '''This bug should be fixed in the latest release of Task Coach. Can you please install the latest release of Task Coach and confirm that this bug has indeed been fixed?

Thanks, Task Coach development team''')])
            except SFAPIError:
                print 'Warning: could not marking fix #%s released.' % id_


def sourceforge_location(settings):
    metadata = taskcoachlib.meta.data.metaDict
    project = metadata['filename_lower']
    project_first_two_letters = project[:2]
    project_first_letter = project[0]
    username = '%s,%s' % (settings.get('sourceforge', 'username'), project)
    folder = '/home/frs/project/%(p)s/%(pr)s/%(project)s/%(project)s/' \
             'Release-%(version)s/' % dict(project=project, 
                                           pr=project_first_two_letters, 
                                           p=project_first_letter, 
                                           version=metadata['version'])
    return '%s@frs.sourceforge.net:%s' % (username, folder)


def rsync(settings, options, rsync_command):
    location = sourceforge_location(settings)
    rsync_command = rsync_command % location
    if options.dry_run:
        print 'Skipping %s.' % rsync_command
    else:
        os.system(rsync_command)


@progress
def building_packages(settings, options):
    metadata = taskcoachlib.meta.data.metaDict
    branch = 'branches/Release%s_Branch' % '_'.join(metadata['version'].split('.')[:2])
    if options.dry_run:
        print 'Skipping force build on branch "%s"' % branch
    else:
        status = json.load(urllib.urlopen('http://www.fraca7.net:8010/json/builders/Release'))
        if status['state'] != 'idle':
            raise RuntimeError('Builder Release is not idle.')

        cj = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        for i in xrange(3): # Retry in case of 500
            try:
                opener.open('http://www.fraca7.net:8010/login',
                            urllib.urlencode([('username', settings.get('buildbot', 'username')),
                                              ('passwd', settings.get('buildbot', 'password'))]))
                opener.open('http://www.fraca7.net:8010/builders/Release/force',
                            urllib.urlencode([('forcescheduler', 'Force'),
                                              ('branch', branch),
                                              ('username', 'release'),
                                              ('reason', 'release')]))
            except urllib2.HTTPError as e:
                print 'Failed to force (%s), retrying' % e
                time.sleep(5)
            else:
                break
        else:
            raise RuntimeError('Could not force build')

        if options.verbose:
            print 'Build forced.'

    if options.verbose:
        print 'Waiting for completion.'

    while True:
        time.sleep(60)
        status = json.load(urllib.urlopen('http://www.fraca7.net:8010/json/builders/Release'))
        if status['state'] == 'idle':
            break

    if options.verbose:
        print 'Build finished.'
        print 'Downloading release.zip'

    buildno = status['cachedBuilds'][-1]
    status = json.load(urllib.urlopen('http://www.fraca7.net:8010/json/builders/Release/builds/%d' % buildno))
    try:
        zipurl = status['steps'][-1]['urls']['Download release']
    except:
        raise RuntimeError('release.zip URL not found. Build failed.')

    if os.path.exists('dist'):
        shutil.rmtree('dist')
    os.mkdir('dist')

    shutil.copyfileobj(urllib.urlopen(zipurl), file(os.path.join('dist', 'release.zip'), 'wb'))

    try:
        zipFile = zipfile.ZipFile(os.path.join('dist', 'release.zip'), 'r')
        try:
            for info in zipFile.infolist():
                if options.verbose:
                    print 'Extracting "%s"' % info.filename
                shutil.copyfileobj(zipFile.open(info, 'r'),
                                   file(os.path.join('dist', info.filename), 'wb'))
        finally:
            zipFile.close()
    finally:
        os.remove(os.path.join('dist', 'release.zip'))


@progress
def uploading_distributions_to_SourceForge(settings, options):
    rsync(settings, options, 'rsync -avP -e ssh dist/* %s')


@progress
def marking_default_downloads(settings, options):
    defaults = list()
    for name in os.listdir('dist'):
        if name.endswith('.dmg'):
            defaults.append(('mac', name))
        elif name.endswith('-win32.exe'):
            defaults.append(('windows', name))

    for platform, name in defaults:
        if options.dry_run:
            print 'Skipping marking "%s" as default for %s' % (name, platform)
        else:
            # httplib does not seem to handle PUT very well
            # See http://stackoverflow.com/questions/111945/is-there-any-way-to-do-http-put-in-python
            opener = urllib2.build_opener(urllib2.HTTPSHandler)
            url = 'https://sourceforge.net/projects/taskcoach/files/taskcoach/Release-%s/%s' % (taskcoachlib.meta.version, name)
            req = urllib2.Request(url,
                                  data=urllib.urlencode(dict(default=platform, api_key=settings.get('sourceforge', 'api_key'))))
            req.add_header('Content-Type', 'application/x-www-form-urlencoded')
            req.get_method = lambda: 'PUT'
            try:
                opener.open(req)
            except urllib2.HTTPError as e:
                print 'Warning: could not mark "%s" as default download for %s (%s)' % (name, platform, e)
            else:
                if options.verbose:
                    print 'Marked "%s" as default download for %s' % (name, platform)


@progress
def marking_bug_fixed(settings, options, *bugIds):
    api = SourceforgeAPI(settings, options)
    for bugId in bugIds:
        api.fix(bugId)


@progress
def marking_bug_released(settings, options, *bugIds):
    api = SourceforgeAPI(settings, options)
    for bugId in bugIds:
        api.release(bugId)


@progress
def downloading_distributions_from_SourceForge(settings, options):
    rsync(settings, options, 'rsync -avP -e ssh %s dist/')


@progress
def generating_MD5_digests(settings, options):
    contents = '''md5digests = {\n'''
    for filename in glob.glob(os.path.join('dist', '*')):
        
        md5digest = hashlib.md5(file(filename, 'rb').read())  # pylint: disable=E1101
        filename = os.path.basename(filename)
        hexdigest = md5digest.hexdigest()
        contents += '''    "%s": "%s",\n''' % (filename, hexdigest)
        if options.verbose:
            print '%40s -> %s' % (filename, hexdigest)
    contents += '}\n'
    
    md5digests_file = file(os.path.join('website.in', 'md5digests.py'), 'w')
    md5digests_file.write(contents)
    md5digests_file.close()


@progress
def generating_website(settings, options):
    os.system('make changes')
    os.chdir('website.in')
    os.system('"%s" make.py' % PYTHONEXE)
    os.chdir('..')


class SimpleFTP(ftplib.FTP, object):
    def __init__(self, hostname, username, password, folder='.'):
        super(SimpleFTP, self).__init__(hostname, username, password)
        self.ensure_folder(folder)
        self.remote_root = folder
            
    def ensure_folder(self, folder):
        try:
            self.cwd(folder)
        except ftplib.error_perm:
            self.mkd(folder)
            self.cwd(folder)    
            
    def put(self, folder, *filename_whitelist):
        for root, subfolders, filenames in os.walk(folder):
            if root != folder:
                print 'Change into %s' % root
                for part in root.split(os.sep):
                    self.cwd(part)
            for subfolder in subfolders:
                print 'Create %s' % os.path.join(root, subfolder)
                try:
                    self.mkd(subfolder)
                except ftplib.error_perm, info:
                    print info
            for filename in filenames:
                if filename_whitelist and filename not in filename_whitelist:
                    print 'Skipping %s' % os.path.join(root, filename)
                    continue
                print 'Store %s' % os.path.join(root, filename)
                try:
                    self.storbinary('STOR %s' % filename, 
                                    file(os.path.join(root, filename), 'rb'))
                except ftplib.error_perm, info:
                    if str(info).endswith('Overwrite permission denied'):
                        self.delete(filename)
                        self.storbinary('STOR %s' % filename, 
                                        file(os.path.join(root, filename), 
                                             'rb'))
                    else:
                        raise
            self.cwd(self.remote_root)

    def get(self, filename):
        print 'Retrieve %s' % filename
        self.retrbinary('RETR %s' % filename, open(filename, 'wb').write)


def uploading_website_to_website_host(settings, options, website_host, 
                                      *filename_whitelist):
    settings_section = website_host.lower()
    hostname = settings.get(settings_section, 'hostname')
    username = settings.get(settings_section, 'username')
    password = settings.get(settings_section, 'password')
    folder = settings.get(settings_section, 'folder')
    
    if hostname and username and password and folder:
        ftp = SimpleFTP(hostname, username, password, folder)
        os.chdir('website.out')
        if options.dry_run:
            print 'Skipping ftp.put(website.out).'
        else:
            ftp.put('.', *filename_whitelist)
        ftp.quit()
        os.chdir('..')
    else:
        print 'Warning: cannot upload website to %s; missing credentials' % \
            website_host


@progress
def uploading_website_to_Dreamhost(settings, options, *args):
    uploading_website_to_website_host(settings, options, 'Dreamhost', *args)
 

@progress
def uploading_website_to_Hostland(settings, options, *args):
    uploading_website_to_website_host(settings, options, 'Hostland', *args)


@progress
def registering_with_PyPI(settings, options):
    username = settings.get('pypi', 'username')
    password = settings.get('pypi', 'password')
    pypirc = file('.pypirc', 'w')
    pypirc.write('[server-login]\nusername = %s\npassword = %s\n' % \
                 (username, password))
    pypirc.close()
    # pylint: disable=W0404
    from setup import setupOptions
    languages_pypi_does_not_know = ['Basque', 'Belarusian', 'Breton', 
        'Estonian', 'Galician', 'Lithuanian', 'Norwegian (Bokmal)', 
        'Norwegian (Nynorsk)', 'Occitan', 'Papiamento', 'Slovene', 
        'German (Low)', 'Mongolian']
    for language in languages_pypi_does_not_know:
        setupOptions['classifiers'].remove('Natural Language :: %s' % language)
    from distutils.core import setup
    del sys.argv[1:]
    os.environ['HOME'] = '.'
    sys.argv.append('register')
    if options.dry_run:
        print 'Skipping PyPI registration.'
    else:
        setup(**setupOptions)  # pylint: disable=W0142
    os.remove('.pypirc')


def postRequest(connection, api_call, body, contentType, ok=200, **headers):
    headers['Content-Type'] = contentType
    connection.request('POST', api_call, body, headers)
    response = connection.getresponse()
    if response.status != ok:
        print 'Request failed: %d %s' % (response.status, response.reason)
        return False
    print 'XXX', response.read() # XXXTMP
    return True


def httpPostRequest(host, api_call, body, contentType, ok=200, port=80, **headers):
    connection = httplib.HTTPConnection(host, port)
    return postRequest(connection, api_call, body, contentType, ok, **headers)


def httpsPostRequest(host, api_call, body, contentType, ok=200, **headers):
    connection = httplib.HTTPSConnection(host)
    return postRequest(connection, api_call, body, contentType, ok, **headers)


@progress
def announcing_on_Freecode(settings, options):
    auth_code = settings.get('freecode', 'auth_code')
    metadata = taskcoachlib.meta.data.metaDict
    version = '%(version)s' % metadata
    changelog = latest_release(metadata, summary_only=True)
    tag = 'Feature enhancements' if version.endswith('.0') else 'Bug fixes'
    release = dict(version=version, changelog=changelog, tag_list=tag)
    body = codecs.encode(json.dumps(dict(auth_code=auth_code, 
                                         release=release)))
    path = '/projects/taskcoach/releases.json'
    host = 'freecode.com'
    if options.dry_run:
        print 'Skipping announcing "%s" on %s.' % (release, host)
    else:
        httpsPostRequest(host, path, body, 'application/json', ok=201)


def status_message():
    ''' Return a brief status message for e.g. Twitter. '''
    metadata = taskcoachlib.meta.data.metaDict
    return "Release %(version)s of %(name)s is available from %(url)s. " \
           "See what's new at %(url)schanges.html." % metadata


def announcing_via_Basic_Auth_Api(settings, options, section, host, 
                                  api_prefix=''):
    credentials = ':'.join(settings.get(section, credential) \
                           for credential in ('username', 'password'))
    basic_auth = base64.encodestring(credentials)[:-1]
    status = status_message()
    api_call = api_prefix + '/statuses/update.json'
    body = '='.join((urllib.quote(body_part.encode('utf-8')) \
                     for body_part in ('status', status)))
    if options.dry_run:
        print 'Skipping announcing "%s" on %s.' % (status, host)
    else:
        httpPostRequest(host, api_call, body, 
                        'application/x-www-form-urlencoded; charset=utf-8',
                        Authorization='Basic %s' % basic_auth)


def announcing_via_OAuth_Api(settings, options, section, host):
    consumer_key = settings.get(section, 'consumer_key')
    consumer_secret = settings.get(section, 'consumer_secret')
    consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
    oauth_token = settings.get(section, 'oauth_token')
    oauth_token_secret = settings.get(section, 'oauth_token_secret')
    token = oauth.Token(key=oauth_token, secret=oauth_token_secret)
    client = oauth.Client(consumer, token)
    status = status_message()
    if options.dry_run:
        print 'Skipping announcing "%s" on %s.' % (status, host)
    else: 
        response, dummy_content = client.request( \
            'http://api.%s/1/statuses/update.json' % host, method='POST', 
            body='status=%s' % status, headers=None)
        if response.status != 200:
            print 'Request failed: %d %s' % (response.status, response.reason)


@progress
def announcing_on_Twitter(settings, options):
    announcing_via_OAuth_Api(settings, options, 'twitter', 'twitter.com')


@progress
def announcing_on_Identica(settings, options):
    announcing_via_Basic_Auth_Api(settings, options, 'identica', 'identi.ca', 
                                  '/api')


def uploading_website(settings, options, *args):
    ''' Upload the website contents to the website(s). If args is present
        only the files specified in args are uploaded. '''
    uploading_website_to_Dreamhost(settings, options, *args)
    uploading_website_to_Hostland(settings, options, *args)
    

def announcing(settings, options):
    registering_with_PyPI(settings, options)
    announcing_on_Twitter(settings, options)
    announcing_on_Identica(settings, options)
    announcing_on_Freecode(settings, options)
    mailing_announcement(settings, options)


def updating_Sourceforge_trackers(settings, options):
    sys.path.insert(0, 'changes.in')
    import changes, changetypes

    for release in changes.releases:
        if release.number == taskcoachlib.meta.version:
            break
    else:
        raise RuntimeError('Could not find version "%s" in changelog' % taskcoachlib.meta.version)

    alreadyDone = set()
    for bugFixed in release.bugsFixed:
        if isinstance(bugFixed, changetypes.Bugv2):
            for id_ in bugFixed.changeIds:
                if id_ not in alreadyDone:
                    alreadyDone.add(id_)
                    if options.dry_run:
                        print 'Skipping mark bug #%s released' % id_
                    else:
                        api = SourceforgeAPI(settings, options)
                        api.release(id_)


def releasing(settings, options):
    building_packages(settings, options)
    uploading_distributions_to_SourceForge(settings, options)
    downloading_distributions_from_SourceForge(settings, options)
    generating_MD5_digests(settings, options)
    generating_website(settings, options)
    uploading_website(settings, options)
    announcing(settings, options)
    updating_Sourceforge_trackers(settings, options)
    tagging_release_in_subversion(settings, options)
    marking_default_downloads(settings, options)


def latest_release(metadata, summary_only=False):
    sys.path.insert(0, 'changes.in')
    # pylint: disable=F0401
    import changes 
    import converter  
    del sys.path[0]
    greeting = 'release %(version)s of %(name)s.' % metadata
    if summary_only:
        greeting = greeting[0].upper() + greeting[1:] 
    else:
        greeting = "We're happy to announce " + greeting
    text_converter = converter.ReleaseToTextConverter()
    convert = text_converter.summary if summary_only else text_converter.convert
    return convert(changes.releases[0], greeting)


@progress
def mailing_announcement(settings, options):
    metadata = taskcoachlib.meta.data.metaDict
    for sender_info in 'sender_name', 'sender_email_address':
        metadata[sender_info] = settings.get('smtp', sender_info)
    metadata['release'] = latest_release(metadata)
    msg = '''To: %(announcement_addresses)s
BCC: %(bcc_announcement_addresses)s
From: %(sender_name)s <%(sender_email_address)s>
Reply-To: %(author_email)s
Subject: [ANN] Release %(version)s of %(name)s

Hi,

%(release)s

What is %(name)s?

%(name)s is a simple task manager that allows for hierarchical tasks, 
i.e. tasks in tasks. %(name)s is open source (%(license_abbrev)s) and is developed 
using Python and wxPython. You can download %(name)s from:

%(url)s

In addition to the source distribution, packaged distributions are available 
for Windows, Mac OS X, Linux, and BSD.

Note that although we consider %(name)s to be %(release_status)s software,
and we do our best to prevent bugs, it is always wise to back up your task 
file regularly, and especially when upgrading to a new release.

Regards, 

%(author)s
Task Coach development team

''' % metadata

    recipients = metadata['announcement_addresses']
    server = settings.get('smtp', 'hostname')
    port = settings.get('smtp', 'port')
    username = settings.get('smtp', 'username')
    password = settings.get('smtp', 'password')

    session = smtplib.SMTP(server, port)
    if options.verbose:
        session.set_debuglevel(1)
    session.helo()
    session.ehlo()
    if password:
        session.starttls()
        session.esmtp_features["auth"] = "LOGIN"  # Needed for Gmail SMTP.
        session.login(username, password)
    if options.dry_run:
        print 'Skipping sending mail.'
        smtpresult = None
    else:
        smtpresult = session.sendmail(username, recipients, msg)

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Could not deliver mail to: %s 
Server said: %s
%s
%s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException, errstr


@progress
def tagging_release_in_subversion(settings, options):
    metadata = taskcoachlib.meta.data.metaDict
    version = metadata['version']
    username = settings.get('sourceforge', 'username') 
    release_tag = 'Release' + version.replace('.', '_')
    output = subprocess.check_output(['svn', 'info'])
    for line in output.split('\n'):
        if line.startswith('URL: '):
            source_url = line[5:].strip()
            break
    else:
        raise RuntimeError('Could not find source URL')

    if source_url.startswith('https://'):
        tag_url = 'https://svn.code.sf.net/p/taskcoach/code/tags/'
    else:
        tag_url = 'svn+ssh://%s@svn.code.sf.net/p/taskcoach/code/tags/' % username
    target_url = tag_url + release_tag
    commit_message = 'Tag for release %s.' % version
    svn_copy = 'svn copy -m "%s" %s %s' % (commit_message, source_url, target_url)
    if options.dry_run:
        print 'Skipping %s.' % svn_copy
    else:
        os.system(svn_copy)


COMMANDS = dict(release=releasing,
                build=building_packages,
                upload=uploading_distributions_to_SourceForge, 
                download=downloading_distributions_from_SourceForge, 
                md5=generating_MD5_digests,
                websitegen=generating_website,
                website=uploading_website,
                websiteDH=uploading_website_to_Dreamhost,
                websiteHL=uploading_website_to_Hostland,
                twitter=announcing_on_Twitter,
                identica=announcing_on_Identica,
                freecode=announcing_on_Freecode,
                pypi=registering_with_PyPI, 
                mail=mailing_announcement,
                announce=announcing,
                update=updating_Sourceforge_trackers,
                tag=tagging_release_in_subversion,
                markdefault=marking_default_downloads,
                markfixed=marking_bug_fixed,
                markreleased=marking_bug_released)

USAGE = 'Usage: %%prog [options] [%s]' % '|'.join(sorted(COMMANDS.keys()))

SETTINGS = Settings()

parser = optparse.OptionParser(usage=USAGE, epilog=HELP_TEXT, 
                               formatter=HelpFormatter())
parser.add_option('-n', '--dry-run', action='store_true', dest='dry_run', 
                  help="don't make permanent changes")
parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                  help='provide more detailed progress information')
options, args = parser.parse_args()

try:
    if len(args) > 1:
        COMMANDS[args[0]](SETTINGS, options, *args[1:])  # pylint: disable=W0142
    else:
        COMMANDS[args[0]](SETTINGS, options)
except (KeyError, IndexError):
    parser.print_help()
