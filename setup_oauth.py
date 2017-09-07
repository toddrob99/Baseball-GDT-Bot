import praw
import os
import simplejson as json
import webbrowser

cwd = os.path.dirname(os.path.realpath(__file__))
while True:
    fatal_errors = []
    with open(cwd + '/src/settings.json') as data:
        SETTINGS = json.load(data)

        if SETTINGS.get('CLIENT_ID') == None: 
            fatal_errors.append('Missing CLIENT_ID')

        if SETTINGS.get('CLIENT_SECRET') == None:
            fatal_errors.append('Missing CLIENT_SECRET')

        if SETTINGS.get('REDIRECT_URI') == None:
            fatal_errors.append('Missing REDIRECT_URI')

        FULL_UA = 'Baseball Game Thread for Reddit - Setup v1.1 https://github.com/toddrob99/Baseball-GDT-Bot'
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
