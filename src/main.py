#!/usr/bin/env python

'''

BASEBALL GAME THREAD BOT FOR REDDIT
https://github.com/toddrob99/Baseball-GDT-Bot

Written by:
/u/toddrob

Please contact me on Reddit or Github if you have any questions.

Forked from https://github.com/mattabullock/Baseball-GDT-Bot
Written by:
/u/DetectiveWoofles
/u/avery_crudeman
/u/toddrob

'''

import editor
from datetime import datetime
import timecheck
import time
import simplejson as json
import praw
import urllib2

class Bot:

    def __init__(self):
        self.VERSION = '4.2.0'
        self.BOT_TIME_ZONE = None
        self.TEAM_TIME_ZONE = None
        self.POST_TIME = None
        self.USERNAME = None
        self.PASSWORD = None
        self.SUBREDDIT = None
        self.TEAM_CODE = None
        self.PREGAME_THREAD = None
        self.CONSOLIDATE_PRE = None
        self.HOLD_DH_GAME2_THREAD = None
        self.POST_GAME_THREAD = None
        self.STICKY = None
        self.SUGGESTED_SORT = None
        self.MESSAGE = None
        self.INBOXREPLIES = None
        self.WINLOSS_POST_THREAD_TAGS = None
        self.FLAIR_MODE = None
        self.OFFDAY_THREAD_SETTINGS = None
        self.PRE_THREAD_SETTINGS = None
        self.THREAD_SETTINGS = None
        self.POST_THREAD_SETTINGS = None
        self.LOG_LEVEL = None

    def read_settings(self):
        import os
        cwd = os.path.dirname(os.path.realpath(__file__))
        fatal_errors = []
        warnings = []
        with open(cwd + '/settings.json') as data:
            settings = json.load(data)

            self.CLIENT_ID = settings.get('CLIENT_ID')
            if self.CLIENT_ID == None: 
                fatal_errors.append('Missing CLIENT_ID')

            self.CLIENT_SECRET = settings.get('CLIENT_SECRET')
            if self.CLIENT_SECRET == None:
                fatal_errors.append('Missing CLIENT_SECRET')

            self.USER_AGENT = settings.get('USER_AGENT')
            if self.USER_AGENT == None:
                warnings.append('Missing USER_AGENT, using default ("")...')
                self.USER_AGENT = ''
            self.USER_AGENT = "OAuth Baseball Game Thread Bot for Reddit v" + self.VERSION + " https://github.com/toddrob99/Baseball-GDT-Bot " + self.USER_AGENT

            self.REDIRECT_URI = settings.get('REDIRECT_URI')
            if self.REDIRECT_URI == None:
                fatal_errors.append('Missing REDIRECT_URI')

            self.REFRESH_TOKEN = settings.get('REFRESH_TOKEN')
            if self.REFRESH_TOKEN == None:
                fatal_errors.append('Missing REFRESH_TOKEN')

            self.BOT_TIME_ZONE = settings.get('BOT_TIME_ZONE')
            if self.BOT_TIME_ZONE == None:
                warnings.append('Missing BOT_TIME_ZONE, using default (ET)...')
                self.BOT_TIME_ZONE = 'ET'

            self.TEAM_TIME_ZONE = settings.get('TEAM_TIME_ZONE')
            if self.TEAM_TIME_ZONE == None:
                warnings.append('Missing TEAM_TIME_ZONE, using default (ET)...')
                self.TEAM_TIME_ZONE = 'ET'

            self.POST_TIME = settings.get('POST_TIME')
            if self.POST_TIME == None:
                warnings.append('Missing POST_TIME, using default (3)...')
                self.POST_TIME = 3

            self.SUBREDDIT = settings.get('SUBREDDIT')
            if self.SUBREDDIT == None:
                fatal_errors.append('Missing SUBREDDIT')

            self.TEAM_CODE = settings.get('TEAM_CODE').lower()
            if self.TEAM_CODE == None:
                fatal_errors.append('Missing TEAM_CODE')

            self.OFFDAY_THREAD = settings.get('OFFDAY_THREAD')
            if self.OFFDAY_THREAD == None:
                warnings.append('Missing OFFDAY_THREAD, using default (true)...')
                self.OFFDAY_THREAD = True
            
            self.PREGAME_THREAD = settings.get('PREGAME_THREAD')
            if self.PREGAME_THREAD == None:
                warnings.append('Missing PREGAME_THREAD, using default (true)...')
                self.PREGAME_THREAD = True
            
            self.CONSOLIDATE_PRE = settings.get('CONSOLIDATE_PRE')
            if self.CONSOLIDATE_PRE == None:
                warnings.append('Missing CONSOLIDATE_PRE, using default (true)...')
                self.CONSOLIDATE_PRE = True

            self.HOLD_DH_GAME2_THREAD = settings.get('HOLD_DH_GAME2_THREAD')
            if self.HOLD_DH_GAME2_THREAD == None:
                warnings.append('Missing HOLD_DH_GAME2_THREAD, using default (true)...')
                self.HOLD_DH_GAME2_THREAD = True

            self.POST_GAME_THREAD = settings.get('POST_GAME_THREAD')
            if self.POST_GAME_THREAD == None:
                warnings.append('Missing POST_GAME_THREAD, using default (true)...')
                self.POST_GAME_THREAD = True

            self.STICKY = settings.get('STICKY')
            if self.STICKY == None:
                warnings.append('Missing STICKY, using default (true - make sure your bot user has mod rights)...')
                self.STICKY = True

            self.SUGGESTED_SORT = settings.get('SUGGESTED_SORT')
            if self.SUGGESTED_SORT == None:
                warnings.append('Missing SUGGESTED_SORT, using default (new - make sure your bot user has mod rights)...')
                self.SUGGESTED_SORT = False

            self.MESSAGE = settings.get('MESSAGE')
            if self.MESSAGE == None:
                warnings.append('Missing MESSAGE, using default (false)...')
                self.MESSAGE = False

            self.INBOXREPLIES = settings.get('INBOXREPLIES')
            if self.INBOXREPLIES == None:
                warnings.append('Missing INBOXREPLIES, using default (false)...')
                self.INBOXREPLIES = False

            self.FLAIR_MODE = settings.get('FLAIR_MODE')
            if self.FLAIR_MODE not in ['', 'none', 'submitter', 'mod']:
                warnings.append('Missing or invalid FLAIR_MODE, using default (none)...')
                self.FLAIR_MODE = 'none'

            temp_settings = settings.get('OFFDAY_THREAD_SETTINGS')
            if temp_settings == None:
                warnings.append('Missing OFFDAY_THREAD_SETTINGS, using defaults (OFFDAY_THREAD_TAG: "OFF DAY THREAD:", OFFDAY_THREAD_TIME: 9AM, OFFDAY_THREAD_BODY: "No game today.", OFFDAY_THREAD_FLAIR: "")...')
                self.OFFDAY_THREAD_SETTINGS = ('OFF DAY THREAD:','9AM','No game today.','')
            else:
                self.OFFDAY_THREAD_SETTINGS = (temp_settings.get('OFFDAY_THREAD_TAG'),temp_settings.get('OFFDAY_THREAD_TIME'),
                                                temp_settings.get('OFFDAY_THREAD_BODY'), temp_settings.get('OFFDAY_THREAD_FLAIR')
                                            )
            if self.OFFDAY_THREAD_SETTINGS[0] == None:
                warnings.append('Missing OFFDAY_THREAD_SETTINGS : OFFDAY_THREAD_TAG, using default ("OFF DAY THREAD:")...')
                self.OFFDAY_THREAD_SETTINGS[0] = ('OFF DAY THREAD:')
            if self.OFFDAY_THREAD_SETTINGS[1] == None:
                warnings.append('Missing OFFDAY_THREAD_SETTINGS : OFFDAY_THREAD_TIME, using default ("9AM")...')
                self.OFFDAY_THREAD_SETTINGS[1] = ('9AM')
            if self.OFFDAY_THREAD_SETTINGS[2] == None:
                warnings.append('Missing OFFDAY_THREAD_SETTINGS : OFFDAY_THREAD_BODY, using default ("No game today.")...')
                self.OFFDAY_THREAD_SETTINGS[2] = ('No game today.')
            if self.OFFDAY_THREAD_SETTINGS[3] == None:
                warnings.append('Missing OFFDAY_THREAD_SETTINGS : OFFDAY_THREAD_FLAIR, using default ("")...')
                self.OFFDAY_THREAD_SETTINGS[3] = ('')

            temp_settings = settings.get('PRE_THREAD_SETTINGS')
            if temp_settings == None:
                warnings.append('Missing PRE_THREAD_SETTINGS, using defaults (PRE_THREAD_TAG: "PREGAME THREAD:", PRE_THREAD_TIME: 9AM, FLAIR: "", PROBABLES: true, FIRST_PITCH: true, DESCRIPTION: true)...')
                self.PRE_THREAD_SETTINGS = ('PREGAME THREAD:','9AM','',(True,True,True))
            else:
                content_settings = temp_settings.get('CONTENT')
                if content_settings == None:
                    warnings.append('Missing PRE_THREAD_SETTINGS : CONTENT, using defaults (PROBABLES: true, FIRST_PITCH: true, DESCRIPTION: true)...')
                    self.PRE_THREAD_SETTINGS = (temp_settings.get('PRE_THREAD_TAG'),temp_settings.get('PRE_THREAD_TIME'), temp_settings.get('FLAIR'), (True,True,True))
                else:
                    self.PRE_THREAD_SETTINGS = (temp_settings.get('PRE_THREAD_TAG'),temp_settings.get('PRE_THREAD_TIME'), temp_settings.get('FLAIR'),
                                                    (content_settings.get('PROBABLES'),content_settings.get('FIRST_PITCH'),content_settings.get('DESCRIPTION'))
                                               )
            if self.PRE_THREAD_SETTINGS[0] == None:
                warnings.append('Missing PRE_THREAD_SETTINGS : PRE_THREAD_TAG, using default ("PREGAME THREAD:")...')
                self.PRE_THREAD_SETTINGS[0] = 'PREGAME THREAD:'
            if self.PRE_THREAD_SETTINGS[1] == None:
                warnings.append('Missing PRE_THREAD_SETTINGS : PRE_THREAD_TIME, using default ("9AM")...')
                self.PRE_THREAD_SETTINGS[1] = '9AM'
            if self.PRE_THREAD_SETTINGS[2] == None:
                warnings.append('Missing PRE_THREAD_SETTINGS : FLAIR, using default ("")...')
                self.PRE_THREAD_SETTINGS[2] = '9AM'
            if self.PRE_THREAD_SETTINGS[3][0] == None:
                warnings.append('Missing PRE_THREAD_SETTINGS : CONTENT : PROBABLES, using default (true)...')
                self.PRE_THREAD_SETTINGS[3][0] = True
            if self.PRE_THREAD_SETTINGS[3][1] == None:
                warnings.append('Missing PRE_THREAD_SETTINGS : CONTENT : FIRST_PITCH, using default (true)...')
                self.PRE_THREAD_SETTINGS[3][1] = True
            if self.PRE_THREAD_SETTINGS[3][2] == None:
                warnings.append('Missing PRE_THREAD_SETTINGS : CONTENT : DESCRIPTION, using default (true)...')
                self.PRE_THREAD_SETTINGS[3][2] = True

            temp_settings = settings.get('THREAD_SETTINGS')
            if temp_settings == None:
                warnings.append('Missing THREAD_SETTINGS, using defaults (THREAD_TAG: "GAME THREAD:", FLAIR: "", HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "**Remember to sort by new to keep up!**", THEATER_LINK: false)...')
                self.THREAD_SETTINGS = ('GAME THREAD:', '', (True, True, True, True, True, '**Remember to sort by new to keep up!**', False))
            else:
                content_settings = temp_settings.get('CONTENT')
                if content_settings == None:
                    warnings.append('Missing THREAD_SETTINGS : CONTENT, using defaults (HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "**Remember to sort by new to keep up!**", THEATER_LINK: false)...')
                    self.THREAD_SETTINGS = (temp_settings.get('THREAD_TAG'), temp_settings.get('FLAIR'), (True, True, True, True, True, '**Remember to sort by new to keep up!**', False))
                else:
                    self.THREAD_SETTINGS = (temp_settings.get('THREAD_TAG'), temp_settings.get('FLAIR'),
                                            (content_settings.get('HEADER'), content_settings.get('BOX_SCORE'),
                                             content_settings.get('LINE_SCORE'), content_settings.get('SCORING_PLAYS'),
                                             content_settings.get('HIGHLIGHTS'), content_settings.get('FOOTER'), content_settings.get('THEATER_LINK'))
                                         )
            if self.THREAD_SETTINGS[0] == None:
                warnings.append('Missing THREAD_SETTINGS : THREAD_TAG, using default ("GAME THREAD:")...') 
                self.THREAD_SETTINGS[0] = 'GAME THREAD:'
            if self.THREAD_SETTINGS[1] == None:
                warnings.append('Missing THREAD_SETTINGS : FLAIR, using default ("")...') 
                self.THREAD_SETTINGS[1] = ''
            if self.THREAD_SETTINGS[2][0] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : HEADER, using default (true)...') 
                self.THREAD_SETTINGS[2][0] = True
            if self.THREAD_SETTINGS[2][1] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : BOX_SCORE, using default (true)...') 
                self.THREAD_SETTINGS[2][1] = True
            if self.THREAD_SETTINGS[2][2] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : LINE_SCORE, using default (true)...') 
                self.THREAD_SETTINGS[2][2] = True
            if self.THREAD_SETTINGS[2][3] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : LINE_SCORE, using default (true)...') 
                self.THREAD_SETTINGS[2][3] = True
            if self.THREAD_SETTINGS[2][4] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : HIGHLIGHTS, using default (true)...') 
                self.THREAD_SETTINGS[2][4] = True
            if self.THREAD_SETTINGS[2][5] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : FOOTER, using default ("**Remember to sort by new to keep up!**")...') 
                self.THREAD_SETTINGS[2][5] = True
            if self.THREAD_SETTINGS[2][6] == None:
                warnings.append('Missing THREAD_SETTINGS : CONTENT : THEATER_LINK, using default (false)...') 
                self.THREAD_SETTINGS[2][6] = False

            temp_settings = settings.get('POST_THREAD_SETTINGS')
            if temp_settings == None:
                warnings.append('Missing POST_THREAD_SETTINGS, using defaults (POST_THREAD_TAG: "POST GAME THREAD:", POST_THREAD_WIN_TAG: "OUR TEAM WON:", POST_THREAD_LOSS_TAG: "OUR TEAM LOST:", FLAIR: "", HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "", THEATER_LINK: true)...')
                self.POST_THREAD_SETTINGS = ('POST GAME THREAD:', '', 'OUR TEAM WON:', 'OUR TEAM LOST:', (True, True, True, True, True, '', True))
            else:
                content_settings = temp_settings.get('CONTENT')
                if content_settings == None:
                    warnings.append('Missing POST_THREAD_SETTINGS : CONTENT, using defaults (HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "", THEATER_LINK: true)...')
                    self.POST_THREAD_SETTINGS = (temp_settings.get('POST_THREAD_TAG'), temp_settings.get('FLAIR'), temp_settings.get('POST_THREAD_WIN_TAG'), temp_settings.get('POST_THREAD_LOSS_TAG'), (True, True, True, True, True, '', True))
                else:
                    self.POST_THREAD_SETTINGS = (temp_settings.get('POST_THREAD_TAG'), temp_settings.get('FLAIR'), temp_settings.get('POST_THREAD_WIN_TAG'), temp_settings.get('POST_THREAD_LOSS_TAG'),
                                            (content_settings.get('HEADER'), content_settings.get('BOX_SCORE'),
                                             content_settings.get('LINE_SCORE'), content_settings.get('SCORING_PLAYS'),
                                             content_settings.get('HIGHLIGHTS'), content_settings.get('FOOTER'), content_settings.get('THEATER_LINK'))
                                         )
            if self.POST_THREAD_SETTINGS[0] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : POST_THREAD_TAG, using default ("POST GAME THREAD:")...')
                self.POST_THREAD_SETTINGS[0] = 'POST GAME THREAD:'
            if self.POST_THREAD_SETTINGS[0] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : FLAIR, using default ("")...')
                self.POST_THREAD_SETTINGS[0] = ''
            if self.POST_THREAD_SETTINGS[0] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : POST_THREAD_WIN_TAG, using default ("OUR TEAM WON:")...')
                self.POST_THREAD_SETTINGS[0] = 'OUR TEAM WON:'
            if self.POST_THREAD_SETTINGS[0] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : POST_THREAD_LOSS_TAG, using default ("OUR TEAM LOST:")...')
                self.POST_THREAD_SETTINGS[0] = 'OUR TEAM LOST:'
            if self.POST_THREAD_SETTINGS[4][0] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : HEADER, using default (true)...')
                self.POST_THREAD_SETTINGS[4][0] = True
            if self.POST_THREAD_SETTINGS[4][1] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : BOX_SCORE, using default (true)...')
                self.POST_THREAD_SETTINGS[4][1] = True
            if self.POST_THREAD_SETTINGS[4][2] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : LINE_SCORE, using default (true)...')
                self.POST_THREAD_SETTINGS[4][2] = True
            if self.POST_THREAD_SETTINGS[4][3] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : SCORING_PLAYS, using default (true)...')
                self.POST_THREAD_SETTINGS[4][3] = True
            if self.POST_THREAD_SETTINGS[4][4] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : HIGHLIGHTS, using default (true)...')
                self.POST_THREAD_SETTINGS[4][4] = True
            if self.POST_THREAD_SETTINGS[4][5] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : FOOTER, using default ("")...')
                self.POST_THREAD_SETTINGS[4][5] = ''
            if self.POST_THREAD_SETTINGS[4][5] == None:
                warnings.append('Missing POST_THREAD_SETTINGS : CONTENT : THEATER_LINK, using default (True)...')
                self.POST_THREAD_SETTINGS[4][5] = True

            self.WINLOSS_POST_THREAD_TAGS = settings.get('WINLOSS_POST_THREAD_TAGS')
            if self.WINLOSS_POST_THREAD_TAGS == None:
                warnings.append('Missing WINLOSS_POST_THREAD_TAGS, using default (false)...')
                self.WINLOSS_POST_THREAD_TAGS = False
            
            self.LOG_LEVEL = settings.get('LOG_LEVEL')
            if self.LOG_LEVEL == None:
                warnings.append('Missing LOG_LEVEL, using default (2)...')
                self.LOG_LEVEL = 2
            
            results = {'fatal' : fatal_errors, 'warnings' : warnings}

        return results

    def run(self):

        try:
            settings_results = self.read_settings()
        except Exception, err:
            print "FATAL ERROR: Cannot read settings from src/settings.json:",err
            return
            
        warnings = settings_results.get('warnings',[])
        fatal_errors = settings_results.get('fatal',[])
        
        if len(warnings):
            if self.LOG_LEVEL>1:
                for warn in warnings:
                    print "WARNING:",warn
        
        if len(fatal_errors):
            if self.LOG_LEVEL>0:
                for fatal_err in fatal_errors:
                    print "FATAL ERROR:",fatal_err
            return

        if self.LOG_LEVEL>2: print "Initiating PRAW instance with User Agent:",self.USER_AGENT
        r = praw.Reddit(client_id=self.CLIENT_ID,
                        client_secret=self.CLIENT_SECRET,
                        refresh_token=self.REFRESH_TOKEN,
                        user_agent=self.USER_AGENT)

        if self.TEAM_TIME_ZONE == 'ET':
            time_info = (self.TEAM_TIME_ZONE,0)
        elif self.TEAM_TIME_ZONE == 'CT':
            time_info = (self.TEAM_TIME_ZONE,1)
        elif self.TEAM_TIME_ZONE == 'MT':
            time_info = (self.TEAM_TIME_ZONE,2)
        elif self.TEAM_TIME_ZONE == 'PT':
            time_info = (self.TEAM_TIME_ZONE,3)
        else:
            if self.LOG_LEVEL>1: print "WARNING: Invalid team time zone setting. Must be ET, CT, MT, PT. Defaulting to ET."
            self.TEAM_TIME_ZONE = 'ET'
            time_info = (self.TEAM_TIME_ZONE,0)

        edit = editor.Editor(time_info, self.PRE_THREAD_SETTINGS,
                self.THREAD_SETTINGS, self.POST_THREAD_SETTINGS, self.LOG_LEVEL)

        if edit.lookup_team_info(field='team_code',lookupfield='team_code',lookupval=self.TEAM_CODE) != self.TEAM_CODE:
            if self.LOG_LEVEL>0: print "FATAL ERROR: Invalid team code detected:",self.TEAM_CODE,"- use lookup_team_code.py to look up the correct team code; see README.md"
            return

        if self.BOT_TIME_ZONE == 'ET':
            time_before = self.POST_TIME * 60 * 60
        elif self.BOT_TIME_ZONE == 'CT':
            time_before = (1 + self.POST_TIME) * 60 * 60
        elif self.BOT_TIME_ZONE == 'MT':
            time_before = (2 + self.POST_TIME) * 60 * 60
        elif self.BOT_TIME_ZONE == 'PT':
            time_before = (3 + self.POST_TIME) * 60 * 60
        else:
            if self.LOG_LEVEL>1: print "Invalid bot time zone setting. Must be ET, CT, MT, PT. Defaulting to ET."
            self.BOT_TIME_ZONE = 'ET'
            time_before = self.POST_TIME * 60 * 60

        timechecker = timecheck.TimeCheck(time_before, self.LOG_LEVEL, self.HOLD_DH_GAME2_THREAD)
        
        games = {}
        offday = {}
        threads = {}

        while True:
            today = datetime.today()

            url = "http://gd2.mlb.com/components/game/mlb/"
            url = url + "year_" + today.strftime("%Y") + "/month_" + today.strftime("%m") + "/day_" + today.strftime("%d") + "/"

            response = ""
            while not response:
                try:
                    response = urllib2.urlopen(url)
                except:
                    if self.LOG_LEVEL>0: print "Couldn't find URL, retrying in 30 seconds..."
                    time.sleep(30)

            html = response.readlines()
            directories = []
            for v in html:
                if self.TEAM_CODE + 'mlb' in v:
                    v = v[v.index("\"") + 1:len(v)]
                    v = v[0:v.index("\"")]
                    directories.append(url + v)

            if len(offday): stale_games[0] = offday
            else: stale_games = games
            if self.LOG_LEVEL>2: print "stale games:",stale_games

            threads = {}
            offday = {}
            othergame = {}
            games = {}
            activegames = completedgames = previewgames = maxapi = 0
            skipflag = False
            i = 1
            for u in directories:
                games[i] = {'url' : u, 'gamenum' : u[-2:-1], 'doubleheader' : False, 'final' : False, 'status' : edit.get_status(u)}
                threads[i] = {'game' : '', 'post' : '', 'pre' : ''}
                if u[-2:-1] != '1':
                    if self.LOG_LEVEL>1: print "Game",i,"detected as doubleheader..."
                    games[i].update({'doubleheader' : True})
                    for tk,tgame in games.items():
                        if tgame.get('url')[:-2] == u[:-2] and tk != i:
                            tgame.update({'doubleheader' : True})
                            if self.LOG_LEVEL>1: print "Game",tk,"marked as other game in doubleheader..."
                i += 1
            if self.LOG_LEVEL>2: print "games:",games
            pendinggames = len(games)

            if len(games) == 0:
                if self.LOG_LEVEL>1: print "No games today..."

            if self.OFFDAY_THREAD and len(games) == 0:
                timechecker.pregamecheck(self.OFFDAY_THREAD_SETTINGS[1])
                offday.update({'offtitle': self.OFFDAY_THREAD_SETTINGS[0] + " " + datetime.strftime(datetime.today(), "%A, %B %d"), 'offmessage' : self.OFFDAY_THREAD_SETTINGS[2]})
                try:
                    subreddit = r.subreddit(self.SUBREDDIT)
                    for submission in subreddit.new():
                        if submission.title == offday.get('offtitle'):
                            if self.LOG_LEVEL>1: print "Offday thread already posted, getting submission..."
                            offday.update({'offsub' : submission})
                            break

                    if not offday.get('offsub'):
                        if self.STICKY and len(stale_games):
                            if self.LOG_LEVEL>1: print "Unstickying stale threads..."
                            try:
                                for stale_k,stale_game in stale_games.items():
                                    if stale_game.get('offsub'):
                                        stale_game.get('offsub').mod.sticky(state=False)
                                    if stale_game.get('presub'):
                                        stale_game.get('presub').mod.sticky(state=False)
                                    if stale_game.get('gamesub'):
                                        stale_game.get('gamesub').mod.sticky(state=False)
                                    if stale_game.get('postsub'):
                                        stale_game.get('postsub').mod.sticky(state=False)
                            except Exception, err:
                                if self.LOG_LEVEL>1: print "Unsticky of stale posts failed, continuing."
                            stale_games = {}

                        if self.LOG_LEVEL>1: print "Submitting offday thread..."
                        offday.update({'offsub' : subreddit.submit(offday.get('offtitle'), selftext=self.OFFDAY_THREAD_SETTINGS[2], send_replies=self.INBOXREPLIES)})
                        if self.LOG_LEVEL>1: print "Offday thread submitted..."

                        if self.STICKY:
                            if self.LOG_LEVEL>1: print "Stickying submission..."
                            offday.get('offsub').mod.sticky()
                            if self.LOG_LEVEL>1: print "Submission stickied..."

                        if self.FLAIR_MODE == 'submitter':
                            if self.LOG_LEVEL>1: print "Adding flair to submission as submitter..."
                            choices = offday.get('offsub').flair.choices()
                            flairsuccess = False
                            for p in choices:
                                if p['flair_text'] == self.OFFDAY_THREAD_SETTINGS[3]:
                                    offday.get('offsub').flair.select(p['flair_template_id'])
                                    flairsuccess = True
                            if flairsuccess:
                                if self.LOG_LEVEL>1: print "Submission flaired..."
                            else: 
                                if self.LOG_LEVEL>1: print "Flair not set: could not find flair in available choices"
                        elif self.FLAIR_MODE == 'mod':
                            if self.LOG_LEVEL>1: print "Adding flair to submission as mod..."
                            offday.get('offsub').mod.flair(self.OFFDAY_THREAD_SETTINGS[3])
                            if self.LOG_LEVEL>1: print "Submission flaired..."

                        if self.SUGGESTED_SORT != "":
                            if self.LOG_LEVEL>1: print "Setting suggested sort to " + self.SUGGESTED_SORT + "..."
                            offday.get('offsub').mod.suggested_sort(self.SUGGESTED_SORT)
                            if self.LOG_LEVEL>1: print "Suggested sort set..."

                        if self.LOG_LEVEL>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p")
                except Exception, err:
                    if self.LOG_LEVEL>0: print "Error posting off day thread:",err
            elif not self.OFFDAY_THREAD and len(games) == 0:
                if self.LOG_LEVEL>1: print "Off day detected, but off day thread disabled."

            if self.PREGAME_THREAD and len(games) > 0:
                timechecker.pregamecheck(self.PRE_THREAD_SETTINGS[1])
                for k,game in games.items():
                    if self.LOG_LEVEL>1: print "Preparing to post pregame thread for Game",k,"..."
                    game.update({'pretitle': edit.generate_title(game.get('url'),"pre",self.WINLOSS_POST_THREAD_TAGS,self.TEAM_CODE,game.get('doubleheader'),game.get('gamenum'),self.CONSOLIDATE_PRE)})
                    while True:
                        try:
                            subreddit = r.subreddit(self.SUBREDDIT)
                            if self.STICKY and len(stale_games):
                                if self.LOG_LEVEL>1: print "Unstickying stale threads..."
                                try:
                                    for stale_k,stale_game in stale_games.items():
                                        if stale_game.get('offsub'):
                                            stale_game.get('offsub').mod.sticky(state=False)
                                        if stale_game.get('presub'):
                                            stale_game.get('presub').mod.sticky(state=False)
                                        if stale_game.get('gamesub'):
                                            stale_game.get('gamesub').mod.sticky(state=False)
                                        if stale_game.get('postsub'):
                                            stale_game.get('postsub').mod.sticky(state=False)
                                except Exception, err:
                                    if self.LOG_LEVEL>1: print "Unsticky of stale posts failed, continuing."
                                stale_games = {}
                            if self.CONSOLIDATE_PRE and game.get('doubleheader'):
                                for otherk,othergame in games.items():
                                    if othergame.get('url')[:-2] == game.get('url')[:-2] and othergame.get('url') != game.get('url'): break
                                if not othergame.get('doubleheader'): othergame = {}
                                if game.get('presub'):
                                    if self.LOG_LEVEL>1: print "Consolidated pregame thread already posted and linked to this game..."
                                    break
                                if not game.get('presub') and othergame.get('presub'):
                                    if self.LOG_LEVEL>1: print "Linking this game to existing consolidated pregame thread from doubleheader game",otherk,"..."
                                    game.update({'presub' : othergame.get('presub')})
                                    break
                            for submission in subreddit.new():
                                if submission.title == game.get('pretitle'):
                                    if game.get('doubleheader') and self.CONSOLIDATE_PRE:
                                        if self.LOG_LEVEL>1: print "Game",k,"consolidated doubleheader pregame thread already posted, submitting edits..."
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_pre_code(game.get('url'),othergame.get('url')))
                                        if self.LOG_LEVEL>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Edits submitted. Sleeping for 5 seconds..."
                                        game.update({'presub' : submission})
                                    else:
                                        if self.LOG_LEVEL>1: print "Game",k,"pregame thread already posted, submitting edits..."
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_pre_code(game.get('url')))
                                        if self.LOG_LEVEL>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Edits submitted. Sleeping for 5 seconds..."
                                    time.sleep(5)
                                    break
                            if not game.get('presub'):
                                if self.LOG_LEVEL>1: print "Submitting pregame thread for Game",k,"..."
                                game.update({'presub' : subreddit.submit(game.get('pretitle'), selftext=edit.generate_pre_code(game.get('url'),othergame.get('url')), send_replies=self.INBOXREPLIES)})
                                if self.LOG_LEVEL>1: print "Pregame thread submitted..."
                                if self.STICKY:
                                    if self.LOG_LEVEL>1: print "Stickying submission..."
                                    game.get('presub').mod.sticky()
                                    if self.LOG_LEVEL>1: print "Submission stickied..."

                                if self.FLAIR_MODE == 'submitter':
                                    if self.LOG_LEVEL>1: print "Adding flair to submission as submitter..."
                                    choices = game.get('presub').flair.choices()
                                    flairsuccess = False
                                    for p in choices:
                                        if p['flair_text'] == self.PRE_THREAD_SETTINGS[2]:
                                            game.get('presub').flair.select(p['flair_template_id'])
                                            flairsuccess = True
                                    if flairsuccess:
                                        if self.LOG_LEVEL>1: print "Submission flaired..."
                                    else:
                                        if self.LOG_LEVEL>1: print "Flair not set: could not find flair in available choices"
                                elif self.FLAIR_MODE == 'mod':
                                    if self.LOG_LEVEL>1: print "Adding flair to submission as mod..."
                                    game.get('presub').mod.flair(self.PRE_THREAD_SETTINGS[2])
                                    if self.LOG_LEVEL>1: print "Submission flaired..."

                                if self.SUGGESTED_SORT != "":
                                    if self.LOG_LEVEL>1: print "Setting suggested sort to " + self.SUGGESTED_SORT + "..."
                                    game.get('presub').mod.suggested_sort(self.SUGGESTED_SORT)
                                    if self.LOG_LEVEL>1: print "Suggested sort set..."

                                if self.LOG_LEVEL>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                time.sleep(5)

                            if self.CONSOLIDATE_PRE and game.get('doubleheader'):
                                if othergame.get('doubleheader'):
                                    if self.LOG_LEVEL>1: print "Linking pregame submission to doubleheader Game",otherk,"..."
                                    othergame.update({'presub' : game.get('presub')})

                            break
                        except Exception, err:
                            if self.LOG_LEVEL>0: print err, ": retrying after 30 seconds..."
                            time.sleep(30)
                if self.LOG_LEVEL>2: print "Finished posting pregame threads..."
                if self.LOG_LEVEL>3: print "games:",games
            elif not self.PREGAME_THREAD and len(games):
                if self.LOG_LEVEL>2: print "Pregame thread disabled..."

            if self.LOG_LEVEL>2: print "Generating game thread titles for all games..."
            for k,game in games.items():
                game.update({'gametitle': edit.generate_title(game.get('url'),'game',self.WINLOSS_POST_THREAD_TAGS,self.TEAM_CODE,game.get('doubleheader'),game.get('gamenum'))})

            while True:
                for k,game in games.items():
                    if self.LOG_LEVEL>1 and len(games)>1: print "Game",k,"check"
                    for otherk,othergame in games.items():
                        if othergame.get('url')[:-2] == game.get('url')[:-2] and othergame.get('url') != game.get('url'): break
                    if not othergame.get('doubleheader'): othergame = {}
                    if othergame.get('doubleheader') and othergame.get('final') and not game.get('gamesub'):
                        if self.LOG_LEVEL>2: print "Updating title for doubleheader Game",k,"since Game",otherk,"is final..."
                        game.update({'gametitle': edit.generate_title(game.get('url'),'game',self.WINLOSS_POST_THREAD_TAGS,self.TEAM_CODE,game.get('doubleheader'),game.get('gamenum'))})
                    game.update({'status' : edit.get_status(game.get('url'))})
                    if timechecker.gamecheck(game.get('url'),game,othergame,activegames+pendinggames) == True:
                        if not timechecker.ppcheck(game.get('url')) and not game.get('final'):
                            check = datetime.today()
                            try:
                                subreddit = r.subreddit(self.SUBREDDIT)
                                if self.STICKY:
                                    if len(stale_games):
                                        if self.LOG_LEVEL>1: print "Unstickying stale threads..."
                                        try:
                                            for stale_k,stale_game in stale_games.items():
                                                if stale_game.get('offsub'):
                                                    stale_game.get('offsub').mod.sticky(state=False)
                                                if stale_game.get('presub'):
                                                    stale_game.get('presub').mod.sticky(state=False)
                                                if stale_game.get('gamesub'):
                                                    stale_game.get('gamesub').mod.sticky(state=False)
                                                if stale_game.get('postsub'):
                                                    stale_game.get('postsub').mod.sticky(state=False)
                                        except Exception, err:
                                            if self.LOG_LEVEL>1: print "Unsticky of stale posts failed, continuing."
                                        stale_games = {}
                                    if game.get('presub') and not game.get('gamesub'):
                                        if self.LOG_LEVEL>1: print "Unstickying Game",k,"pregame thread..."
                                        game.get('presub').mod.sticky(state=False)
                                if not game.get('gamesub'):
                                    for submission in subreddit.new():
                                        if submission.title == game.get('gametitle'):
                                            if self.LOG_LEVEL>1: print "Game",k,"thread already posted, getting submission..."
                                            game.update({'gamesub' : submission, 'status' : edit.get_status(game.get('url'))})
                                            threads[k].update({'game' : submission.selftext})
                                            break
                                if not game.get('gamesub'):
                                    if self.LOG_LEVEL>1: print "Submitting game thread for Game",k,"..."
                                    threads[k].update({'game' : edit.generate_code(game.get('url'),"game")})
                                    game.update({'gamesub' : subreddit.submit(game.get('gametitle'), selftext=threads[k].get('game'), send_replies=self.INBOXREPLIES), 'status' : edit.get_status(game.get('url'))})
                                    if self.LOG_LEVEL>1: print "Game thread submitted..."

                                    if self.STICKY:
                                        if self.LOG_LEVEL>1: print "Stickying submission..."
                                        game.get('gamesub').mod.sticky()
                                        if self.LOG_LEVEL>1: print "Submission stickied..."

                                    if self.SUGGESTED_SORT != "":
                                        if self.LOG_LEVEL>1: print "Setting suggested sort to " + self.SUGGESTED_SORT + "..."
                                        game.get('gamesub').mod.suggested_sort(self.SUGGESTED_SORT)
                                        if self.LOG_LEVEL>1: print "Suggested sort set..."

                                    if self.MESSAGE:
                                        if self.LOG_LEVEL>1: print "Messaging Baseballbot..."
                                        r.redditor('baseballbot').message('Gamethread posted', game.get('gamesub').shortlink)
                                        if self.LOG_LEVEL>1: print "Baseballbot messaged..."

                                    if self.FLAIR_MODE == 'submitter':
                                        if self.LOG_LEVEL>1: print "Adding flair to submission as submitter..."
                                        choices = game.get('gamesub').flair.choices()
                                        flairsuccess = False
                                        for p in choices:
                                            if p['flair_text'] == self.THREAD_SETTINGS[1]:
                                                game.get('gamesub').flair.select(p['flair_template_id'])
                                                flairsuccess = True
                                        if flairsuccess:
                                            if self.LOG_LEVEL>1: print "Submission flaired..."
                                        else:
                                            if self.LOG_LEVEL>1: print "Flair not set: could not find flair in available choices"
                                    elif self.FLAIR_MODE == 'mod':
                                        if self.LOG_LEVEL>1: print "Adding flair to submission as mod..."
                                        game.get('gamesub').mod.flair(self.THREAD_SETTINGS[1])
                                        if self.LOG_LEVEL>1: print "Submission flaired..."

                                    skipflag=True
                                    if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                    time.sleep(5)

                            except Exception, err:
                                if self.LOG_LEVEL>0: print "Error while getting/posting game thread: ",err, ": continuing after 10 seconds..."
                                time.sleep(10)

                            check = datetime.today()
                            str = edit.generate_code(game.get('url'),"game")
                            if skipflag: skipflag=False
                            else:
                                if str != threads[k].get('game'):
                                    threads[k].update({'game' : str})
                                    if self.LOG_LEVEL>2: print "Editing thread for Game",k,"..."
                                    while True:
                                        try:
                                            game.get('gamesub').edit(str)
                                            if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"edits submitted. Sleeping for 5 seconds..."
                                            time.sleep(5)
                                            break
                                        except Exception, err:
                                            if self.LOG_LEVEL>0: print datetime.strftime(check, "%d %I:%M:%S %p"),"Couldn't submit edits, retrying in 10 seconds..."
                                            time.sleep(10)
                                else:
                                    if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"No changes to Game",k,"thread. Sleeping for 5 seconds..."
                                    time.sleep(5)

                            if "##COMPLETED EARLY" in str:
                                check = datetime.today()
                                if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Completed Early..."
                                game.update({'final' : True})
                            elif "##FINAL: TIE" in str:
                                check = datetime.today()
                                if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Final (Tie)..."
                                game.update({'final' : True})
                            elif "##POSTPONED" in str:
                                check = datetime.today()
                                if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Postponed..."
                                game.update({'final' : True})
                            elif "##SUSPENDED" in str:
                                check = datetime.today()
                                if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Suspended..."
                                game.update({'final' : True})
                            elif "##CANCELLED" in str:
                                check = datetime.today()
                                if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Cancelled..."
                                game.update({'final' : True})
                            elif "|Decisions|" in str:
                                check = datetime.today()
                                if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Final..."
                                game.update({'final' : True})

                            if game.get('final'):
                                if self.POST_GAME_THREAD:
                                    try:
                                        game.update({'posttitle' : edit.generate_title(game.get('url'),"post",self.WINLOSS_POST_THREAD_TAGS,self.TEAM_CODE,game.get('doubleheader'),game.get('gamenum'))})
                                        subreddit = r.subreddit(self.SUBREDDIT)
                                        if self.STICKY:
                                            if game.get('presub'):
                                                if self.LOG_LEVEL>1: print "Unstickying Game",k,"pregame thread..."
                                                game.get('presub').mod.sticky(state=False)
                                            if game.get('gamesub'):
                                                if self.LOG_LEVEL>1: print "Unstickying Game",k,"game thread..."
                                                game.get('gamesub').mod.sticky(state=False)
                                        if not game.get('postsub'):
                                            for submission in subreddit.new():
                                                if submission.title == game.get('posttitle'):
                                                    if self.LOG_LEVEL>1: print "Game",k,"postgame thread already posted, getting submission..."
                                                    game.update({'postsub' : submission})
                                                    break
                                        if not game.get('postsub'):
                                            if self.LOG_LEVEL>1: print "Submitting postgame thread for Game",k,"..."
                                            game.update({'postsub' : subreddit.submit(game.get('posttitle'), selftext=edit.generate_code(game.get('url'),"post"), send_replies=self.INBOXREPLIES)})
                                            if self.LOG_LEVEL>1: print "Postgame thread submitted..."

                                            if self.STICKY:
                                                if self.LOG_LEVEL>1: print "Stickying submission..."
                                                game.get('postsub').mod.sticky()
                                                if self.LOG_LEVEL>1: print "Submission stickied..."

                                            if self.FLAIR_MODE == 'submitter':
                                                if self.LOG_LEVEL>1: print "Adding flair to submission as submitter..."
                                                choices = game.get('postsub').flair.choices()
                                                flairsuccess = False
                                                for p in choices:
                                                    if p['flair_text'] == self.POST_THREAD_SETTINGS[1]:
                                                        game.get('postsub').flair.select(p['flair_template_id'])
                                                        flairsuccess = True
                                                if flairsuccess:
                                                    if self.LOG_LEVEL>1: print "Submission flaired..."
                                                else:
                                                    if self.LOG_LEVEL>1: print "Flair not set: could not find flair in available choices"
                                            elif self.FLAIR_MODE == 'mod':
                                                if self.LOG_LEVEL>1: print "Adding flair to submission as mod..."
                                                game.get('postsub').mod.flair(self.POST_THREAD_SETTINGS[1])
                                                if self.LOG_LEVEL>1: print "Submission flaired..."

                                            if self.SUGGESTED_SORT != "":
                                                if self.LOG_LEVEL>1: print "Setting suggested sort to " + self.SUGGESTED_SORT + "..."
                                                game.get('postsub').mod.suggested_sort(self.SUGGESTED_SORT)
                                                if self.LOG_LEVEL>1: print "Suggested sort set..."

                                            if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                            time.sleep(5)
                                    except Exception, err:
                                        if self.LOG_LEVEL>0: print "Error while posting postgame thread:",err, ": continuing after 15 seconds..."
                                        time.sleep(15)
                        else: 
                            if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"final or postponed, nothing to do... "
                check = datetime.today()
                activegames=0
                pendinggames=0
                previewgames=0
                completedgames=0
                for  sk,sgame in games.items():
                    if sgame.get('gamesub') and not sgame.get('final'):
                        activegames += 1
                        if sgame.get('status') in ['Preview','Pre-Game']:
                            previewgames += 1
                    if not sgame.get('gamesub'):
                        pendinggames += 1
                    if sgame.get('postsub') and sgame.get('final'):
                        completedgames += 1

                if self.LOG_LEVEL>3: print "threads:",threads
                if len(offday):
                    if self.LOG_LEVEL>3: print "offday:",offday
                if self.LOG_LEVEL>3: print "games:",games
                limits = r.auth.limits
                if limits.get('used') > maxapi: maxapi = limits.get('used')
                if self.LOG_LEVEL>2: print "Reddit API Calls:",limits,"- Max usage today:",maxapi
                if self.LOG_LEVEL>2: print "Active Games:",activegames,"...in Preview/Pre-Game Status:",previewgames,"- Pending Games:",pendinggames,"- Completed Games:",completedgames

                if activegames == 0 and pendinggames == 0:
                    if self.LOG_LEVEL>1: print "All games final for today (or off day), going into end of day loop... "
                    break
                elif pendinggames > 0 and activegames == 0:
                    if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"No game threads to post yet, sleeping for 10 minutes... "
                    time.sleep(600)
                elif activegames > 0 and previewgames == activegames:
                    if self.LOG_LEVEL>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"All posted games are in Preview/Pre-Game status, sleeping for 5 minutes... "
                    time.sleep(300)
                elif limits.get('remaining') < 60:
                    if self.LOG_LEVEL>0: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Approaching Reddit API rate limit. Taking a 10 second break..."
                    time.sleep(10)
            if datetime.today().day == today.day:
                timechecker.endofdaycheck()

if __name__ == '__main__':
    program = Bot()
    program.run()
