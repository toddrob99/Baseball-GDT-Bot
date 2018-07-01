#!/usr/bin/env python
import praw
import sys
import os
import simplejson as json
import webbrowser

settings_path = os.path.dirname(os.path.realpath(__file__)) + '/'
settings_file = 'settings.json'
if len(sys.argv)>1:
    settings_file = next((x.split('=')[1] for x in sys.argv if x.startswith('--settings=') or x.startswith('-settings=') or x.startswith('/settings=')),'settings.json')
if settings_file.find('/') == -1 and settings_file.find('\\') == -1: #absolute path not provided, assume same path as main.py
    settings_file = settings_path + 'src/' + settings_file
while True:
    fatal_errors = []
    with open(settings_file) as data:
        SETTINGS = json.load(data)

        if SETTINGS.get('CLIENT_ID') in [None,"","XXX"]: 
            fatal_errors.append('Missing CLIENT_ID')

        if SETTINGS.get('CLIENT_SECRET') in [None,"","XXX"]:
            fatal_errors.append('Missing CLIENT_SECRET')

        if SETTINGS.get('REDIRECT_URI') in [None,"","XXX"]:
            fatal_errors.append('Missing REDIRECT_URI')

        FULL_UA = 'Baseball Game Thread for Reddit - Setup v1.2 https://github.com/toddrob99/Baseball-GDT-Bot'
        if SETTINGS.get('USER_AGENT') != None:
            FULL_UA += ' ' + SETTINGS.get('USER_AGENT')

        if len(fatal_errors):
            for fatal_err in fatal_errors:
                print "FATAL ERROR:",fatal_err
            print "Please fix the error(s) listed above and press Enter to try again. See instructions in README.md."
            raw_input()
        else: break

r = praw.Reddit(client_id=SETTINGS.get('CLIENT_ID'),
                client_secret=SETTINGS.get('CLIENT_SECRET'),
                redirect_uri=SETTINGS.get('REDIRECT_URI'),
                user_agent=FULL_UA)

url = r.auth.url(['identity', 'submit', 'edit', 'read', 'modposts', 'privatemessages', 'flair', 'modflair'], '...', 'permanent')
webbrowser.open(url)

var_input = raw_input("Enter code: ")
access_information = r.auth.authorize(var_input)
print "Refresh token:",access_information
