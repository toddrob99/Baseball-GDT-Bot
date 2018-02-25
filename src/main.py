#!/usr/bin/env python

'''

BASEBALL GAME THREAD BOT FOR REDDIT
https://github.com/toddrob99/Baseball-GDT-Bot

Maintained by:
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
        self.VERSION = '5.0.3'
        self.SETTINGS = {}

    def read_settings(self):
        import os
        cwd = os.path.dirname(os.path.realpath(__file__))
        fatal_errors = []
        warnings = []
        with open(cwd + '/settings.json') as data:
            self.SETTINGS = json.load(data)

            if self.SETTINGS.get('CLIENT_ID') == None: 
                fatal_errors.append('Missing CLIENT_ID')

            if self.SETTINGS.get('CLIENT_SECRET') == None:
                fatal_errors.append('Missing CLIENT_SECRET')

            if self.SETTINGS.get('REFRESH_TOKEN') == None:
                fatal_errors.append('Missing REFRESH_TOKEN')

            if self.SETTINGS.get('USER_AGENT') == None:
                warnings.append('Missing USER_AGENT, using default ("")...')
                self.SETTINGS.update({'USER_AGENT' : ''})
            self.SETTINGS.update({'FULL_USER_AGENT' : "OAuth Baseball Game Thread Bot for Reddit v" + self.VERSION + " https://github.com/toddrob99/Baseball-GDT-Bot " + self.SETTINGS.get('USER_AGENT')})

            if self.SETTINGS.get('SUBREDDIT') == None:
                fatal_errors.append('Missing SUBREDDIT')

            if self.SETTINGS.get('TEAM_CODE') == None:
                fatal_errors.append('Missing TEAM_CODE')

            if self.SETTINGS.get('BOT_TIME_ZONE') == None:
                warnings.append('Missing BOT_TIME_ZONE, using default (ET)...')
                self.SETTINGS.update({'BOT_TIME_ZONE' : 'ET'})

            if self.SETTINGS.get('TEAM_TIME_ZONE') == None:
                warnings.append('Missing TEAM_TIME_ZONE, using default (ET)...')
                self.SETTINGS.update({'TEAM_TIME_ZONE' : 'ET'})

            if self.SETTINGS.get('STICKY') == None:
                warnings.append('Missing STICKY, using default (true - make sure your bot user has mod rights)...')
                self.SETTINGS.update({'STICKY' : True})

            if self.SETTINGS.get('FLAIR_MODE') not in ['', 'none', 'submitter', 'mod']:
                warnings.append('Missing or invalid FLAIR_MODE, using default ("none")...')
                self.SETTINGS.update({'FLAIR_MODE' : 'none'})

            if self.SETTINGS.get('SERIES_IN_TITLES') == None:
                warnings.append('Missing SERIES_IN_TITLES, using default (true)...')
                self.SETTINGS.update({'SERIES_IN_TITLES' : True})

            if self.SETTINGS.get('LOG_LEVEL') == None:
                warnings.append('Missing LOG_LEVEL, using default (2)...')
                self.SETTINGS.update({'LOG_LEVEL' : 2})

            if self.SETTINGS.get('OFF_THREAD') == None:
                warnings.append('Missing OFF_THREAD, using defaults (ENABLED: true, TAG: "OFF DAY THREAD:", TIME: 9AM, FOOTER: "No game today. Feel free to discuss whatever you want in this thread.", SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", SUPPRESS_OFFSEASON: true)...')
                self.SETTINGS.update({'OFF_THREAD' : {'ENABLED' : True,'TAG' : 'OFF DAY THREAD:','TIME' : '9AM', 'FOOTER' : 'No game today. Feel free to discuss whatever you want in this thread.', 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'SUPPRESS_OFFSEASON' : True}})

            if self.SETTINGS.get('OFF_THREAD').get('ENABLED') == None:
                warnings.append('Missing OFF_THREAD : ENABLED, using default (true)...')
                self.SETTINGS['OFF_THREAD'].update({'ENABLED' : True})

            if self.SETTINGS.get('OFF_THREAD').get('TAG') == None:
                warnings.append('Missing OFF_THREAD : TAG, using default ("OFF DAY THREAD:")...')
                self.SETTINGS['OFF_THREAD'].update({'TAG' : 'OFF DAY THREAD:'})

            if self.SETTINGS.get('OFF_THREAD').get('TIME') == None:
                warnings.append('Missing OFF_THREAD : TIME, using default ("9AM")...')
                self.SETTINGS['OFF_THREAD'].update({'TIME' : '9AM'})

            if self.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT') == None:
                warnings.append('Missing OFF_THREAD : SUGGESTED_SORT, using default ("new" - make sure your bot user has mod rights)...')
                self.SETTINGS['OFF_THREAD'].update({'SUGGESTED_SORT' : 'new'})

            if self.SETTINGS.get('OFF_THREAD').get('INBOX_REPLIES') == None:
                warnings.append('Missing OFF_THREAD : INBOX_REPLIES, using default (false)...')
                self.SETTINGS['OFF_THREAD'].update({'INBOX_REPLIES' : False})

            if self.SETTINGS.get('OFF_THREAD').get('FLAIR') == None:
                warnings.append('Missing OFF_THREAD : FLAIR, using default ("")...')
                self.SETTINGS['OFF_THREAD'].update({'FLAIR' : ''})

            if self.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON') == None:
                warnings.append('Missing OFF_THREAD : SUPPRESS_OFFSEASON, using default (true)...')
                self.SETTINGS['OFF_THREAD'].update({'SUPPRESS_OFFSEASON' : True})

            if self.SETTINGS.get('OFF_THREAD').get('FOOTER') == None:
                warnings.append('Missing OFF_THREAD : FOOTER, using default ("No game today. Feel free to discuss whatever you want in this thread.")...')
                self.SETTINGS['OFF_THREAD'].update({'FOOTER' : 'No game today. Feel free to discuss whatever you want in this thread.'})

            if self.SETTINGS.get('PRE_THREAD') == None:
                warnings.append('Missing PRE_THREAD, using defaults (TAG: "PREGAME THREAD:", TIME: 9AM, SUPPRESS_MINUTES: 0, SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", PROBABLES: true, FIRST_PITCH: true, DESCRIPTION: true, BLURB: true)...')
                self.SETTINGS.update({'PRE_THREAD' : {'TAG' : 'PREGAME THREAD:', 'TIME' : '9AM', 'SUPPRESS_MINUTES' : 0, 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'CONTENT' : {'PROBABLES' : True, 'FIRST_PITCH' : True, 'DESCRIPTION' : True, 'BLURB' : True}}})

            if self.SETTINGS.get('PRE_THREAD').get('ENABLED') == None:
                warnings.append('Missing PRE_THREAD : ENABLED, using default (true)...')
                self.SETTINGS['PRE_THREAD'].update({'ENABLED' : True})

            if self.SETTINGS.get('PRE_THREAD').get('TAG') == None:
                warnings.append('Missing PRE_THREAD : TAG, using default ("PREGAME THREAD")...')
                self.SETTINGS['PRE_THREAD'].update({'TAG' : 'PREGAME THREAD'})

            if self.SETTINGS.get('PRE_THREAD').get('TIME') == None:
                warnings.append('Missing PRE_THREAD : TIME, using default ("9AM")...')
                self.SETTINGS['PRE_THREAD'].update({'TIME' : '9AM'})

            if self.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES') == None:
                warnings.append('Missing PRE_THREAD : SUPPRESS_MINUTES, using default (0)...')
                self.SETTINGS['PRE_THREAD'].update({'SUPPRESS_MINUTES' : 0})

            if self.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT') == None:
                warnings.append('Missing PRE_THREAD : SUGGESTED_SORT, using default ("new" - make sure your bot user has mod rights)...')
                self.SETTINGS['PRE_THREAD'].update({'SUGGESTED_SORT' : 'new'})

            if self.SETTINGS.get('PRE_THREAD').get('INBOX_REPLIES') == None:
                warnings.append('Missing PRE_THREAD : INBOX_REPLIES, using default (false)...')
                self.SETTINGS['PRE_THREAD'].update({'INBOX_REPLIES' : False})

            if self.SETTINGS.get('PRE_THREAD').get('FLAIR') == None:
                warnings.append('Missing PRE_THREAD : FLAIR, using default ("")...')
                self.SETTINGS['PRE_THREAD'].update({'FLAIR' : ''})

            if self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') == None:
                warnings.append('Missing PRE_THREAD : CONSOLIDATE_DH, using default (true)...')
                self.SETTINGS['PRE_THREAD'].update({'CONSOLIDATE_DH' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT') == None:
                warnings.append('Missing PRE_THREAD : CONTENT, using defaults (BLURB: true, PROBABLES: true, BROADCAST: true, FIRST_PITCH: true, DESCRIPTION: true)...')
                self.SETTINGS['PRE_THREAD'].update({'CONTENT' : {'BLURB' : True, 'PROBABLES' : True, 'BROADCAST' : True, 'FIRST_PITCH' : True, 'DESCRIPTION' : True}})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BLURB') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : BLURB, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'BLURB' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('PROBABLES') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : PROBABLES, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'PROBABLES' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BROADCAST') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : BROADCAST, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'BROADCAST' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('FIRST_PITCH') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : FIRST_PITCH, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'FIRST_PITCH' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('DESCRIPTION') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : DESCRIPTION, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'DESCRIPTION' : True})

            if self.SETTINGS.get('GAME_THREAD') == None:
                warnings.append('Missing GAME_THREAD, using defaults (TAG: "GAME THREAD:", HOURS_BEFORE: 3, SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", MESSAGE: false, HOLD_DH_GAME2_THREAD: true, EXTRA_SLEEP: 0, HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, CURRENT_STATE: true, FOOTER: "**Remember to sort by new to keep up!**", UPDATE_STAMP: true, THEATER_LINK: false, PREVIEW_BLURB: true, PREVIEW_PROBABLES: true, NEXT_GAME: true)...')
                self.SETTINGS.update({'GAME_THREAD' : {'TAG' : 'GAME THREAD:', 'HOURS_BEFORE' : 3, 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'MESSAGE' : False, 'HOLD_DH_GAME2_THREAD' : True, 'EXTRA_SLEEP' : 0, 'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'CURRENT_STATE' : True, 'FOOTER' : '**Remember to sort by new to keep up!**', 'UPDATE_STAMP' : True, 'THEATER_LINK' : False, 'PREVIEW_BLURB' : True, 'PREVIEW_PROBABLES' : True, 'NEXT_GAME' : True}}})

            if self.SETTINGS.get('GAME_THREAD').get('TAG') == None:
                warnings.append('Missing GAME_THREAD : TAG, using default ("GAME THREAD:")...')
                self.SETTINGS['GAME_THREAD'].update({'TAG' : 'GAME THREAD:'})

            if self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE') == None:
                warnings.append('Missing HOURS_BEFORE, using default (3)...')
                self.SETTINGS['GAME_THREAD'].update({'HOURS_BEFORE' : 3})

            if self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT') == None:
                warnings.append('Missing GAME_THREAD : SUGGESTED_SORT, using default ("new" - make sure your bot user has mod rights)...')
                self.SETTINGS['GAME_THREAD'].update({'SUGGESTED_SORT' : 'new'})

            if self.SETTINGS.get('GAME_THREAD').get('INBOX_REPLIES') == None:
                warnings.append('Missing GAME_THREAD : INBOX_REPLIES, using default (false)...')
                self.SETTINGS['GAME_THREAD'].update({'INBOX_REPLIES' : False})

            if self.SETTINGS.get('GAME_THREAD').get('FLAIR') == None:
                warnings.append('Missing GAME_THREAD : FLAIR, using default ("")...')
                self.SETTINGS['GAME_THREAD'].update({'FLAIR' : ''})

            if self.SETTINGS.get('GAME_THREAD').get('MESSAGE') == None:
                warnings.append('Missing GAME_THREAD : MESSAGE, using default (false)...')
                self.SETTINGS['GAME_THREAD'].update({'MESSAGE' : False})

            if self.SETTINGS.get('GAME_THREAD').get('HOLD_DH_GAME2_THREAD') == None:
                warnings.append('Missing GAME_THREAD : HOLD_DH_GAME2_THREAD, using default (true)...')
                self.SETTINGS['GAME_THREAD'].update({'HOLD_DH_GAME2_THREAD' : True})

            if self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP') == None or not isinstance(self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP'),(int,long)) or self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP') < 0:
                warnings.append('Missing or invalid GAME_THREAD : EXTRA_SLEEP, using default (0)...')
                self.SETTINGS['GAME_THREAD'].update({'EXTRA_SLEEP' : 0})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT') == None:
                warnings.append('Missing GAME_THREAD : CONTENT, using defaults (HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "**Remember to sort by new to keep up!**", THEATER_LINK: false, PREVIEW_BLURB: true, PREVIEW_PROBABLES: true)...')
                self.SETTINGS['GAME_THREAD'].update({'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'FOOTER' : '**Remember to sort by new to keep up!**', 'THEATER_LINK' : False, 'PREVIEW_BLURB' : True, 'PREVIEW_PROBABLES' : True}})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('HEADER') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : HEADER, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'HEADER' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('BOX_SCORE') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : BOX_SCORE, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'BOX_SCORE' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('LINE_SCORE') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : LINE_SCORE, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'LINE_SCORE' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('SCORING_PLAYS') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : SCORING_PLAYS, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'SCORING_PLAYS' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('HIGHLIGHTS') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : HIGHLIGHTS, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'HIGHLIGHTS' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('CURRENT_STATE') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : CURRENT_STATE, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'CURRENT_STATE' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('FOOTER') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : FOOTER, using default ("**Remember to sort by new to keep up!**")...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'FOOTER' : "**Remember to sort by new to keep up!**"})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : UPDATE_STAMP, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'UPDATE_STAMP' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('THEATER_LINK') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : THEATER_LINK, using default (false)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'THEATER_LINK' : False})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('PREVIEW_BLURB') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : PREVIEW_BLURB, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'PREVIEW_BLURB' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('PREVIEW_PROBABLES') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : PREVIEW_PROBABLES, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'PREVIEW_PROBABLES' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('NEXT_GAME') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : NEXT_GAME, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'NEXT_GAME' : True})

            if self.SETTINGS.get('POST_THREAD') == None:
                warnings.append('Missing POST_THREAD, using defaults (WIN_TAG: "OUR TEAM WON:", LOSS_TAG: "OUR TEAM LOST:", OTHER_TAG: "POST GAME THREAD:",  SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "", THEATER_LINK: true, NEXT_GAME: true)...')
                self.SETTINGS.update({'POST_THREAD' : {'WIN_TAG' : 'OUR TEAM WON:', 'LOSS_TAG' : 'OUR TEAM LOST:', 'OTHER_TAG' : 'POST GAME THREAD:', 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'FOOTER' : '', 'THEATER_LINK' : True, 'NEXT_GAME' : True}}})

            if self.SETTINGS.get('POST_THREAD').get('ENABLED') == None:
                warnings.append('Missing POST_THREAD : ENABLED, using default (true)...')
                self.SETTINGS['POST_THREAD'].update({'ENABLED' : True})

            if self.SETTINGS.get('POST_THREAD').get('WIN_TAG') == None:
                warnings.append('Missing POST_THREAD : WIN_TAG, using default ("OUR TEAM WON:")...')
                self.SETTINGS['POST_THREAD'].update({'WIN_TAG' : 'OUR TEAM WON:'})

            if self.SETTINGS.get('POST_THREAD').get('LOSS_TAG') == None:
                warnings.append('Missing POST_THREAD : LOSS_TAG, using default ("OUR TEAM LOST:")...')
                self.SETTINGS['POST_THREAD'].update({'LOSS_TAG' : 'OUR TEAM LOST:'})

            if self.SETTINGS.get('POST_THREAD').get('OTHER_TAG') == None:
                warnings.append('Missing POST_THREAD : OTHER_TAG, using default ("POST GAME THREAD:")...')
                self.SETTINGS['POST_THREAD'].update({'OTHER_TAG' : 'POST GAME THREAD:'})

            if self.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT') == None:
                warnings.append('Missing POST_THREAD : SUGGESTED_SORT, using default ("new" - make sure your bot user has mod rights)...')
                self.SETTINGS['POST_THREAD'].update({'SUGGESTED_SORT' : 'new'})

            if self.SETTINGS.get('POST_THREAD').get('INBOX_REPLIES') == None:
                warnings.append('Missing POST_THREAD : INBOX_REPLIES, using default (false)...')
                self.SETTINGS['POST_THREAD'].update({'INBOX_REPLIES' : False})

            if self.SETTINGS.get('POST_THREAD').get('FLAIR') == None:
                warnings.append('Missing POST_THREAD : FLAIR, using default ("")...')
                self.SETTINGS['POST_THREAD'].update({'FLAIR' : ''})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT') == None:
                warnings.append('Missing POST_THREAD : CONTENT, using defaults (HEADER: true, BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "", THEATER_LINK: true)...')
                self.SETTINGS['POST_THREAD'].update({'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'FOOTER' : '', 'THEATER_LINK' : True}})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('HEADER') == None:
                warnings.append('Missing POST_THREAD : CONTENT : HEADER, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'HEADER' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('BOX_SCORE') == None:
                warnings.append('Missing POST_THREAD : CONTENT : BOX_SCORE, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'BOX_SCORE' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('LINE_SCORE') == None:
                warnings.append('Missing POST_THREAD : CONTENT : LINE_SCORE, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'LINE_SCORE' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('SCORING_PLAYS') == None:
                warnings.append('Missing POST_THREAD : CONTENT : SCORING_PLAYS, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'SCORING_PLAYS' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('HIGHLIGHTS') == None:
                warnings.append('Missing POST_THREAD : CONTENT : HIGHLIGHTS, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'HIGHLIGHTS' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('FOOTER') == None:
                warnings.append('Missing POST_THREAD : CONTENT : FOOTER, using default ("")...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'FOOTER' : ""})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('THEATER_LINK') == None:
                warnings.append('Missing POST_THREAD : CONTENT : THEATER_LINK, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'THEATER_LINK' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('NEXT_GAME') == None:
                warnings.append('Missing POST_THREAD : CONTENT : NEXT_GAME, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'NEXT_GAME' : True})

            if self.SETTINGS.get('LOG_LEVEL')>3: print "Settings:",self.SETTINGS

        return {'fatal' : fatal_errors, 'warnings' : warnings}

    def run(self):

        settings_results = self.read_settings()

        warnings = settings_results.get('warnings',[])
        fatal_errors = settings_results.get('fatal',[])

        if len(warnings):
            if self.SETTINGS.get('LOG_LEVEL')>1:
                for warn in warnings:
                    print "WARNING:",warn

        if len(fatal_errors):
            if self.SETTINGS.get('LOG_LEVEL')>0:
                for fatal_err in fatal_errors:
                    print "FATAL ERROR:",fatal_err
            return

        if self.SETTINGS.get('TEAM_TIME_ZONE') == 'ET':
            time_info = (self.SETTINGS.get('TEAM_TIME_ZONE'),0)
        elif self.SETTINGS.get('TEAM_TIME_ZONE') == 'CT':
            time_info = (self.SETTINGS.get('TEAM_TIME_ZONE'),1)
        elif self.SETTINGS.get('TEAM_TIME_ZONE') == 'MT':
            time_info = (self.SETTINGS.get('TEAM_TIME_ZONE'),2)
        elif self.SETTINGS.get('TEAM_TIME_ZONE') == 'PT':
            time_info = (self.SETTINGS.get('TEAM_TIME_ZONE'),3)
        else:
            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Invalid TEAM_TIME_ZONE. Must be ET, CT, MT, PT. Using default (ET)..."
            self.SETTINGS.update({'TEAM_TIME_ZONE' : 'ET'})
            time_info = (self.SETTINGS.get('TEAM_TIME_ZONE'),0)

        edit = editor.Editor(time_info, self.SETTINGS)

        if edit.lookup_team_info(field='team_code',lookupfield='team_code',lookupval=self.SETTINGS.get('TEAM_CODE')) != self.SETTINGS.get('TEAM_CODE'):
            if self.SETTINGS.get('LOG_LEVEL')>0: print "FATAL ERROR: Invalid team code detected:",self.SETTINGS.get('TEAM_CODE'),"- use lookup_team_code.py to look up the correct team code; see README.md"
            return

        if self.SETTINGS.get('BOT_TIME_ZONE') == 'ET':
            time_before = self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE') * 60 * 60
        elif self.SETTINGS.get('BOT_TIME_ZONE') == 'CT':
            time_before = (1 + self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE')) * 60 * 60
        elif self.SETTINGS.get('BOT_TIME_ZONE') == 'MT':
            time_before = (2 + self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE')) * 60 * 60
        elif self.SETTINGS.get('BOT_TIME_ZONE') == 'PT':
            time_before = (3 + self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE')) * 60 * 60
        else:
            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Invalid BOT_TIME_ZONE. Must be ET, CT, MT, PT. Using default (ET)..."
            self.SETTINGS.update({'BOT_TIME_ZONE' : 'ET'})
            time_before = self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE') * 60 * 60

        timechecker = timecheck.TimeCheck(time_before, self.SETTINGS.get('LOG_LEVEL'), self.SETTINGS.get('GAME_THREAD').get('HOLD_DH_GAME2_THREAD'))

        if self.SETTINGS.get('LOG_LEVEL')>2: print "Initiating PRAW instance with User Agent:",self.SETTINGS.get('FULL_USER_AGENT')
        r = praw.Reddit(client_id=self.SETTINGS.get('CLIENT_ID'),
                        client_secret=self.SETTINGS.get('CLIENT_SECRET'),
                        refresh_token=self.SETTINGS.get('REFRESH_TOKEN'),
                        user_agent=self.SETTINGS.get('FULL_USER_AGENT'))
        scopes = ['identity', 'submit', 'edit', 'read', 'modposts', 'privatemessages', 'flair', 'modflair']
        praw_scopes = r.auth.scopes()
        missing_scopes = []
        if self.SETTINGS.get('LOG_LEVEL')>2: print "Reddit authorized scopes:",praw_scopes
        if 'identity' in praw_scopes:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Reddit authorized user:",r.user.me()
        for scope in scopes:
            if scope not in praw_scopes:
                missing_scopes.append(scope)
        if len(missing_scopes):
            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING:",missing_scopes,"scope(s) not authorized. Please re-run setup-oauth.py to update scopes for your bot user. See instructions in README.md."

        games = {}
        offday = {}
        threads = {}
        offseason = False

        while True:
            if len(offday): stale_games[0] = offday
            else: stale_games = games
            if self.SETTINGS.get('STICKY') and len(stale_games)==0:
                try:
                    sticky1 = r.subreddit(self.SETTINGS.get('SUBREDDIT')).sticky(1)
                    if (sticky1.author == r.user.me() and not sticky1.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y")) and 
                                                        not sticky1.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y") + " - DOUBLEHEADER") and
                                                        not sticky1.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y") + " - GAME 1") and
                                                        not sticky1.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y") + " - GAME 2") and 
                                                        sticky1.title.startswith((self.SETTINGS.get('OFF_THREAD').get('TAG'), 
                                                                                    self.SETTINGS.get('PRE_THREAD').get('TAG'), 
                                                                                    self.SETTINGS.get('GAME_THREAD').get('TAG'), 
                                                                                    self.SETTINGS.get('POST_THREAD').get('WIN_TAG'), 
                                                                                    self.SETTINGS.get('POST_THREAD').get('LOSS_TAG'), 
                                                                                    self.SETTINGS.get('POST_THREAD').get('OTHER_TAG')))):
                        stale_games[len(stale_games)+1] = {'gamesub' : sticky1, 'gametitle' : sticky1.title}
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Found stale thread in top sticky slot..."
                    sticky2 = r.subreddit(self.SETTINGS.get('SUBREDDIT')).sticky(2)
                    if (sticky2.author == r.user.me() and not sticky2.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y")) and 
                                                        not sticky2.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y") + " - DOUBLEHEADER") and 
                                                        not sticky2.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y") + " - GAME 1") and 
                                                        not sticky2.title.endswith(datetime.strftime(datetime.today(),"%B %d, %Y") + " - GAME 2") and
                                                        sticky2.title.startswith((self.SETTINGS.get('OFF_THREAD').get('TAG'), 
                                                                                    self.SETTINGS.get('PRE_THREAD').get('TAG'), 
                                                                                    self.SETTINGS.get('GAME_THREAD').get('TAG'), 
                                                                                    self.SETTINGS.get('POST_THREAD').get('WIN_TAG'), 
                                                                                    self.SETTINGS.get('POST_THREAD').get('LOSS_TAG'), 
                                                                                    self.SETTINGS.get('POST_THREAD').get('OTHER_TAG')))):
                        stale_games[len(stale_games)+1] = {'gamesub' : sticky2, 'gametitle' : sticky2.title}
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Found stale thread in bottom sticky slot..."
                except:
                    pass
            if self.SETTINGS.get('LOG_LEVEL')>2: print "stale games:",stale_games

            today = datetime.today()
            #today = datetime.strptime('2018-02-22','%Y-%m-%d') # leave commented unless testing

            baseurl = "http://gd2.mlb.com/components/game/mlb/"
            todayurl = baseurl + "year_" + today.strftime("%Y") + "/month_" + today.strftime("%m") + "/day_" + today.strftime("%d") + "/"
            gridurl = todayurl + "grid.json"

            while True:
                try:
                    gridresponse = urllib2.urlopen(gridurl)
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"), "There are no games today."
                        todaygames = {}
                        break
                    else:
                        if self.SETTINGS.get('LOG_LEVEL')>0: print "Couldn't find URL, retrying in 30 seconds..."
                        time.sleep(30)
                else:
                    todaygames = json.load(gridresponse).get('data').get('games').get('game')
                    if todaygames == None:
                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"), "There are no games today."
                        todaygames = {}
                    break

            threads = {}
            offday = {}
            othergame = {}
            games = {}
            activegames = completedgames = previewgames = maxapi = 0
            skipflag = False
            i = 1
            if isinstance(todaygames,dict): todaygames = [todaygames]
            for todaygame in todaygames:
                if todaygame.get('home_code') == self.SETTINGS.get('TEAM_CODE') or todaygame.get('away_code') == self.SETTINGS.get('TEAM_CODE'):
                    games[i] = todaygame
                    games[i].pop('game_media',None) #remove some clutter
                    games[i].pop('newsroom',None) #remove some clutter
                    homeaway = None
                    if todaygame.get('home_code') == self.SETTINGS.get('TEAM_CODE'): homeaway = 'home'
                    if todaygame.get('away_code') == self.SETTINGS.get('TEAM_CODE'): homeaway = 'away'
                    if homeaway != None: games[i].update({'homeaway' : homeaway})
                    gid = 'gid_' + todaygame.get('id').replace('/','_').replace('-','_') + '/'
                    if gid == 'gid_/':
                        if homeaway == 'home' and todaygame.get('series') == 'Exhibition Game':
                            gid = 'gid_' + today.strftime("%Y_%m_%d_") + todaygame.get('away_code') + 'bbc_' + todaygame.get('home_code') + 'mlb_' + todaygame.get('game_nbr') + '/'
                        elif homeaway == 'away' and todaygame.get('series') == 'Exhibition Game':
                            gid = 'gid_' + today.strftime("%Y_%m_%d_") + todaygame.get('away_code') + 'mlb_' + todaygame.get('home_code') + 'bbc_' + todaygame.get('game_nbr') + '/'
                        else:
                            gid = 'gid_' + today.strftime("%Y_%m_%d_") + todaygame.get('away_code') + 'mlb_' + todaygame.get('home_code') + 'mlb_' + todaygame.get('game_nbr') + '/'
                    games[i].update({'url' : todayurl + gid, 'final' : False})
                    if todaygame.get('double_header_sw') != 'N':
                        games[i].update({'doubleheader' : True})
                        if todaygame.get('double_header_sw') == "S": dhtype = 'split'
                        if todaygame.get('double_header_sw') == "Y": dhtype = 'straight'
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Game " + str(i) + " detected as " + dhtype + " doubleheader game " + todaygame.get('game_nbr') + "..."
                    else: games[i].update({'doubleheader' : False})
                    threads[i] = {'game' : '', 'post' : '', 'pre' : ''}
                    i += 1
            if self.SETTINGS.get('LOG_LEVEL')>2: print "games:",games
            pendinggames = len(games)

            if len(games) == 0:
                next_game = edit.next_game(30)
                if next_game.get('days_away')==None:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "No games in the next 30 days. It's the off season..."
                    offseason = True
                elif next_game.get('days_away') > 14:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Next game is",next_game.get('days_away'),"days away. It's the off season..."
                    offseason = True
                elif next_game.get('days_away') <= 14:
                    last_game = edit.last_game(14)
                    if not last_game.get('days_ago'):
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Next game is",next_game.get('days_away'),"day(s) away, but no games in the last 14 days. It's the off season..."
                        offseason = True
                    else:
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "No games today..."
                        offseason = False
                else:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "No games today..."
                    offseason = False

            if self.SETTINGS.get('OFF_THREAD').get('ENABLED') and len(games) == 0 and not (offseason and self.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON')):
                timechecker.pregamecheck(self.SETTINGS.get('OFF_THREAD').get('TIME'))
                offday.update({'offtitle': self.SETTINGS.get('OFF_THREAD').get('TAG') + " " + datetime.strftime(datetime.today(), "%A, %B %d"), 'offmessage' : self.SETTINGS.get('OFF_THREAD').get('FOOTER')})
                if next_game.get('date'): 
                    next = edit.generate_next_game(next_game=next_game)
                    if len(self.SETTINGS.get('OFF_THREAD').get('FOOTER')): next += "\n\n"
                    offday.update({'offmessage' : next + self.SETTINGS.get('OFF_THREAD').get('FOOTER')})
                else: 
                    if len(self.SETTINGS.get('OFF_THREAD').get('FOOTER')) == 0:
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: No date found for next game, and off day footer text is blank. Using default footer text since post cannot be blank..."
                        offday.update({'offmessage' : "No game today. Feel free to discuss whatever you want in this thread."})
                    else: offday.update({'offmessage' : self.SETTINGS.get('OFF_THREAD').get('FOOTER')})
                try:
                    subreddit = r.subreddit(self.SETTINGS.get('SUBREDDIT'))
                    for submission in subreddit.new():
                        if submission.title == offday.get('offtitle'):
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Offday thread already posted, getting submission..."
                            offday.update({'offsub' : submission})
                            break

                    if not offday.get('offsub'):
                        if self.SETTINGS.get('STICKY') and len(stale_games):
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying stale threads..."
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
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of stale posts failed, continuing."
                            stale_games = {}

                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting offday thread..."
                        offday.update({'offsub' : subreddit.submit(offday.get('offtitle'), selftext=offday.get('offmessage'), send_replies=self.SETTINGS.get('OFF_THREAD').get('INBOX_REPLIES'))})
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Offday thread submitted..."

                        if self.SETTINGS.get('STICKY'):
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                            try:
                                offday.get('offsub').mod.sticky()
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                            except:
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of offday thread failed (check mod privileges), continuing."

                        if self.SETTINGS.get('FLAIR_MODE') == 'submitter':
                            if self.SETTINGS.get('OFF_THREAD').get('FLAIR') == "":
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = submitter, but OFF_THREAD : FLAIR is blank..."
                            else:
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as submitter..."
                                choices = offday.get('offsub').flair.choices()
                                flairsuccess = False
                                for p in choices:
                                    if p['flair_text'] == self.SETTINGS.get('OFF_THREAD').get('FLAIR'):
                                        offday.get('offsub').flair.select(p['flair_template_id'])
                                        flairsuccess = True
                                if flairsuccess:
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."
                                else: 
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Flair not set: could not find flair in available choices"
                        elif self.SETTINGS.get('FLAIR_MODE') == 'mod':
                            if self.SETTINGS.get('OFF_THREAD').get('FLAIR') == "":
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = mod, but OFF_THREAD : FLAIR is blank..."
                            else:
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as mod..."
                                offday.get('offsub').mod.flair(self.SETTINGS.get('OFF_THREAD').get('FLAIR'))
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."

                        if self.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT') != "":
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Setting suggested sort to " + self.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT') + "..."
                            try:
                                offday.get('offsub').mod.suggested_sort(self.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT'))
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Suggested sort set..."
                            except:
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on offday thread failed (check mod privileges), continuing."

                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p")
                except Exception, err:
                    if self.SETTINGS.get('LOG_LEVEL')>0: print "Error posting off day thread:",err
            elif not self.SETTINGS.get('OFF_THREAD').get('ENABLED') and len(games) == 0:
                if self.SETTINGS.get('LOG_LEVEL')>1: print "Off day detected, but off day thread disabled."
            elif offseason and self.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON') and len(games) == 0:
                if self.SETTINGS.get('LOG_LEVEL')>1: print "Suppressing off day thread during off season..."

            if self.SETTINGS.get('PRE_THREAD').get('ENABLED') and len(games) > 0:
                timechecker.pregamecheck(self.SETTINGS.get('PRE_THREAD').get('TIME'))
                for k,game in games.items():
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Preparing to post pregame thread for Game",k,"..."
                    game.update({'pretitle': edit.generate_title(game.get('url'),"pre",game.get('doubleheader'),game.get('game_nbr'))})
                    while True:
                        try:
                            subreddit = r.subreddit(self.SETTINGS.get('SUBREDDIT'))
                            if self.SETTINGS.get('STICKY') and len(stale_games):
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying stale threads..."
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
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of stale posts failed, continuing."
                                stale_games = {}
                            othergame = otherk = None
                            if self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and game.get('doubleheader'):
                                for otherk,othergame in games.items():
                                    if othergame.get('url')[:-2] == game.get('url')[:-2] and othergame.get('url') != game.get('url'): break
                                if not othergame.get('doubleheader'): othergame = {}
                                if game.get('presub'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Consolidated pregame thread already posted and linked to this game..."
                                    break
                                if not game.get('presub') and othergame.get('presub'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Linking this game to existing consolidated pregame thread from doubleheader game",otherk,"..."
                                    game.update({'presub' : othergame.get('presub')})
                                    break
                            gameinfo = edit.get_teams_time(game.get('url'))
                            original_pretitle = None
                            if gameinfo.get('status') in ['Final', 'Game Over', 'Completed Early']:
                                if int(gameinfo.get('home').get('runs')) > int(gameinfo.get('away').get('runs')):
                                    original_pretitle = game.get('pretitle').replace(gameinfo.get('home').get('team_name') + ' (' + gameinfo.get('home').get('win') + '-' + gameinfo.get('home').get('loss') + ')', gameinfo.get('home').get('team_name') + ' (' + str(int(gameinfo.get('home').get('win'))-1) + '-' + gameinfo.get('home').get('loss') + ')').replace(gameinfo.get('away').get('team_name') + ' (' + gameinfo.get('away').get('win') + '-' + gameinfo.get('away').get('loss') + ')', gameinfo.get('away').get('team_name') + ' (' + gameinfo.get('away').get('win') + '-' + str(int(gameinfo.get('away').get('loss'))-1) + ')')
                                elif int(gameinfo.get('away').get('runs')) > int(gameinfo.get('home').get('runs')):
                                    original_pretitle = game.get('pretitle').replace(gameinfo.get('home').get('team_name') + ' (' + gameinfo.get('home').get('win') + '-' + gameinfo.get('home').get('loss') + ')', gameinfo.get('home').get('team_name') + ' (' + gameinfo.get('home').get('win') + '-' + str(int(gameinfo.get('home').get('loss'))-1) + ')').replace(gameinfo.get('away').get('team_name') + ' (' + gameinfo.get('away').get('win') + '-' + gameinfo.get('away').get('loss') + ')', gameinfo.get('away').get('team_name') + ' (' + str(int(gameinfo.get('away').get('win'))-1) + '-' + gameinfo.get('away').get('loss') + ')')
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Detected Game",k,"is over. Checking for thread with previous title..."
                            for submission in subreddit.new():
                                if submission.title in [game.get('pretitle'), original_pretitle]:
                                    if submission.title == original_pretitle: game.update({'pretitle' : original_pretitle})
                                    if game.get('doubleheader') and self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"consolidated doubleheader pregame thread already posted, submitting edits..."
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_pre_code(games,k,otherk))
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Edits submitted. Sleeping for 5 seconds..."
                                        game.update({'presub' : submission})
                                    else:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"pregame thread already posted, submitting edits..."
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_pre_code(games,k))
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Edits submitted. Sleeping for 5 seconds..."
                                    time.sleep(5)
                                    break
                            if not game.get('presub'):
                                if self.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES')>=0:
                                    time_to_post = timechecker.gamecheck(game.get('url'),game,othergame,just_get_time=True)
                                    minutes_until_post_time = int((time_to_post-datetime.today()).total_seconds() / 60)
                                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Minutes until game thread post time:",minutes_until_post_time
                                    if minutes_until_post_time <= self.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Suppressing pregame thread for Game",k,"because game thread will be posted soon..."
                                        break
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting pregame thread for Game",k,"..."
                                game.update({'presub' : subreddit.submit(game.get('pretitle'), selftext=edit.generate_pre_code(games,k,otherk), send_replies=self.SETTINGS.get('PRE_THREAD').get('INBOX_REPLIES'))})
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Pregame thread submitted..."
                                if self.SETTINGS.get('STICKY'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                    try:
                                        game.get('presub').mod.sticky()
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                    except:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of pregame thread failed (check mod privileges), continuing."

                                if self.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                    if self.SETTINGS.get('PRE_THREAD').get('FLAIR') == "":
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = submitter, but PRE_THREAD : FLAIR is blank..."
                                    else:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as submitter..."
                                        choices = game.get('presub').flair.choices()
                                        flairsuccess = False
                                        for p in choices:
                                            if p['flair_text'] == self.SETTINGS.get('PRE_THREAD').get('FLAIR'):
                                                game.get('presub').flair.select(p['flair_template_id'])
                                                flairsuccess = True
                                        if flairsuccess:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."
                                        else:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Flair not set: could not find flair in available choices"
                                elif self.SETTINGS.get('FLAIR_MODE') == 'mod':
                                    if self.SETTINGS.get('PRE_THREAD').get('FLAIR') == "":
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = mod, but PRE_THREAD : FLAIR is blank..."
                                    else:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as mod..."
                                        game.get('presub').mod.flair(self.SETTINGS.get('PRE_THREAD').get('FLAIR'))
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."

                                if self.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT') != "":
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Setting suggested sort to " + self.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT') + "..."
                                    try:
                                        game.get('presub').mod.suggested_sort(self.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT'))
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Suggested sort set..."
                                    except:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on pregame thread failed (check mod privileges), continuing."

                                if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                time.sleep(5)

                            if self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and game.get('doubleheader'):
                                if othergame.get('doubleheader'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Linking pregame submission to doubleheader Game",otherk,"..."
                                    othergame.update({'presub' : game.get('presub')})

                            break
                        except Exception, err:
                            if self.SETTINGS.get('LOG_LEVEL')>0: print err, ": retrying after 30 seconds..."
                            time.sleep(30)
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Finished posting pregame threads..."
                if self.SETTINGS.get('LOG_LEVEL')>3: print "games:",games
            elif not self.SETTINGS.get('PRE_THREAD').get('ENABLED') and len(games):
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Pregame thread disabled..."

            if len(games) > 0:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Generating game thread titles for all games..."
                for k,game in games.items():
                    game.update({'gametitle': edit.generate_title(game.get('url'),'game',game.get('doubleheader'),game.get('game_nbr'))})

            while len(games) > 0:
                for k,game in games.items():
                    if self.SETTINGS.get('LOG_LEVEL')>1 and len(games)>1: print "Game",k,"check"
                    for otherk,othergame in games.items():
                        if othergame.get('url')[:-2] == game.get('url')[:-2] and othergame.get('url') != game.get('url'): break
                    if not othergame.get('doubleheader'): othergame = {}
                    if othergame.get('doubleheader') and othergame.get('final') and not game.get('gamesub'):
                        if self.SETTINGS.get('LOG_LEVEL')>2: print "Updating title for doubleheader Game",k,"since Game",otherk,"is final..."
                        game.update({'gametitle': edit.generate_title(game.get('url'),'game',game.get('doubleheader'),game.get('game_nbr'))})
                    game.update({'status' : edit.get_status(game.get('url'))})
                    if timechecker.gamecheck(game.get('url'),game,othergame,activegames+pendinggames) == True:
                        if not game.get('final'):
                            check = datetime.today()
                            try:
                                subreddit = r.subreddit(self.SETTINGS.get('SUBREDDIT'))
                                if self.SETTINGS.get('STICKY'):
                                    if len(stale_games):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying stale threads..."
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
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of stale posts failed, continuing."
                                        stale_games = {}
                                    if game.get('presub') and not game.get('gamesub'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying Game",k,"pregame thread..."
                                        try:
                                            game.get('presub').mod.sticky(state=False)
                                        except:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of pregame thread failed, continuing."
                                if not game.get('gamesub'):
                                    gameinfo = edit.get_teams_time(game.get('url'))
                                    original_gametitle = None
                                    if gameinfo.get('status') in ['Final', 'Game Over', 'Completed Early']:
                                        if int(gameinfo.get('home').get('runs')) > int(gameinfo.get('away').get('runs')):
                                            original_gametitle = game.get('gametitle').replace(gameinfo.get('home').get('team_name') + ' (' + gameinfo.get('home').get('win') + '-' + gameinfo.get('home').get('loss') + ')', gameinfo.get('home').get('team_name') + ' (' + str(int(gameinfo.get('home').get('win'))-1) + '-' + gameinfo.get('home').get('loss') + ')').replace(gameinfo.get('away').get('team_name') + ' (' + gameinfo.get('away').get('win') + '-' + gameinfo.get('away').get('loss') + ')', gameinfo.get('away').get('team_name') + ' (' + gameinfo.get('away').get('win') + '-' + str(int(gameinfo.get('away').get('loss'))-1) + ')')
                                        elif int(gameinfo.get('away').get('runs')) > int(gameinfo.get('home').get('runs')):
                                            original_gametitle = game.get('gametitle').replace(gameinfo.get('home').get('team_name') + ' (' + gameinfo.get('home').get('win') + '-' + gameinfo.get('home').get('loss') + ')', gameinfo.get('home').get('team_name') + ' (' + gameinfo.get('home').get('win') + '-' + str(int(gameinfo.get('home').get('loss'))-1) + ')').replace(gameinfo.get('away').get('team_name') + ' (' + gameinfo.get('away').get('win') + '-' + gameinfo.get('away').get('loss') + ')', gameinfo.get('away').get('team_name') + ' (' + str(int(gameinfo.get('away').get('win'))-1) + '-' + gameinfo.get('away').get('loss') + ')')
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Detected Game",k,"is over. Checking for thread with previous title..."
                                    for submission in subreddit.new():
                                        if submission.title in [game.get('gametitle'), original_gametitle]:
                                            if submission.title == original_gametitle: game.update({'gametitle' : original_gametitle})
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"thread already posted, getting submission..."
                                            game.update({'gamesub' : submission, 'status' : edit.get_status(game.get('url'))})
                                            threads[k].update({'game' : submission.selftext})
                                            break
                                if not game.get('gamesub'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting game thread for Game",k,"..."
                                    threads[k].update({'game' : edit.generate_code(game.get('url'),"game")})
                                    if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP'): 
                                        lastupdate = "^^^Last ^^^Updated: ^^^" + datetime.strftime(datetime.today(), "%m/%d/%Y ^^^%I:%M:%S ^^^%p ^^^") + self.SETTINGS.get('BOT_TIME_ZONE')
                                    else: lastupdate = ""
                                    threadtext = threads[k].get('game') + lastupdate
                                    game.update({'gamesub' : subreddit.submit(game.get('gametitle'), selftext=threadtext, send_replies=self.SETTINGS.get('GAME_THREAD').get('INBOX_REPLIES')), 'status' : edit.get_status(game.get('url'))})
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Game thread submitted..."

                                    if self.SETTINGS.get('STICKY'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                        try:
                                            game.get('gamesub').mod.sticky()
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                        except:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of game thread failed (check mod privileges), continuing."

                                    if self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT') != "":
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Setting suggested sort to " + self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT') + "..."
                                        try:
                                            game.get('gamesub').mod.suggested_sort(self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT'))
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Suggested sort set..."
                                        except:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on game thread failed (check mod privileges), continuing."

                                    if self.SETTINGS.get('GAME_THREAD').get('MESSAGE'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Messaging Baseballbot..."
                                        r.redditor('baseballbot').message('Gamethread posted', game.get('gamesub').shortlink)
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Baseballbot messaged..."

                                    if self.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                        if self.SETTINGS.get('GAME_THREAD').get('FLAIR') == "":
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = submitter, but GAME_THREAD : FLAIR is blank..."
                                        else:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as submitter..."
                                            choices = game.get('gamesub').flair.choices()
                                            flairsuccess = False
                                            for p in choices:
                                                if p['flair_text'] == self.SETTINGS.get('GAME_THREAD').get('FLAIR'):
                                                    game.get('gamesub').flair.select(p['flair_template_id'])
                                                    flairsuccess = True
                                            if flairsuccess:
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."
                                            else:
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Flair not set: could not find flair in available choices"
                                    elif self.SETTINGS.get('FLAIR_MODE') == 'mod':
                                        if self.SETTINGS.get('GAME_THREAD').get('FLAIR') == "":
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = mod, but GAME_THREAD : FLAIR is blank..."
                                        else:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as mod..."
                                            game.get('gamesub').mod.flair(self.SETTINGS.get('GAME_THREAD').get('FLAIR'))
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."

                                    skipflag=True
                                    sleeptime = 5 + self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Sleeping for",sleeptime,"seconds..."
                                    time.sleep(sleeptime)

                            except Exception, err:
                                if self.SETTINGS.get('LOG_LEVEL')>0: print "Error while getting/posting game thread: ",err, ": continuing after 10 seconds..."
                                time.sleep(10)

                            check = datetime.today()
                            if skipflag: skipflag=False
                            else:
                                game.update({'status' : edit.get_status(game.get('url'))})
                                threadstr = edit.generate_code(game.get('url'),"game")
                                if threadstr != threads[k].get('game'):
                                    threads[k].update({'game' : threadstr})
                                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Editing thread for Game",k,"..."
                                    while True:
                                        try:
                                            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP'): threadstr += "^^^Last ^^^Updated: ^^^" + datetime.strftime(datetime.today(), "%m/%d/%Y ^^^%I:%M:%S ^^^%p ^^^") + self.SETTINGS.get('BOT_TIME_ZONE')
                                            game.get('gamesub').edit(threadstr)
                                            sleeptime = 5 + self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"edits submitted. Sleeping for",sleeptime,"seconds..."
                                            time.sleep(sleeptime)
                                            break
                                        except Exception, err:
                                            if self.SETTINGS.get('LOG_LEVEL')>0: print datetime.strftime(check, "%d %I:%M:%S %p"),"Couldn't submit edits, retrying in 10 seconds..."
                                            time.sleep(10)
                                else:
                                    sleeptime = 5 + self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"No changes to Game",k,"thread. Sleeping for",sleeptime,"seconds..."
                                    time.sleep(sleeptime)

                            if game.get('status') in ['Final','Game Over','Completed Early','Postponed','Suspended','Cancelled']:
                                check = datetime.today()
                                game.update({'final' : True})
                                if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Status:",game.get('status')
                                if self.SETTINGS.get('POST_THREAD').get('ENABLED'):
                                    try:
                                        game.update({'posttitle' : edit.generate_title(game.get('url'),"post",game.get('doubleheader'),game.get('game_nbr'))})
                                        subreddit = r.subreddit(self.SETTINGS.get('SUBREDDIT'))
                                        if self.SETTINGS.get('STICKY'):
                                            if game.get('presub'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying Game",k,"pregame thread..."
                                                try:
                                                    game.get('presub').mod.sticky(state=False)
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of pregame thread failed, continuing."
                                            if game.get('gamesub'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying Game",k,"game thread..."
                                                try:
                                                    game.get('gamesub').mod.sticky(state=False)
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of game thread failed, continuing."
                                        if not game.get('postsub'):
                                            for submission in subreddit.new():
                                                if submission.title == game.get('posttitle'):
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"postgame thread already posted, getting submission..."
                                                    game.update({'postsub' : submission})
                                                    break
                                        if not game.get('postsub'):
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting postgame thread for Game",k,"..."
                                            game.update({'postsub' : subreddit.submit(game.get('posttitle'), selftext=edit.generate_code(game.get('url'),"post"), send_replies=self.SETTINGS.get('POST_THREAD').get('INBOX_REPLIES'))})
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Postgame thread submitted..."

                                            if self.SETTINGS.get('STICKY'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                                try:
                                                    game.get('postsub').mod.sticky()
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of postgame thread failed (check mod privileges), continuing."

                                            if self.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                                if self.SETTINGS.get('POST_THREAD').get('FLAIR') == "":
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = submitter, but POST_THREAD : FLAIR is blank..."
                                                else:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as submitter..."
                                                    choices = game.get('postsub').flair.choices()
                                                    flairsuccess = False
                                                    for p in choices:
                                                        if p['flair_text'] == self.SETTINGS.get('POST_THREAD').get('FLAIR'):
                                                            game.get('postsub').flair.select(p['flair_template_id'])
                                                            flairsuccess = True
                                                    if flairsuccess:
                                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."
                                                    else:
                                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Flair not set: could not find flair in available choices"
                                            elif self.SETTINGS.get('FLAIR_MODE') == 'mod':
                                                if self.SETTINGS.get('POST_THREAD').get('FLAIR') == "":
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: FLAIR_MODE = mod, but POST_THREAD : FLAIR is blank..."
                                                else:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Adding flair to submission as mod..."
                                                    game.get('postsub').mod.flair(self.SETTINGS.get('POST_THREAD').get('FLAIR'))
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission flaired..."

                                            if self.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT') != "":
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Setting suggested sort to " + self.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT') + "..."
                                                try:
                                                    game.get('postsub').mod.suggested_sort(self.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT'))
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Suggested sort set..."
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on postgame thread failed (check mod privileges), continuing."

                                            if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                            time.sleep(5)
                                    except Exception, err:
                                        if self.SETTINGS.get('LOG_LEVEL')>0: print "Error while posting postgame thread:",err, ": continuing after 15 seconds..."
                                        time.sleep(15)
                        else: 
                            if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Game",k,"final or postponed, nothing to do... "
                check = datetime.today()
                activegames=0
                pendinggames=0
                previewgames=0
                completedgames=0
                delayedgames=0
                for sk,sgame in games.items():
                    if sgame.get('gamesub') and not sgame.get('final'):
                        activegames += 1
                        if sgame.get('status') in ['Preview','Pre-Game','Scheduled']:
                            previewgames += 1
                        if sgame.get('status') in ['Delayed', 'Delayed Start']:
                            delayedgames += 1
                    if not sgame.get('gamesub'):
                        pendinggames += 1
                    if sgame.get('postsub') and sgame.get('final'):
                        completedgames += 1

                if self.SETTINGS.get('LOG_LEVEL')>3: print "threads:",threads
                if len(offday):
                    if self.SETTINGS.get('LOG_LEVEL')>3: print "offday:",offday
                if self.SETTINGS.get('LOG_LEVEL')>3: print "games:",games
                limits = r.auth.limits
                if limits.get('used') > maxapi: maxapi = limits.get('used')
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Reddit API Calls:",limits,"- Max usage today:",maxapi
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Active Games:",activegames,"...in Preview/Pre-Game/Scheduled Status:",previewgames,"...in Delayed Status:",delayedgames,"- Pending Games:",pendinggames,"- Completed Games:",completedgames

                if activegames == 0 and pendinggames == 0:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "All games final for today (or off day), going into end of day loop... "
                    break
                elif pendinggames > 0 and activegames == 0:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"No game threads to post yet, sleeping for 10 minutes... "
                    time.sleep(600)
                elif activegames > 0 and previewgames == activegames:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"All posted games are in Preview/Pre-Game/Scheduled status, sleeping for 5 minutes... "
                    time.sleep(300)
                elif activegames > 0 and (delayedgames + previewgames) == activegames:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"All posted games are in Preview/Pre-Game/Scheduled or Delayed status, sleeping for 1 minute... "
                    time.sleep(60)
                elif limits.get('remaining') < 60:
                    if self.SETTINGS.get('LOG_LEVEL')>0: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Approaching Reddit API rate limit. Taking a 10 second break..."
                    time.sleep(10)
            if datetime.today().day == today.day:
                timechecker.endofdaycheck()
            else:
                if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"NEW DAY"

if __name__ == '__main__':
    program = Bot()
    program.run()
