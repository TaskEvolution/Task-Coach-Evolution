# -*- coding: utf-8 -*-

'''
Task Coach - Your friendly task manager
Copyright (C) 2004-2013 Task Coach developers <developers@taskcoach.org>
Copyright (C) 2013 Marcus Johansson <marcus1.johansson@gmail.com>

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
from taskcoachlib.thirdparty.googleapi import httplib2
import os
import wx

from taskcoachlib.thirdparty.googleapi.apiclient import discovery
from taskcoachlib.thirdparty.googleapi.oauth2client import file
from taskcoachlib.thirdparty.googleapi.oauth2client import client
from taskcoachlib.thirdparty.googleapi.oauth2client import tools

# Parser for command-line arguments.
parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawDescriptionHelpFormatter,
    parents=[tools.argparser])


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__),'client_secrets.json')

# Set up a Flow object to be used for authentication.
# Add one or more of the following scopes.
FLOW = client.flow_from_clientsecrets(CLIENT_SECRETS,
  scope=[
      'https://www.googleapis.com/auth/tasks',
      'https://www.googleapis.com/auth/tasks.readonly',
    ],
    message=tools.message_if_missing(CLIENT_SECRETS))


def connect(argv):
  # Parse the command-line flags.
  flags = parser.parse_args(argv[1:])

  # If the credentials don't exist or are invalid run through the native client
  # flow. The Storage object will ensure that if successful the good
  # credentials will get written back to the file.
  storage = file.Storage('credentials.dat')
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    wx.MessageBox("Click OK to open webbrowser and authorize TaskCoach to access your Google Tasks",'Authorization',wx.OK|wx.ICON_INFORMATION)
    credentials = tools.run_flow(FLOW, storage, flags)
    if credentials is None:
        return None
  # Create an httplib2.Http object to handle our HTTP requests and authorize it
  # with our good Credentials.
  http = httplib2.Http()
  http = credentials.authorize(http)

  # Construct the service object for the interacting with the Tasks API.
  return discovery.build('tasks', 'v1', http=http)
