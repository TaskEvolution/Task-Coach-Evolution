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

import argparse
from dropbox import client, rest, session
import os
import sys
import webbrowser
import wx

TOKENS_FILE = os.path.join(os.path.dirname(__file__),'dropbox_tokens.dat')
DROPBOX_APP_KEY = '3jlovmrpanxteqg'
DROPBOX_APP_SECRET = 'ckptu9i11x0ir7a'
access_type = 'app_folder'

def dbclient():
    # Get your app key and secret from the Dropbox developer website
    sess = session.DropboxSession(DROPBOX_APP_KEY, DROPBOX_APP_SECRET, access_type)
    
    token_key,token_secret = readTokenFile()
    if len(token_key) == 0:
        token_key, token_secret = obtainTokens(sess)
        if len(token_key) == 0:
            return None, "Authorization not passed."
    writeTokenFile(token_key, token_secret)
    sess.set_token(token_key, token_secret)
    dbclient = client.DropboxClient(sess)
    if testDropboxClient(dbclient):
        return dbclient, "OK."
    return None, "Problem with authorization. Try again."

def readTokenFile():
    try:
        token_file = open(TOKENS_FILE, 'r')
    except:
        return "", ""
    token_file_contents = token_file.read()
    token_file.close()
    # if size of the token file is zero
    if len(token_file_contents) == 0:
        #wx.MessageBox('Token file empty!', 'Token file', wx.OK | wx.ICON_INFORMATION)
        return "", ""
    # else, read token_key and token_secret 
    token_key,token_secret = token_file_contents.split('|')
    return token_key, token_secret

def writeTokenFile(key, secret):
    #wx.MessageBox('Writing to token file', 'Token file', wx.OK | wx.ICON_INFORMATION)
    token_file = open(TOKENS_FILE, 'w')
    token_file.write("%s|%s" % (key, secret))
    token_file.close()

def obtainTokens(session):
    request_token = session.obtain_request_token()
    url = session.build_authorize_url(request_token)
    webbrowser.open(url, new=2)
    wx.MessageBox('Go to web browser and allow Task Coach Backup Folder to create a folder in your Dropbox. Click OK when done.', 'Authorize Dropbox in Web Browser', wx.OK | wx.ICON_EXCLAMATION)
    try:
        access_token = session.obtain_access_token(request_token)
        return access_token.key, access_token.secret
    except:
        return "", ""
    
def deleteTokenFile():
    try:
        os.remove(TOKENS_FILE)
    except OSError:
        pass
    
def testDropboxClient(dbclient):
    try:
        response = dbclient.account_info()
        return True
    # dropbox.rest.ErrorResponse
    except rest.ErrorResponse:
        deleteTokenFile()
        return False
    
# get dropbox folder metadata
def folderMetadata(dbclient):
    return dbclient.metadata('/')

# get filenames in dropbox app folder
def fileNames(dbclient):
    metadata = folderMetadata(dbclient)
    filenameList = []
    for listelement in metadata['contents']:
        if listelement['is_dir'] == False and 'tsk' in listelement['path']:
            filenameList.append(listelement['path'])
    return filenameList

# download file from dropbox by filename
def restorefile(dbclient, filename):
    file, metadata = dbclient.get_file_and_metadata(filename)
    return file