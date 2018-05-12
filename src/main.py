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
import games
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Bot:

    def __init__(self):
        self.VERSION = '5.1.0'
        self.SETTINGS = {}
        self.games = games.Games().games
        self.gamesLive = games.Games().gamesLive

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

            if self.SETTINGS.get('STICKY') == None:
                warnings.append('Missing STICKY, using default (true - make sure your bot user has mod rights)...')
                self.SETTINGS.update({'STICKY' : True})

            if self.SETTINGS.get('FLAIR_MODE') not in ['', 'none', 'submitter', 'mod']:
                warnings.append('Missing or invalid FLAIR_MODE, using default ("none")...')
                self.SETTINGS.update({'FLAIR_MODE' : 'none'})

            if self.SETTINGS.get('LOG_LEVEL') == None:
                warnings.append('Missing LOG_LEVEL, using default (2)...')
                self.SETTINGS.update({'LOG_LEVEL' : 2})

            if self.SETTINGS.get('OFF_THREAD') == None:
                warnings.append('Missing OFF_THREAD, using defaults (ENABLED: true, TITLE: "OFF DAY THREAD: {date:%A, %B %d}", TIME: 9AM, FOOTER: "No game today. Feel free to discuss whatever you want in this thread.", SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", SUPPRESS_OFFSEASON: true, TWITTER:ENABLED: false, TWITTER:TEXT: "")...')
                self.SETTINGS.update({'OFF_THREAD' : {'ENABLED' : True,'TITLE' : 'OFF DAY THREAD: {date:%A, %B %d}','TIME' : '9AM', 'FOOTER' : 'No game today. Feel free to discuss whatever you want in this thread.', 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'SUPPRESS_OFFSEASON' : True, 'TWITTER' : {'ENABLED' : False, 'TEXT' : ""}}})

            if self.SETTINGS.get('OFF_THREAD').get('ENABLED') == None:
                warnings.append('Missing OFF_THREAD : ENABLED, using default (true)...')
                self.SETTINGS['OFF_THREAD'].update({'ENABLED' : True})

            if self.SETTINGS.get('OFF_THREAD').get('TITLE') == None:
                warnings.append('Missing OFF_THREAD : TITLE, using default ("OFF DAY THREAD: {date:%A, %B %d}")...')
                self.SETTINGS['OFF_THREAD'].update({'TITLE' : 'OFF DAY THREAD: {date:%A, %B %d}'})

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

            if self.SETTINGS.get('OFF_THREAD').get('TWITTER') == None:
                warnings.append('Missing OFF_THREAD : TWITTER, using defaults (ENABLED: false, TEXT: "")...')
                self.SETTINGS['OFF_THREAD'].update({'TWITTER' : {'ENABLED' : False, 'TEXT' : ""}})

            if self.SETTINGS.get('OFF_THREAD').get('TWITTER').get('ENABLED') == None:
                warnings.append('Missing OFF_THREAD : TWITTER : ENABLED, using default (false)...')
                self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False})

            if self.SETTINGS.get('OFF_THREAD').get('TWITTER').get('TEXT') == None:
                warnings.append('Missing OFF_THREAD : TWITTER : TEXT, using default ("")...')
                self.SETTINGS['OFF_THREAD']['TWITTER'].update({'TEXT' : ""})

            if self.SETTINGS.get('PRE_THREAD') == None:
                warnings.append('Missing PRE_THREAD, using defaults (TITLE: "PREGAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}", CONSOLIDATED_DH_TITLE: "PREGAME THREAD:{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d}{dh: - DOUBLEHEADER}", TIME: 9AM, SUPPRESS_MINUTES: 0, SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", HEADER: true, BLURB: true, PROBABLES: true, FOOTER: "", TWITTER:ENABLED: false, TWITTER:TEXT: "", TWITTER:CONSOLIDATED_DH_TEXT: "")...')
                self.SETTINGS.update({'PRE_THREAD' : {'TITLE' : 'PREGAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}', 'CONSOLIDATED_DH_TITLE' : 'PREGAME THREAD:{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d}{dh: - DOUBLEHEADER}', 'TIME' : '9AM', 'SUPPRESS_MINUTES' : 0, 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'CONTENT' : {'HEADER' : True, 'BLURB' : True, 'PROBABLES' : True, 'FOOTER' : ""}, 'TWITTER' : {'ENABLED' : False, 'TEXT' : "", 'CONSOLIDATED_DH_TEXT' : ""}}})

            if self.SETTINGS.get('PRE_THREAD').get('ENABLED') == None:
                warnings.append('Missing PRE_THREAD : ENABLED, using default (true)...')
                self.SETTINGS['PRE_THREAD'].update({'ENABLED' : True})

            if self.SETTINGS.get('PRE_THREAD').get('TITLE') == None:
                warnings.append('Missing PRE_THREAD : TITLE, using default ("PREGAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")...')
                self.SETTINGS['PRE_THREAD'].update({'TITLE' : 'PREGAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}'})

            if self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATED_DH_TITLE') == None:
                warnings.append('Missing PRE_THREAD : CONSOLIDATED_DH_TITLE, using default ("PREGAME THREAD:{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d}{dh: - DOUBLEHEADER}")...')
                self.SETTINGS['PRE_THREAD'].update({'CONSOLIDATED_DH_TITLE' : 'PREGAME THREAD:{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d}{dh: - DOUBLEHEADER}'})

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
                warnings.append('Missing PRE_THREAD : CONTENT, using defaults (HEADER: true, BLURB: true, PROBABLES: true, FOOTER: "")...')
                self.SETTINGS['PRE_THREAD'].update({'CONTENT' : {'HEADER': True, 'BLURB' : True, 'PROBABLES' : True, 'FOOTER' : ""}})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('HEADER') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : HEADER, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'HEADER' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BLURB') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : BLURB, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'BLURB' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('PROBABLES') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : PROBABLES, using default (true)...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'PROBABLES' : True})

            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('FOOTER') == None:
                warnings.append('Missing PRE_THREAD : CONTENT : FOOTER, using default ("")...')
                self.SETTINGS['PRE_THREAD']['CONTENT'].update({'FOOTER' : ""})

            if self.SETTINGS.get('PRE_THREAD').get('TWITTER') == None:
                warnings.append('Missing PRE_THREAD : TWITTER, using defaults (ENABLED: false, TEXT: "")...')
                self.SETTINGS['PRE_THREAD'].update({'TWITTER' : {'ENABLED' : False, 'TEXT' : ""}})

            if self.SETTINGS.get('PRE_THREAD').get('TWITTER').get('ENABLED') == None:
                warnings.append('Missing PRE_THREAD : TWITTER : ENABLED, using default (false)...')
                self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False})

            if self.SETTINGS.get('PRE_THREAD').get('TWITTER').get('TEXT') == None:
                warnings.append('Missing PRE_THREAD : TWITTER : TEXT, using default ("")...')
                self.SETTINGS['PRE_THREAD']['TWITTER'].update({'TEXT' : ""})

            if self.SETTINGS.get('PRE_THREAD').get('TWITTER').get('CONSOLIDATED_DH_TEXT') == None:
                warnings.append('Missing PRE_THREAD : TWITTER : CONSOLIDATED_DH_TEXT, using default ("")...')
                self.SETTINGS['PRE_THREAD']['TWITTER'].update({'CONSOLIDATED_DH_TEXT' : ""})

            if self.SETTINGS.get('GAME_THREAD') == None:
                warnings.append('Missing GAME_THREAD, using defaults (TITLE: "GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}", HOURS_BEFORE: 3, SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", MESSAGE: false, HOLD_DH_GAME2_THREAD: true, EXTRA_SLEEP: 0, HEADER: true, BOX_SCORE: true, EXTENDED_BOX_SCORE: false, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, CURRENT_STATE: true, FOOTER: "**Remember to sort by new to keep up!**", UPDATE_STAMP: true, THEATER_LINK: false, PREVIEW_BLURB: true, PREVIEW_PROBABLES: true, NEXT_GAME: true, TWITTER:ENABLED: false, TWITTER:TEXT: "")...')
                self.SETTINGS.update({'GAME_THREAD' : {'TITLE' : 'GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}', 'HOURS_BEFORE' : 3, 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'MESSAGE' : False, 'HOLD_DH_GAME2_THREAD' : True, 'EXTRA_SLEEP' : 0, 'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'EXTENDED_BOX_SCORE' : False, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'CURRENT_STATE' : True, 'FOOTER' : '**Remember to sort by new to keep up!**', 'UPDATE_STAMP' : True, 'THEATER_LINK' : False, 'PREVIEW_BLURB' : True, 'PREVIEW_PROBABLES' : True, 'NEXT_GAME' : True}, 'TWITTER' : {'ENABLED' : False, 'TEXT' : ""}}})

            if self.SETTINGS.get('GAME_THREAD').get('TITLE') == None:
                warnings.append('Missing GAME_THREAD : TITLE, using default ("GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")...')
                self.SETTINGS['GAME_THREAD'].update({'TITLE' : 'GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}'})

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
                warnings.append('Missing GAME_THREAD : CONTENT, using defaults (HEADER: true, BOX_SCORE: true, EXTENDED_BOX_SCORE : false, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "**Remember to sort by new to keep up!**", THEATER_LINK: false, PREVIEW_BLURB: true, PREVIEW_PROBABLES: true)...')
                self.SETTINGS['GAME_THREAD'].update({'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'EXTENDED_BOX_SCORE' : False,  'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'FOOTER' : '**Remember to sort by new to keep up!**', 'THEATER_LINK' : False, 'PREVIEW_BLURB' : True, 'PREVIEW_PROBABLES' : True}})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('HEADER') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : HEADER, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'HEADER' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('BOX_SCORE') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : BOX_SCORE, using default (true)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'BOX_SCORE' : True})

            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('EXTENDED_BOX_SCORE') == None:
                warnings.append('Missing GAME_THREAD : CONTENT : EXTENDED_BOX_SCORE, using default (false)...')
                self.SETTINGS['GAME_THREAD']['CONTENT'].update({'EXTENDED_BOX_SCORE' : False})

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

            if self.SETTINGS.get('GAME_THREAD').get('TWITTER') == None:
                warnings.append('Missing GAME_THREAD : TWITTER, using defaults (ENABLED: false, TEXT: ""...')
                self.SETTINGS['GAME_THREAD'].update({'TWITTER' : {'ENABLED' : False, 'TEXT' : ""}})

            if self.SETTINGS.get('GAME_THREAD').get('TWITTER').get('ENABLED') == None:
                warnings.append('Missing GAME_THREAD : TWITTER : ENABLED, using default (false)...')
                self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False})

            if self.SETTINGS.get('GAME_THREAD').get('TWITTER').get('TEXT') == None:
                warnings.append('Missing GAME_THREAD : TWITTER : TEXT, using default ("")...')
                self.SETTINGS['GAME_THREAD']['TWITTER'].update({'TEXT' : ""})

            if self.SETTINGS.get('POST_THREAD') == None:
                warnings.append('Missing POST_THREAD, using defaults (WIN_TITLE: "WIN THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}", LOSS_TITLE: "LOSS THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}", OTHER_TITLE: "POST GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}", SUGGESTED_SORT: "new", INBOX_REPLIES: false, FLAIR: "", HEADER: true, BOX_SCORE: true, EXTENDED_BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "", THEATER_LINK: true, NEXT_GAME: true, TWITTER:ENABLED: false, TWITTER:WIN_TEXT: "", TWITTER:LOSS_TEXT: "", TWITTER:OTHER_TEXT: "")...')
                self.SETTINGS.update({'POST_THREAD' : {'WIN_TITLE' : 'WIN THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}', 'LOSS_TITLE' : 'LOSS THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}', 'OTHER_TITLE' : 'POST GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}', 'SUGGESTED_SORT': 'new', 'INBOX_REPLIES': False, 'FLAIR' : '', 'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'EXTENDED_BOX_SCORE' : True, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'FOOTER' : '', 'THEATER_LINK' : True, 'NEXT_GAME' : True}, 'TWITTER' : {'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""}}})

            if self.SETTINGS.get('POST_THREAD').get('ENABLED') == None:
                warnings.append('Missing POST_THREAD : ENABLED, using default (true)...')
                self.SETTINGS['POST_THREAD'].update({'ENABLED' : True})

            if self.SETTINGS.get('POST_THREAD').get('WIN_TITLE') == None:
                warnings.append('Missing POST_THREAD : WIN_TITLE, using default ("WIN THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")...')
                self.SETTINGS['POST_THREAD'].update({'WIN_TITLE' : 'WIN THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}'})

            if self.SETTINGS.get('POST_THREAD').get('LOSS_TITLE') == None:
                warnings.append('Missing POST_THREAD : LOSS_TITLE, using default ("LOSS THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")...')
                self.SETTINGS['POST_THREAD'].update({'LOSS_TITLE' : 'LOSS THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}'})

            if self.SETTINGS.get('POST_THREAD').get('OTHER_TITLE') == None:
                warnings.append('Missing POST_THREAD : OTHER_TITLE, using default ("POST GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}")...')
                self.SETTINGS['POST_THREAD'].update({'OTHER_TITLE' : 'POST GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}'})

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
                warnings.append('Missing POST_THREAD : CONTENT, using defaults (HEADER: true, BOX_SCORE: true, EXTENDED_BOX_SCORE: true, LINE_SCORE: true, SCORING_PLAYS: true, HIGHLIGHTS: true, FOOTER: "", THEATER_LINK: true)...')
                self.SETTINGS['POST_THREAD'].update({'CONTENT' : {'HEADER' : True, 'BOX_SCORE' : True, 'EXTENDED_BOX_SCORE' : True, 'LINE_SCORE' : True, 'SCORING_PLAYS' : True, 'HIGHLIGHTS' : True, 'FOOTER' : '', 'THEATER_LINK' : True}})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('HEADER') == None:
                warnings.append('Missing POST_THREAD : CONTENT : HEADER, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'HEADER' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('BOX_SCORE') == None:
                warnings.append('Missing POST_THREAD : CONTENT : BOX_SCORE, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'BOX_SCORE' : True})

            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('EXTENDED_BOX_SCORE') == None:
                warnings.append('Missing POST_THREAD : CONTENT : EXTENDED_BOX_SCORE, using default (true)...')
                self.SETTINGS['POST_THREAD']['CONTENT'].update({'EXTENDED_BOX_SCORE' : True})

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

            if self.SETTINGS.get('POST_THREAD').get('TWITTER') == None:
                warnings.append('Missing POST_THREAD : TWITTER, using defaults (ENABLED: false, WIN_TEXT: "", LOSS_TEXT: "", OTHER_TEXT: ""...')
                self.SETTINGS['POST_THREAD'].update({'TWITTER' : {'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""}})

            if self.SETTINGS.get('POST_THREAD').get('TWITTER').get('ENABLED') == None:
                warnings.append('Missing POST_THREAD : TWITTER : ENABLED, using default (false)...')
                self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False})

            if self.SETTINGS.get('POST_THREAD').get('TWITTER').get('WIN_TEXT') == None:
                warnings.append('Missing POST_THREAD : TWITTER : WIN_TEXT, using default ("")...')
                self.SETTINGS['POST_THREAD']['TWITTER'].update({'WIN_TEXT' : ""})

            if self.SETTINGS.get('POST_THREAD').get('TWITTER').get('LOSS_TEXT') == None:
                warnings.append('Missing POST_THREAD : TWITTER : LOSS_TEXT, using default ("")...')
                self.SETTINGS['POST_THREAD']['TWITTER'].update({'LOSS_TEXT' : ""})

            if self.SETTINGS.get('POST_THREAD').get('TWITTER').get('OTHER_TEXT') == None:
                warnings.append('Missing POST_THREAD : TWITTER : OTHER_TEXT, using default ("")...')
                self.SETTINGS['POST_THREAD']['TWITTER'].update({'OTHER_TEXT' : ""})

            if self.SETTINGS.get('TWITTER') == None:
                warnings.append('Missing TWITTER, disabling Twitter features...')
                self.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : None, 'CONSUMER_SECRET' : None, 'ACCESS_TOKEN' : None, 'ACCESS_SECRET' : None})
                self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""})
            else:
                if self.SETTINGS.get('TWITTER').get('CONSUMER_KEY') in [None, "XXX"]:
                    warnings.append('Missing TWITTER : CONSUMER_KEY (or invalid value), disabling Twitter features...')
                    self.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : None, 'CONSUMER_SECRET' : None, 'ACCESS_TOKEN' : None, 'ACCESS_SECRET' : None})
                    self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""})
                if self.SETTINGS.get('TWITTER').get('CONSUMER_SECRET') in [None, "XXX"]:
                    warnings.append('Missing TWITTER : CONSUMER_SECRET (or invalid value), disabling Twitter features...')
                    self.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : None, 'CONSUMER_SECRET' : None, 'ACCESS_TOKEN' : None, 'ACCESS_SECRET' : None})
                    self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""})
                if self.SETTINGS.get('TWITTER').get('ACCESS_TOKEN') in [None, "XXX"]:
                    warnings.append('Missing TWITTER : ACCESS_TOKEN (or invalid value), disabling Twitter features...')
                    self.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : None, 'CONSUMER_SECRET' : None, 'ACCESS_TOKEN' : None, 'ACCESS_SECRET' : None})
                    self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""})
                if self.SETTINGS.get('TWITTER').get('ACCESS_SECRET') in [None, "XXX"]:
                    warnings.append('Missing TWITTER : ACCESS_SECRET (or invalid value), disabling Twitter features...')
                    self.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : None, 'CONSUMER_SECRET' : None, 'ACCESS_TOKEN' : None, 'ACCESS_SECRET' : None})
                    self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                    self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""})

            if self.SETTINGS.get('apiURL') == None:
                self.SETTINGS.update({'apiURL' : 'https://statsapi.mlb.com'})

            if self.SETTINGS.get('LOG_LEVEL')>3: print "Settings:",self.SETTINGS

        return {'fatal' : fatal_errors, 'warnings' : warnings}

    def run(self):

        settings_results = self.read_settings()

        warnings = settings_results.get('warnings',[])
        fatal_errors = settings_results.get('fatal',[])
        
        if (self.SETTINGS['OFF_THREAD']['ENABLED'] and self.SETTINGS['OFF_THREAD']['TWITTER']['ENABLED']) or (self.SETTINGS['PRE_THREAD']['ENABLED'] and self.SETTINGS['PRE_THREAD']['TWITTER']['ENABLED']) or (self.SETTINGS['GAME_THREAD']['ENABLED'] and self.SETTINGS['GAME_THREAD']['TWITTER']['ENABLED']) or (self.SETTINGS['POST_THREAD']['ENABLED'] and self.SETTINGS['POST_THREAD']['TWITTER']['ENABLED']):
            try:
                import twitter
            except:
                warnings.append('Unable to import python-twitter module. Please ensure it is installed. Disabling Twitter features...')
                self.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : None, 'CONSUMER_SECRET' : None, 'ACCESS_TOKEN' : None, 'ACCESS_SECRET' : None})
                self.SETTINGS['OFF_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                self.SETTINGS['PRE_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                self.SETTINGS['GAME_THREAD']['TWITTER'].update({'ENABLED' : False, 'TEXT' : ""})
                self.SETTINGS['POST_THREAD']['TWITTER'].update({'ENABLED' : False, 'WIN_TEXT' : "", 'LOSS_TEXT' : "", 'OTHER_TEXT' : ""})
            else:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Initiating Twitter instance..."
                twt = twitter.Api(self.SETTINGS.get('TWITTER').get('CONSUMER_KEY'),
                                       self.SETTINGS.get('TWITTER').get('CONSUMER_SECRET'),
                                       self.SETTINGS.get('TWITTER').get('ACCESS_TOKEN'),
                                       self.SETTINGS.get('TWITTER').get('ACCESS_SECRET'))
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Twitter authorized user:",twt.VerifyCredentials().screen_name

        if len(warnings):
            if self.SETTINGS.get('LOG_LEVEL')>1:
                for warn in warnings:
                    print "WARNING:",warn

        if len(fatal_errors):
            if self.SETTINGS.get('LOG_LEVEL')>0:
                for fatal_err in fatal_errors:
                    print "FATAL ERROR:",fatal_err
            return

        edit = editor.Editor(self.SETTINGS)

        while True:
            myteam = edit.lookup_team_info(field='all',lookupfield='team_code',lookupval=self.SETTINGS.get('TEAM_CODE'))
            if myteam == -1:
                time.sleep(10)
            elif myteam == None or myteam.get('team_code') != self.SETTINGS.get('TEAM_CODE'):
                if self.SETTINGS.get('LOG_LEVEL')>0: print "FATAL ERROR: Invalid team code detected:",self.SETTINGS.get('TEAM_CODE'),"-- use lookup_team_code.py to look up the correct team code; see README.md"
                return
            else: break

        timechecker = timecheck.TimeCheck(self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE') * 60 * 60, self.SETTINGS.get('LOG_LEVEL'), self.SETTINGS.get('GAME_THREAD').get('HOLD_DH_GAME2_THREAD'), self.SETTINGS.get('POST_THREAD').get('ENABLED'))

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

        stale_games = {}
        offday = {}
        threads = {}
        offseason = False

        while True:
            if len(offday):
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Marking yesterday's offday thread as stale..."
                stale_games[0] = offday
            else:
                if len(self.games)>0:
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Marking yesterday's threads as stale..."
                    stale_games = self.games.copy()
            if self.SETTINGS.get('STICKY') and len(stale_games)==0:
                dateformats = []
                if self.SETTINGS.get('OFF_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(self.SETTINGS.get('OFF_THREAD').get('TITLE')[self.SETTINGS.get('OFF_THREAD').get('TITLE').find('{date:')+6:self.SETTINGS.get('OFF_THREAD').get('TITLE').find('}',self.SETTINGS.get('OFF_THREAD').get('TITLE').find('{date:'))])
                if self.SETTINGS.get('PRE_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(self.SETTINGS.get('PRE_THREAD').get('TITLE')[self.SETTINGS.get('PRE_THREAD').get('TITLE').find('{date:')+6:self.SETTINGS.get('PRE_THREAD').get('TITLE').find('}',self.SETTINGS.get('PRE_THREAD').get('TITLE').find('{date:'))])
                if self.SETTINGS.get('GAME_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(self.SETTINGS.get('GAME_THREAD').get('TITLE')[self.SETTINGS.get('GAME_THREAD').get('TITLE').find('{date:')+6:self.SETTINGS.get('GAME_THREAD').get('TITLE').find('}',self.SETTINGS.get('GAME_THREAD').get('TITLE').find('{date:'))])
                if self.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('{date:') > -1:
                    dateformats.append(self.SETTINGS.get('POST_THREAD').get('WIN_TITLE')[self.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('{date:')+6:self.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('}',self.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('{date:'))])
                if self.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('{date:') > -1:
                    dateformats.append(self.SETTINGS.get('POST_THREAD').get('LOSS_TITLE')[self.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('{date:')+6:self.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('}',self.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('{date:'))])
                if self.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('{date:') > -1:
                    dateformats.append(self.SETTINGS.get('POST_THREAD').get('OTHER_TITLE')[self.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('{date:')+6:self.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('}',self.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('{date:'))])
                if len(dateformats)==0: dateformats = ["%B %d, %Y"]
                dateformats = list(set(dateformats))
                datestocheck = []
                for f in dateformats:
                    datestocheck.append(datetime.strftime(datetime.now(),f.replace('%I:%M %p','').replace('%I:%M%p','').replace('%I:%M','').replace(' @ ','').replace('  ',' ')).rstrip())
                try:
                    sticky1 = r.subreddit(self.SETTINGS.get('SUBREDDIT')).sticky(1)
                    if sticky1.author == r.user.me() and not any(f in sticky1.title for f in datestocheck):
                        stale_games[len(stale_games)] = {'gamesub' : sticky1, 'gametitle' : sticky1.title}
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Found stale thread in top sticky slot ("+sticky1.title+")..."
                    sticky2 = r.subreddit(self.SETTINGS.get('SUBREDDIT')).sticky(2)
                    if sticky2.author == r.user.me() and not any(f in sticky2.title for f in datestocheck):
                        stale_games[len(stale_games)] = {'gamesub' : sticky2, 'gametitle' : sticky2.title}
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Found stale thread in bottom sticky slot ("+sticky2.title+")..."
                except:
                    pass
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Stale games:",stale_games

            today = datetime.today()
            #today = datetime.strptime('2018-04-06','%Y-%m-%d') # leave commented unless testing

            if self.SETTINGS.get('LOG_LEVEL')>2: print "Clearing api cache..."
            edit.gamesLive.clear() #clear api cache daily to keep memory usage down
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Clearing team info cache..."
            edit.TEAMINFO.clear() #clear team info cache daily to keep data fresh

            todaygames = edit.get_schedule(today,myteam.get('team_id'))

            threads = {}
            offday = {}
            self.games.clear()
            activegames = completedgames = previewgames = maxapi = 0
            i = 1

            if todaygames[0]:
                for todaygame in todaygames:
                    hometeam = todaygame.get('teams').get('home').get('team').get('id')
                    awayteam = todaygame.get('teams').get('away').get('team').get('id')
                    homeaway = None
                    if hometeam == int(myteam.get('team_id')):
                        homeaway = 'home'
                    elif awayteam == int(myteam.get('team_id')):
                        homeaway = 'away'
                    if homeaway != None:
                        if self.SETTINGS.get('LOG_LEVEL')>3: print "Found game " + str(i) + ": ",todaygame
                        self.games[i] = todaygame
                        self.games[i].update({'homeaway' : homeaway, 'final' : False, 'skipflag' : False})
                        if todaygame.get('doubleHeader') != 'N':
                            self.games[i].update({'doubleheader' : True})
                            if todaygame.get('doubleHeader') == "S": dhtype = 'split'
                            if todaygame.get('doubleHeader') == "Y": dhtype = 'straight'
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Game " + str(i) + " detected as " + dhtype + " doubleheader game " + str(todaygame.get('gameNumber')) + "..."
                        else: self.games[i].update({'doubleheader' : False})
                        ## Start support for legacy URL
                        gamelive = edit.api_download(todaygame.get('link'))
                        gamelivedir = gamelive.get('gameData').get('links',{}).get('dataDirectory')
                        if gamelivedir != None:
                            self.games[i].update({'url' : 'http://gd2.mlb.com' + gamelivedir + '/'})
                        else:
                            gameliveid = gamelive.get('gameData').get('game').get('id')
                            gameurl = "http://gd2.mlb.com/components/game/mlb/" + "year_" + today.strftime("%Y") + "/month_" + today.strftime("%m") + "/day_" + today.strftime("%d") + "/"
                            gameurl += 'gid_' + gameliveid.replace('/','_').replace('-','_') + '/'
                            self.games[i].update({'url' : gameurl})
                        ## End support for legacy URL
                        if self.SETTINGS.get('LOG_LEVEL')>3: print "Legacy data directory for Game " + str(i) + ": " + self.games[i].get('url')
                        self.games[i].update({'gameInfo' : edit.get_teams_time(pk=self.games[i].get('gamePk'),d=today.date())})
                        self.games[i].get('gameInfo').pop('status') #remove redundant status node (it won't be kept up-to-date anyway)
                        threads[i] = {'game' : '', 'post' : '', 'pre' : ''}
                        i += 1
                if len(self.games) > 1:
                    for a,g in self.games.items(): #Update games with id of other game in the doubleheader
                        if g.get('doubleHeader') != 'N':
                            ghometeam = g.get('teams').get('home').get('team').get('id')
                            gawayteam = g.get('teams').get('away').get('team').get('id')
                            for b,h in self.games.items():
                                hhometeam = h.get('teams').get('home').get('team').get('id')
                                hawayteam = h.get('teams').get('away').get('team').get('id')
                                if str(g.get('gamePk')) != str(h.get('gamePk')) and ghometeam == hhometeam and gawayteam == hawayteam and g.get('doubleHeader') == h.get('doubleHeader'):
                                    self.games[a].update({'othergame' : b})
                                    if self.SETTINGS.get('LOG_LEVEL')>3: print "Game " + str(a) + " other doubleheader game found, game id: " + str(b) + "..."
                        else: self.games[a].update({'othergame' : 0})
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Today's games:",self.games
            pendinggames = len(self.games)

            if len(self.games) == 0:
                next_game = edit.next_game(30,team_id=myteam.get('team_id'))
                if next_game.get('days_away')==None:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "No games in the next 30 days. It's the off season..."
                    offseason = True
                elif next_game.get('days_away') > 14:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Next game is",next_game.get('days_away'),"days away. It's the off season..."
                    offseason = True
                elif next_game.get('days_away') <= 14:
                    last_game = edit.last_game(14,myteam.get('team_id'))
                    if not last_game.get('days_ago'):
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Next game is",next_game.get('days_away'),"day(s) away, but no games in the last 14 days. It's the off season..."
                        offseason = True
                    else:
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "No games today..."
                        offseason = False
                else:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "No games today..."
                    offseason = False

            if self.SETTINGS.get('OFF_THREAD').get('ENABLED') and len(self.games) == 0 and not (offseason and self.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON')):
                timechecker.pregamecheck(self.SETTINGS.get('OFF_THREAD').get('TIME'))
                offday.update({'offtitle': edit.generate_title(0,"off"), 'offmessage' : self.SETTINGS.get('OFF_THREAD').get('FOOTER')})
                if next_game.get('date'): 
                    nex = edit.generate_next_game(next_game=next_game)
                    if len(self.SETTINGS.get('OFF_THREAD').get('FOOTER')): nex += "\n\n"
                    offday.update({'offmessage' : nex + self.SETTINGS.get('OFF_THREAD').get('FOOTER')})
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
                            if self.SETTINGS.get('STICKY'):
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                try:
                                    offday.get('offsub').mod.sticky()
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                except:
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of offday thread failed (check mod privileges or the thread may have already been sticky), continuing..."
                            if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Finished posting offday thread, going into end of day loop..."
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
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of stale posts failed, continuing..."
                            stale_games.clear()

                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting offday thread..."
                        offday.update({'offsub' : subreddit.submit(offday.get('offtitle'), selftext=offday.get('offmessage'), send_replies=self.SETTINGS.get('OFF_THREAD').get('INBOX_REPLIES'))})
                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Offday thread submitted..."

                        if self.SETTINGS.get('STICKY'):
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                            try:
                                offday.get('offsub').mod.sticky()
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                            except:
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of offday thread failed (check mod privileges), continuing..."

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
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on offday thread failed (check mod privileges), continuing..."

                        if self.SETTINGS.get('OFF_THREAD').get('TWITTER').get('ENABLED'):
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Preparing to tweet link to off day thread..."
                            tweetText = edit.replace_params(self.SETTINGS.get('OFF_THREAD').get('TWITTER').get('TEXT').replace('{link}',offday.get('offsub').shortlink), 'off', 'tweet')
                            twt.PostUpdate(tweetText)
                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Tweet submitted..."

                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Finished posting offday thread, going into end of day loop..."
                except Exception, err:
                    if self.SETTINGS.get('LOG_LEVEL')>0: print "Error posting off day thread:",err
            elif not self.SETTINGS.get('OFF_THREAD').get('ENABLED') and len(self.games) == 0:
                if self.SETTINGS.get('LOG_LEVEL')>1: print "Off day detected, but off day thread disabled. Going into end of day loop..."
            elif offseason and self.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON') and len(self.games) == 0:
                if self.SETTINGS.get('LOG_LEVEL')>1: print "Suppressing off day thread during off season, going into end of day loop..."

            if self.SETTINGS.get('PRE_THREAD').get('ENABLED') and len(self.games) > 0:
                timechecker.pregamecheck(self.SETTINGS.get('PRE_THREAD').get('TIME'))
                for k,game in self.games.items():
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Preparing to post pregame thread for Game",k,"..."
                    game.update({'pretitle': edit.generate_title(k,"pre")})
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
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of stale posts failed, continuing..."
                                stale_games.clear()
                            if self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and game.get('doubleheader'):
                                if game.get('presub'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Consolidated pregame thread already posted and linked to this game..."
                                    break
                                if not game.get('presub') and self.games[game.get('othergame')].get('presub'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Linking this game to existing consolidated pregame thread from doubleheader game",game.get('othergame'),"..."
                                    game.update({'presub' : self.games[game.get('othergame')].get('presub')})
                                    break
                            original_pretitle = None
                            if game.get('status').get('abstractGameState') == 'Final':
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Detected Game",k,"is over. Checking for pre thread with previous title (subtracting win/loss from team records)..."
                                original_pretitle = edit.generate_title(k,"pre",True)

                            for submission in subreddit.new():
                                if submission.title in [game.get('pretitle'), original_pretitle]:
                                    if submission.title == original_pretitle: game.update({'pretitle' : original_pretitle})
                                    if game.get('doubleheader') and self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"consolidated doubleheader pregame thread already posted, submitting edits..."
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_thread_code('pre',k,game.get('othergame')))
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Edits submitted. Sleeping for 5 seconds..."
                                        game.update({'presub' : submission})
                                    else:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"pregame thread already posted, submitting edits..."
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_thread_code('pre',k))
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Edits submitted. Sleeping for 5 seconds..."
                                        if self.SETTINGS.get('STICKY'):
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                            try:
                                                game.get('presub').mod.sticky()
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                            except:
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of pregame thread failed (check mod privileges or the thread may have already been sticky), continuing..."
                                    time.sleep(5)
                                    break
                            if not game.get('presub'):
                                if self.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES')>=0:
                                    time_to_post = timechecker.gamecheck(k,just_get_time=True)
                                    minutes_until_post_time = int((time_to_post-edit.convert_tz(datetime.utcnow(),'bot')).total_seconds() / 60)
                                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Minutes until game thread post time:",minutes_until_post_time
                                    if minutes_until_post_time <= self.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Suppressing pregame thread for Game",k,"because game thread will be posted soon..."
                                        break
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting pregame thread for Game",k,"..."
                                game.update({'presub' : subreddit.submit(game.get('pretitle'), selftext=edit.generate_thread_code('pre',k,game.get('othergame')), send_replies=self.SETTINGS.get('PRE_THREAD').get('INBOX_REPLIES'))})
                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Pregame thread submitted..."
                                if self.SETTINGS.get('STICKY'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                    try:
                                        game.get('presub').mod.sticky()
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                    except:
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of pregame thread failed (check mod privileges), continuing..."

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
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on pregame thread failed (check mod privileges), continuing..."

                                if self.SETTINGS.get('PRE_THREAD').get('TWITTER').get('ENABLED'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Preparing to tweet link to pregame thread..."
                                    if game.get('doubleheader') and self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'):
                                        tweetText = edit.replace_params(self.SETTINGS.get('PRE_THREAD').get('TWITTER').get('CONSOLIDATED_DH_TEXT').replace('{link}',game.get('presub').shortlink), 'pre', 'tweet', k)
                                    else: tweetText = edit.replace_params(self.SETTINGS.get('PRE_THREAD').get('TWITTER').get('TEXT').replace('{link}',game.get('presub').shortlink), 'pre', 'tweet', k)
                                    twt.PostUpdate(tweetText)
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Tweet submitted..."

                                if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                time.sleep(5)

                            if self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and game.get('doubleheader'):
                                if self.games[game.get('othergame')].get('doubleheader'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Linking pregame submission to doubleheader Game",game.get('othergame'),"..."
                                    self.games[game.get('othergame')].update({'presub' : game.get('presub')})
                            break
                        except Exception, err:
                            if self.SETTINGS.get('LOG_LEVEL')>0: print "Error posting/editing pregame thread:",err,": retrying after 30 seconds..."
                            time.sleep(30)
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Finished posting pregame threads..."
                if self.SETTINGS.get('LOG_LEVEL')>3: print "self.games:",self.games
            elif not self.SETTINGS.get('PRE_THREAD').get('ENABLED') and len(self.games):
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Pregame thread disabled..."

            if len(self.games) > 0:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Generating game thread titles for all games..."
                for k,game in self.games.items():
                    game.update({'gametitle': edit.generate_title(k,'game')})

            while len(self.games) > 0:
                for k,game in self.games.items():
                    if self.SETTINGS.get('LOG_LEVEL')>2 and len(self.games)>1: print "Game",k,"check"
                    if game.get('othergame')>0 and self.games[game.get('othergame')].get('doubleheader') and self.games[game.get('othergame')].get('final') and not game.get('gamesub'):
                        if self.SETTINGS.get('LOG_LEVEL')>2: print "Updating title for doubleheader Game",k,"since Game",game.get('othergame'),"is final..."
                        game.update({'gametitle': edit.generate_title(k,'game')})
                    game.update({'status' : edit.get_status(k)})
                    if timechecker.gamecheck(k,activegames+pendinggames) == True:
                        if not game.get('final'):
                            check = edit.convert_tz(datetime.utcnow(),'bot')
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
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of stale posts failed, continuing..."
                                        stale_games.clear()
                                    if game.get('presub') and not game.get('gamesub'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying Game",k,"pregame thread..."
                                        try:
                                            game.get('presub').mod.sticky(state=False)
                                        except:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of pregame thread failed, continuing..."
                                if not game.get('gamesub') and not game.get('skipflag'):
                                    original_gametitle = None
                                    if game.get('status').get('abstractGameState') == 'Final':
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Detected Game",k,"is over. Checking for game thread with previous title (subtracting win/loss from team records)..."
                                        original_gametitle = edit.generate_title(k,'game',True)
                                    for submission in subreddit.new():
                                        if submission.title in [game.get('gametitle'), original_gametitle]:
                                            if submission.title == original_gametitle: game.update({'gametitle' : original_gametitle})
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"thread already posted, getting submission..."
                                            game.update({'gamesub' : submission, 'status' : edit.get_status(k)})
                                            threads[k].update({'game' : submission.selftext})
                                            break
                                    if game.get('gamesub'):
                                        if self.SETTINGS.get('STICKY'):
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                            try:
                                                game.get('gamesub').mod.sticky()
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                            except:
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of game thread failed (check mod privileges or the thread may have already been sticky), continuing..."
                                if not game.get('gamesub') and not game.get('skipflag'):
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting game thread for Game",k,"..."
                                    threads[k].update({'game' : edit.generate_thread_code("game",k)})
                                    if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP'): 
                                        lastupdate = "^^^Last ^^^Updated: ^^^" + edit.convert_tz(datetime.utcnow(),'bot').strftime("%m/%d/%Y ^^^%I:%M:%S ^^^%p ^^^%Z")
                                    else: lastupdate = ""
                                    threadtext = threads[k].get('game') + lastupdate
                                    game.update({'gamesub' : subreddit.submit(game.get('gametitle'), selftext=threadtext, send_replies=self.SETTINGS.get('GAME_THREAD').get('INBOX_REPLIES')), 'status' : edit.get_status(k)})
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Game thread submitted..."

                                    if self.SETTINGS.get('STICKY'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                        try:
                                            game.get('gamesub').mod.sticky()
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                        except:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of game thread failed (check mod privileges), continuing..."

                                    if self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT') != "":
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Setting suggested sort to " + self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT') + "..."
                                        try:
                                            game.get('gamesub').mod.suggested_sort(self.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT'))
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Suggested sort set..."
                                        except:
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on game thread failed (check mod privileges), continuing..."

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

                                    if self.SETTINGS.get('GAME_THREAD').get('TWITTER').get('ENABLED'):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Preparing to tweet link to game thread..."
                                        tweetText = edit.replace_params(self.SETTINGS.get('GAME_THREAD').get('TWITTER').get('TEXT').replace('{link}',game.get('gamesub').shortlink), 'game', 'tweet', k)
                                        twt.PostUpdate(tweetText)
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Tweet submitted..."

                                    game.update({'skipflag':True})
                                    sleeptime = 5 + self.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Sleeping for",sleeptime,"seconds..."
                                    time.sleep(sleeptime)
                            except Exception, err:
                                if self.SETTINGS.get('LOG_LEVEL')>0: print "Error while getting/posting game thread: ",err, ": continuing after 10 seconds..."
                                time.sleep(10)

                            check = edit.convert_tz(datetime.utcnow(),'bot')
                            if game.get('skipflag'): game.update({'skipflag':False})
                            else:
                                while True:
                                    statusCheck = edit.get_status(k)
                                    game.update({'status' : statusCheck})
                                    threadstr = edit.generate_thread_code("game",k)
                                    if threadstr != threads[k].get('game'):
                                        threads[k].update({'game' : threadstr})
                                        if self.SETTINGS.get('LOG_LEVEL')>2: print "Editing thread for Game",k,"..."
                                        while True:
                                            try:
                                                if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP'): threadstr += "^^^Last ^^^Updated: ^^^" + edit.convert_tz(datetime.utcnow(),'bot').strftime("%m/%d/%Y ^^^%I:%M:%S ^^^%p ^^^%Z")
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
                                    if (game.get('status').get('abstractGameState') == 'Final' or game.get('status').get('detailedState').startswith("Suspended")) and not (statusCheck.get('abstractGameState') == 'Final' or statusCheck.get('detailedState').startswith("Suspended")):
                                        if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Detected game ended final during last game thread update. Updating game thread one more time... "
                                        continue
                                    else: break

                            if game.get('status').get('abstractGameState') == 'Final' or game.get('status').get('detailedState').startswith("Suspended"):
                                game.update({'gameInfo' : edit.get_teams_time(pk=game.get('gamePk'),d=today.date())})
                                game.get('gameInfo').pop('status') #remove redundant status node (it won't be kept up-to-date anyway)
                                check = edit.convert_tz(datetime.utcnow(),'bot')
                                game.update({'final' : True})
                                if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Game",k,"Status:",game.get('status').get('abstractGameState'),"/",game.get('status').get('detailedState')
                                if self.SETTINGS.get('POST_THREAD').get('ENABLED'):
                                    try:
                                        myteamwon = edit.didmyteamwin(k)
                                        game.update({'posttitle' : edit.generate_title(k,"post",myteamwon)})
                                        subreddit = r.subreddit(self.SETTINGS.get('SUBREDDIT'))
                                        if self.SETTINGS.get('STICKY'):
                                            if game.get('presub'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying Game",k,"pregame thread..."
                                                try:
                                                    game.get('presub').mod.sticky(state=False)
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of pregame thread failed, continuing..."
                                            if game.get('gamesub'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Unstickying Game",k,"game thread..."
                                                try:
                                                    game.get('gamesub').mod.sticky(state=False)
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Unsticky of game thread failed, continuing..."
                                        if not game.get('postsub'):
                                            for submission in subreddit.new():
                                                if submission.title == game.get('posttitle'):
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Game",k,"postgame thread already posted, getting submission..."
                                                    game.update({'postsub' : submission})
                                                    if self.SETTINGS.get('STICKY'):
                                                        if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                                        try:
                                                            game.get('postsub').mod.sticky()
                                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                                        except:
                                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of postgame thread failed (check mod privileges or the thread may have already been sticky), continuing..."
                                                    break
                                        if not game.get('postsub'):
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Submitting postgame thread for Game",k,"..."
                                            game.update({'postsub' : subreddit.submit(game.get('posttitle'), selftext=edit.generate_thread_code("post",k), send_replies=self.SETTINGS.get('POST_THREAD').get('INBOX_REPLIES'))})
                                            if self.SETTINGS.get('LOG_LEVEL')>1: print "Postgame thread submitted..."

                                            if self.SETTINGS.get('STICKY'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Stickying submission..."
                                                try:
                                                    game.get('postsub').mod.sticky()
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Submission stickied..."
                                                except:
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Sticky of postgame thread failed (check mod privileges), continuing..."

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
                                                    if self.SETTINGS.get('LOG_LEVEL')>1: print "WARNING: Setting suggested sort on postgame thread failed (check mod privileges), continuing..."

                                            if self.SETTINGS.get('POST_THREAD').get('TWITTER').get('ENABLED'):
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Preparing to tweet link to postgame thread..."
                                                if myteamwon=="1": winLossOther = "WIN"
                                                elif myteamwon=="0": winLossOther = "LOSS"
                                                else: winLossOther = "OTHER"
                                                tweetText = edit.replace_params(self.SETTINGS.get('POST_THREAD').get('TWITTER').get(winLossOther+"_TEXT").replace('{link}',game.get('postsub').shortlink), 'post', 'tweet', k)
                                                twt.PostUpdate(tweetText)
                                                if self.SETTINGS.get('LOG_LEVEL')>1: print "Tweet submitted..."

                                            if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Sleeping for 5 seconds..."
                                            time.sleep(5)
                                    except Exception, err:
                                        if self.SETTINGS.get('LOG_LEVEL')>0: print "Error while posting postgame thread:",err, ": continuing after 15 seconds..."
                                        time.sleep(15)
                                elif not self.SETTINGS.get('POST_THREAD').get('ENABLED') and len(self.games):
                                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Postgame thread disabled..."
                        else: 
                            if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Game",k,"final or postponed, nothing to do... "
                check = edit.convert_tz(datetime.utcnow(),'bot')
                activegames=0
                pendinggames=0
                previewgames=0
                completedgames=0
                delayedgames=0
                for sk,sgame in self.games.items():
                    if sgame.get('gamesub') and not sgame.get('final'):
                        activegames += 1
                        if sgame.get('status').get('abstractGameState') == 'Preview' and not sgame.get('status').get('detailedState').startswith("Delayed"):
                            previewgames += 1
                        if sgame.get('status').get('detailedState').startswith('Delayed'):
                            delayedgames += 1
                    elif not sgame.get('gamesub') and not sgame.get('final'):
                        pendinggames += 1
                    elif sgame.get('final'):
                        completedgames += 1

                if self.SETTINGS.get('LOG_LEVEL')>3: print "threads:",threads
                if len(offday):
                    if self.SETTINGS.get('LOG_LEVEL')>3: print "offday:",offday
                if self.SETTINGS.get('LOG_LEVEL')>3: print "self.games:",self.games
                limits = r.auth.limits
                if limits.get('used') > maxapi: maxapi = limits.get('used')
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Reddit API Calls:",limits,"- Max usage today:",maxapi
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Active Games:",activegames,"...in Preview Status:",previewgames,"...in Delayed Status:",delayedgames,"- Pending Games:",pendinggames,"- Completed Games:",completedgames

                if activegames == 0 and pendinggames == 0:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "All games final for today, going into end of day loop... "
                    break
                elif pendinggames > 0 and activegames == 0:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"No game threads to post yet, sleeping for 10 minutes... "
                    time.sleep(600)
                elif activegames > 0 and previewgames == activegames:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"All posted games are in Preview status, sleeping for 5 minutes... "
                    time.sleep(300)
                elif activegames > 0 and (delayedgames + previewgames) == activegames:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"All posted games are in Preview or Delayed status, sleeping for 1 minute... "
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
