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
from logger import Logger
from config import Config

class Bot:

    def __init__(self, settings_file):
        self.VERSION = '5.1.8'
        self.games = games.Games().games
        self.editStats = {}
        self.editStatHistory = []
        self.settings_file = settings_file

    def run(self):
        logger = Logger({'CONSOLE': True, 'CONSOLE_LOG_LEVEL': 'INFO', 'FILE': True, 'FILE_LOG_LEVEL': 'DEBUG'},'startup')
        conf = Config(self.settings_file)
        edit = None
        myteam={}
        timechecker = None

        stale_games = {}
        offday = {}
        weekly = {}
        threads = {}
        offseason = False
        UA = None
        refresh_token = None
        r = None

        while True:
            if not edit: logger.info("Loading settings from file [%s] and validating, see /logs/startup.log for debug log...",self.settings_file)
            else:
                logger.debug("Clearing team info cache...")
                edit.TEAMINFO.clear() #clear team info cache daily to keep data fresh
                logger.info("Reloading settings from file [%s] and validating...",self.settings_file)
            (logger,conf,edit,myteam,timechecker) = self.update_settings(logger,conf,edit,myteam,timechecker)
            if (conf.SETTINGS['OFF_THREAD']['ENABLED'] and conf.SETTINGS['OFF_THREAD']['TWITTER']['ENABLED']) or (conf.SETTINGS['PRE_THREAD']['ENABLED'] and conf.SETTINGS['PRE_THREAD']['TWITTER']['ENABLED']) or (conf.SETTINGS['GAME_THREAD']['TWITTER']['ENABLED']) or (conf.SETTINGS['POST_THREAD']['ENABLED'] and conf.SETTINGS['POST_THREAD']['TWITTER']['ENABLED']):
                try:
                    if 'twitter' not in sys.modules: import twitter
                except:
                    logger.error('Unable to import python-twitter module. Please ensure it is installed. Disabling Twitter features...')
                    conf.SETTINGS['TWITTER'].update({'CONSUMER_KEY' : '', 'CONSUMER_SECRET' : '', 'ACCESS_TOKEN' : '', 'ACCESS_SECRET' : ''})
                    conf.validate_all(settings=conf.SETTINGS, config={'TWITTER':conf.SETTINGS_CONFIG.get('TWITTER')})
                else:
                    logger.info("Initiating Twitter instance...")
                    twt = twitter.Api(conf.SETTINGS.get('TWITTER').get('CONSUMER_KEY'),
                                           conf.SETTINGS.get('TWITTER').get('CONSUMER_SECRET'),
                                           conf.SETTINGS.get('TWITTER').get('ACCESS_TOKEN'),
                                           conf.SETTINGS.get('TWITTER').get('ACCESS_SECRET'))
                    logger.info("Twitter authorized user: %s",twt.VerifyCredentials().screen_name)

            if conf.SETTINGS['NOTIFICATIONS']['PROWL']['ENABLED']:
                logger.info("Setting up Prowl notifications...")
                if 'pyprowl' not in sys.modules: import pyprowl
                prowl = pyprowl.Prowl(conf.SETTINGS['NOTIFICATIONS']['PROWL']['API_KEY'], myteam.get('name') + " Reddit Bot")
                try:
                    verifyKey = prowl.verify_key()
                    logger.info("Successfully validated Prowl API key...")
                except Exception, e:
                    logger.error("Could not validate Prowl API key, disabling Prowl notifications. Response: %s",e)
                    conf.SETTINGS['NOTIFICATIONS']['PROWL'].update({'ENABLED':False})

            if not r or refresh_token != conf.SETTINGS.get('REFRESH_TOKEN') or UA != 'OAuth Baseball Game Thread Bot for Reddit v' + self.VERSION + ' https://github.com/toddrob99/Baseball-GDT-Bot ' + conf.SETTINGS.get('USER_AGENT'):
                UA = 'OAuth Baseball Game Thread Bot for Reddit v' + self.VERSION + ' https://github.com/toddrob99/Baseball-GDT-Bot ' + conf.SETTINGS.get('USER_AGENT')
                refresh_token=conf.SETTINGS.get('REFRESH_TOKEN')
                logger.debug("Initiating PRAW instance with User Agent: %s",UA)
                r = praw.Reddit(client_id=conf.SETTINGS.get('CLIENT_ID'),
                                client_secret=conf.SETTINGS.get('CLIENT_SECRET'),
                                refresh_token=conf.SETTINGS.get('REFRESH_TOKEN'),
                                user_agent=UA)
                scopes = ['identity', 'submit', 'edit', 'read', 'modposts', 'privatemessages', 'flair', 'modflair']
                praw_scopes = r.auth.scopes()
                missing_scopes = []
                logger.debug("Reddit authorized scopes: %s",praw_scopes)
                if 'identity' in praw_scopes:
                    logger.info("Reddit authorized user: %s",r.user.me())
                for scope in scopes:
                    if scope not in praw_scopes:
                        missing_scopes.append(scope)
                if len(missing_scopes):
                    logger.warn("%s scope(s) not authorized. Please re-run setup-oauth.py to update scopes for your bot user. See instructions in README.md.",missing_scopes)

            if len(offday):
                logger.info("Marking yesterday's offday thread as stale...")
                stale_games[0] = offday
            else:
                if len(self.games)>0:
                    logger.info("Marking yesterday's threads as stale...")
                    stale_games = self.games.copy()
            if conf.SETTINGS.get('STICKY') and len(stale_games)==0:
                dateformats = ["%B %d, %Y"]
                if conf.SETTINGS.get('OFF_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('OFF_THREAD').get('TITLE')[conf.SETTINGS.get('OFF_THREAD').get('TITLE').find('{date:')+6:conf.SETTINGS.get('OFF_THREAD').get('TITLE').find('}',conf.SETTINGS.get('OFF_THREAD').get('TITLE').find('{date:'))])
                if conf.SETTINGS.get('PRE_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('PRE_THREAD').get('TITLE')[conf.SETTINGS.get('PRE_THREAD').get('TITLE').find('{date:')+6:conf.SETTINGS.get('PRE_THREAD').get('TITLE').find('}',conf.SETTINGS.get('PRE_THREAD').get('TITLE').find('{date:'))])
                if conf.SETTINGS.get('GAME_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('GAME_THREAD').get('TITLE')[conf.SETTINGS.get('GAME_THREAD').get('TITLE').find('{date:')+6:conf.SETTINGS.get('GAME_THREAD').get('TITLE').find('}',conf.SETTINGS.get('GAME_THREAD').get('TITLE').find('{date:'))])
                if conf.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('POST_THREAD').get('WIN_TITLE')[conf.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('{date:')+6:conf.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('}',conf.SETTINGS.get('POST_THREAD').get('WIN_TITLE').find('{date:'))])
                if conf.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('POST_THREAD').get('LOSS_TITLE')[conf.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('{date:')+6:conf.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('}',conf.SETTINGS.get('POST_THREAD').get('LOSS_TITLE').find('{date:'))])
                if conf.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('POST_THREAD').get('OTHER_TITLE')[conf.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('{date:')+6:conf.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('}',conf.SETTINGS.get('POST_THREAD').get('OTHER_TITLE').find('{date:'))])
                if conf.SETTINGS.get('WEEKLY_THREAD').get('TITLE').find('{date:') > -1:
                    dateformats.append(conf.SETTINGS.get('WEEKLY_THREAD').get('TITLE')[conf.SETTINGS.get('WEEKLY_THREAD').get('TITLE').find('{date:')+6:conf.SETTINGS.get('WEEKLY_THREAD').get('TITLE').find('}',conf.SETTINGS.get('WEEKLY_THREAD').get('TITLE').find('{date:'))])
                dateformats = list(set(dateformats))
                datestocheck = []
                for f in dateformats:
                    datestocheck.append(datetime.strftime(datetime.now(),f.replace('%I:%M %p','').replace('%I:%M%p','').replace('%I:%M','').replace(' @ ','').replace('  ',' ')).rstrip())
                try:
                    sticky1 = r.subreddit(conf.SETTINGS.get('SUBREDDIT')).sticky(1)
                    if sticky1.author == r.user.me() and not any(f in sticky1.title for f in datestocheck):
                        stale_games[len(stale_games)] = {'gamesub' : sticky1, 'gametitle' : sticky1.title}
                        logger.warn("Found stale thread in top sticky slot (%s)...",sticky1.title)
                    sticky2 = r.subreddit(conf.SETTINGS.get('SUBREDDIT')).sticky(2)
                    if sticky2.author == r.user.me() and not any(f in sticky2.title for f in datestocheck):
                        stale_games[len(stale_games)] = {'gamesub' : sticky2, 'gametitle' : sticky2.title}
                        logger.warn("Found stale thread in bottom sticky slot (%s)...",sticky2.title)
                except:
                    pass
            logger.debug("Stale games: %s",stale_games)

            today = datetime.today()
            #today = datetime.strptime('2018-04-06','%Y-%m-%d') # leave commented unless testing

            logger.debug("Clearing api cache...")
            edit.gamesLive.clear() #clear api cache daily to keep memory usage down
            logger.debug("Clearing daily game thread edit stats...")
            self.editStats.clear() #clear edit timestamps daily to keep memory usage down
            logger.debug("Clearing game comment history...")
            edit.gamesComments.clear() #clear game comment history daily to keep memory usage down

            todaygames = edit.get_schedule(today)#,myteam.get('team_id'))

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
                    elif todaygame.get('teams').get('home').get('team').get('id') in [159,160] and todaygame.get('teams').get('away').get('team').get('id') in [159,160]:
                        if conf.SETTINGS.get('ASG'):
                            logger.info("Detected All Star Game...")
                            todaygame.update({'ASG':True})
                            homeaway = 'home' if myteam.get('league_id') == edit.lookup_team_info('league_id','team_id',str(todaygame.get('teams').get('home').get('team').get('id'))) else 'away'
                        else:
                            logger.info("Detected All Star Game, but ASG threads are disabled. Ignoring...")
                    if homeaway != None:
                        logger.debug("Found game %s: %s",str(i),todaygame)
                        self.games[i] = todaygame
                        self.games[i].update({'homeaway' : homeaway, 'final' : False, 'skipflag' : False})
                        if todaygame.get('doubleHeader') != 'N':
                            self.games[i].update({'doubleheader' : True})
                            if todaygame.get('doubleHeader') == "S": dhtype = 'split'
                            if todaygame.get('doubleHeader') == "Y": dhtype = 'straight'
                            logger.info("Game %s detected as %s doubleheader game %s...", str(i), dhtype, str(todaygame.get('gameNumber')))
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
                        logger.debug("Legacy data directory for Game %s: %s",str(i), self.games[i].get('url'))
                        self.games[i].update({'gameInfo' : edit.get_teams_time(pk=self.games[i].get('gamePk'),d=today.date()), 'atBatIndex':edit.get_latest_atBatIndex(i)})
                        self.games[i].get('gameInfo').pop('status') #remove redundant status node (it won't be kept up-to-date anyway)
                        threads[i] = {'game' : '', 'post' : '', 'pre' : ''}
                        self.editStats.update({i: {'checked' : [], 'edited' : [], 'commented' : []}})
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
                                    logger.debug("Game %s other doubleheader game found, game id: %s...", str(a), str(b))
                        else: self.games[a].update({'othergame' : 0})
            logger.debug("Today's games: %s",self.games)
            pendinggames = len(self.games)

            if len(self.games) == 0:
                next_game = edit.next_game(30,team_id=myteam.get('team_id'))
                if next_game.get('days_away')==None:
                    logger.info("No games in the next 30 days. It's the off season...")
                    offseason = True
                elif next_game.get('days_away') > 14:
                    logger.info("Next game is %s days away. It's the off season...", next_game.get('days_away'))
                    offseason = True
                elif next_game.get('days_away') <= 14:
                    last_game = edit.last_game(14,myteam.get('team_id'))
                    if not last_game.get('days_ago'):
                        logger.info("Next game is %s day(s) away, but no games in the last 14 days. It's the off season...", next_game.get('days_away'))
                        offseason = True
                    else:
                        logger.info("No games today...")
                        offseason = False
                else:
                    logger.info("No games today...")
                    offseason = False

            if conf.SETTINGS.get('WEEKLY_THREAD').get('ENABLED') and ((offseason and conf.SETTINGS.get('WEEKLY_THREAD').get('OFFSEASON_ONLY')) or not conf.SETTINGS.get('WEEKLY_THREAD').get('OFFSEASON_ONLY')):
                try:
                    weekly.update({'weeklytitle': edit.generate_title(0,"weekly",usedate=timechecker.dateoflastweekly()), 'weeklymessage' : edit.generate_thread_code('weekly',0,offseason=offseason)})
                    subreddit = r.subreddit(conf.SETTINGS.get('SUBREDDIT'))
                    if not weekly.get('weeklysub'):
                        for submission in subreddit.new():
                            if submission.title == weekly.get('weeklytitle') and timechecker.iscurrent('weekly',submission.created_utc,6):
                                logger.info("Found a weekly thread with matching title posted within the last 6 days, getting submission...")
                                weekly.update({'weeklysub' : submission})
                                if len(stale_games):
                                    for stk,stg in stale_games.items():
                                        if stg.get('weeklysub') == weekly.get('weeklysub') or stg.get('gamesub') == weekly.get('weeklysub'):
                                            logger.info("Weekly thread was marked as stale, marking as active again...")
                                            stale_games.pop(stk)
                                            logger.debug("stale_games: %s",stale_games)
                                if conf.SETTINGS.get('STICKY'):
                                    logger.info("Stickying submission...")
                                    try:
                                        weekly.get('weeklysub').mod.sticky()
                                        logger.info("Submission stickied...")
                                    except:
                                        logger.warn("Sticky of weekly thread failed (check mod privileges or the thread may have already been sticky), continuing...")
                                break
                        if not weekly.get('weeklysub'):
                            logger.info("No existing weekly thread found.")

                    if timechecker.weeklycheck():
                        if weekly.get('weeklysub') and weekly.get('weeklysub').title != weekly.get('weeklytitle'):
                            logger.info("Marking previous weekly thread as stale...")
                            stale_games[len(stale_games)] = {'weeklysub' : weekly.get('weeklysub'), 'gametitle' : weekly.get('weeklysub').title}
                            weekly.pop('weeklysub')

                        if not weekly.get('weeklysub'):
                            if conf.SETTINGS.get('STICKY') and len(stale_games):
                                logger.info("Unstickying stale threads...")
                                try:
                                    for stale_k,stale_game in stale_games.items():
                                        if stale_game.get('offsub') and offseason and conf.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON'):
                                            stale_game.get('offsub').mod.sticky(state=False)
                                            stale_games.pop(stale_k)
                                            continue
                                        if stale_game.get('presub') and offseason:
                                            stale_game.get('presub').mod.sticky(state=False)
                                            stale_games.pop(stale_k)
                                            continue
                                        if stale_game.get('gamesub') and offseason:
                                            stale_game.get('gamesub').mod.sticky(state=False)
                                            stale_games.pop(stale_k)
                                            continue
                                        if stale_game.get('postsub') and offseason:
                                            stale_game.get('postsub').mod.sticky(state=False)
                                            stale_games.pop(stale_k)
                                            continue
                                        if stale_game.get('weeklysub'):
                                            stale_game.get('weeklysub').mod.sticky(state=False)
                                            stale_games.pop(stale_k)
                                            continue
                                    logger.debug("stale_games: %s",stale_games)
                                except Exception, err:
                                    logger.error("Unsticky of stale posts failed, continuing...")

                            logger.info("Submitting weekly thread...")
                            weekly.update({'weeklysub' : subreddit.submit(weekly.get('weeklytitle'), selftext=weekly.get('weeklymessage'), send_replies=conf.SETTINGS.get('WEEKLY_THREAD').get('INBOX_REPLIES'))})
                            logger.info("Weekly thread submitted...")

                            if conf.SETTINGS.get('STICKY'):
                                logger.info("Stickying submission...")
                                try:
                                    weekly.get('weeklysub').mod.sticky()
                                    logger.info("Submission stickied...")
                                except:
                                    logger.warn("Sticky of weekly thread failed (check mod privileges or the thread may have already been sticky), continuing...")

                            if conf.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                if conf.SETTINGS.get('WEEKLY_THREAD').get('FLAIR') == "":
                                    logger.error("FLAIR_MODE = submitter, but WEEKLY_THREAD : FLAIR is blank...")
                                else:
                                    logger.info("Adding flair to submission as submitter...")
                                    choices = weekly.get('weeklysub').flair.choices()
                                    flairsuccess = False
                                    for p in choices:
                                        if p['flair_text'] == conf.SETTINGS.get('WEEKLY_THREAD').get('FLAIR'):
                                            weekly.get('weeklysub').flair.select(p['flair_template_id'])
                                            flairsuccess = True
                                    if flairsuccess:
                                        logger.info("Submission flaired...")
                                    else: 
                                        logger.error("Flair not set: could not find flair in available choices")
                            elif conf.SETTINGS.get('FLAIR_MODE') == 'mod':
                                if conf.SETTINGS.get('WEEKLY_THREAD').get('FLAIR') == "":
                                    logger.error("FLAIR_MODE = mod, but WEEKLY_THREAD : FLAIR is blank...")
                                else:
                                    logger.info("Adding flair to submission as mod...")
                                    try:
                                        weekly.get('weeklysub').mod.flair(conf.SETTINGS.get('WEEKLY_THREAD').get('FLAIR'))
                                        logger.info("Submission flaired...")
                                    except:
                                        logger.error("Failed to set flair (check mod privileges or change FLAIR_MODE to submitter), continuing...")

                            if conf.SETTINGS.get('WEEKLY_THREAD').get('SUGGESTED_SORT') != "":
                                logger.info("Setting suggested sort to %s...",conf.SETTINGS.get('WEEKLY_THREAD').get('SUGGESTED_SORT'))
                                try:
                                    weekly.get('weeklysub').mod.suggested_sort(conf.SETTINGS.get('WEEKLY_THREAD').get('SUGGESTED_SORT'))
                                    logger.info("Suggested sort set...")
                                except:
                                    logger.error("Setting suggested sort on weekly thread failed (check mod privileges), continuing...")

                            if conf.SETTINGS.get('WEEKLY_THREAD').get('TWITTER').get('ENABLED'):
                                logger.info("Preparing to tweet link to weekly thread...")
                                tweetText = edit.replace_params(conf.SETTINGS.get('WEEKLY_THREAD').get('TWITTER').get('TEXT').replace('{link}',weekly.get('weeklysub').shortlink), 'weekly', 'tweet')
                                twt.PostUpdate(tweetText)
                                logger.info("Tweet submitted...")

                            if conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('ENABLED') and conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('NOTIFY_WHEN').get('WEEKLY_THREAD_SUBMITTED'):
                                logger.info("Sending Prowl notification...")
                                event = myteam.get('name') + ' Weekly Thread Posted'
                                description = myteam.get('name') + ' weekly thread was posted to r/'+conf.SETTINGS.get('SUBREDDIT')+' at '+edit.convert_tz(datetime.utcnow(),'bot').strftime('%I:%M %p %Z')+'.\nThread title: '+weekly.get('weeklytitle')+'\nURL: '+weekly.get('weeklysub').shortlink
                                try:
                                    prowlResult = prowl.notify(event, description, conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('PRIORITY'), weekly.get('weeklysub').shortlink)
                                    logger.info("Successfully sent notification to Prowl...")
                                except Exception, e:
                                    logger.error("Failed to send notification to Prowl... Event: %s, Description: %s, Response: %s", event, description, e)

                            logger.info("Finished posting weekly thread, sleeping for 5 seconds and then checking if anything else is needed...")
                            time.sleep(5)
                    elif not weekly.get('weeklysub'):
                        logger.info("It's not time to post the weekly thread...")
                except Exception, err:
                    logger.info("Error posting weekly thread, continuing: %s",err)

            if conf.SETTINGS.get('OFF_THREAD').get('ENABLED') and len(self.games) == 0 and not (offseason and conf.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON')):
                timechecker.pregamecheck(conf.SETTINGS.get('OFF_THREAD').get('TIME'))
                offday.update({'offtitle': edit.generate_title(0,"off"), 'offmessage' : edit.generate_thread_code('off',0,nextgame=next_game,offseason=offseason)})
                try:
                    subreddit = r.subreddit(conf.SETTINGS.get('SUBREDDIT'))
                    for submission in subreddit.new():
                        if submission.title == offday.get('offtitle'):
                            logger.info("Offday thread already posted, getting submission...")
                            offday.update({'offsub' : submission})
                            if conf.SETTINGS.get('STICKY'):
                                logger.info("Stickying submission...")
                                try:
                                    offday.get('offsub').mod.sticky()
                                    logger.info("Submission stickied...")
                                except:
                                    logger.warn("Sticky of offday thread failed (check mod privileges or the thread may have already been sticky), continuing...")
                            logger.info("Finished posting offday thread, going into end of day loop...")
                            break

                    if not offday.get('offsub'):
                        if conf.SETTINGS.get('STICKY') and len(stale_games):
                            logger.info("Unstickying stale threads...")
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
                                logger.error("Unsticky of stale posts failed, continuing...")
                            stale_games.clear()

                        logger.info("Submitting offday thread...")
                        offday.update({'offsub' : subreddit.submit(offday.get('offtitle'), selftext=offday.get('offmessage'), send_replies=conf.SETTINGS.get('OFF_THREAD').get('INBOX_REPLIES'))})
                        logger.info("Offday thread submitted...")

                        if conf.SETTINGS.get('STICKY'):
                            logger.info("Stickying submission...")
                            try:
                                offday.get('offsub').mod.sticky()
                                logger.info("Submission stickied...")
                            except:
                                logger.error("Sticky of offday thread failed (check mod privileges), continuing...")

                        if conf.SETTINGS.get('FLAIR_MODE') == 'submitter':
                            if conf.SETTINGS.get('OFF_THREAD').get('FLAIR') == "":
                                logger.error("FLAIR_MODE = submitter, but OFF_THREAD : FLAIR is blank...")
                            else:
                                logger.info("Adding flair to submission as submitter...")
                                choices = offday.get('offsub').flair.choices()
                                flairsuccess = False
                                for p in choices:
                                    if p['flair_text'] == conf.SETTINGS.get('OFF_THREAD').get('FLAIR'):
                                        offday.get('offsub').flair.select(p['flair_template_id'])
                                        flairsuccess = True
                                if flairsuccess:
                                    logger.info("Submission flaired...")
                                else: 
                                    logger.error("Flair not set: could not find flair in available choices")
                        elif conf.SETTINGS.get('FLAIR_MODE') == 'mod':
                            if conf.SETTINGS.get('OFF_THREAD').get('FLAIR') == "":
                                logger.error("FLAIR_MODE = mod, but OFF_THREAD : FLAIR is blank...")
                            else:
                                logger.info("Adding flair to submission as mod...")
                                try:
                                    offday.get('offsub').mod.flair(conf.SETTINGS.get('OFF_THREAD').get('FLAIR'))
                                    logger.info("Submission flaired...")
                                except:
                                    logger.error("Failed to set flair (check mod privileges or change FLAIR_MODE to submitter), continuing...")

                        if conf.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT') != "":
                            logger.info("Setting suggested sort to %s...",conf.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT'))
                            try:
                                offday.get('offsub').mod.suggested_sort(conf.SETTINGS.get('OFF_THREAD').get('SUGGESTED_SORT'))
                                logger.info("Suggested sort set...")
                            except:
                                logger.error("Setting suggested sort on offday thread failed (check mod privileges), continuing...")

                        if conf.SETTINGS.get('OFF_THREAD').get('TWITTER').get('ENABLED'):
                            logger.info("Preparing to tweet link to off day thread...")
                            tweetText = edit.replace_params(conf.SETTINGS.get('OFF_THREAD').get('TWITTER').get('TEXT').replace('{link}',offday.get('offsub').shortlink), 'off', 'tweet')
                            twt.PostUpdate(tweetText)
                            logger.info("Tweet submitted...")

                        if conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('ENABLED') and conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('NOTIFY_WHEN').get('OFF_THREAD_SUBMITTED'):
                            logger.info("Sending Prowl notification...")
                            event = myteam.get('name') + ' Off Day Thread Posted'
                            description = myteam.get('name') + ' off day thread was posted to r/'+conf.SETTINGS.get('SUBREDDIT')+' at '+edit.convert_tz(datetime.utcnow(),'bot').strftime('%I:%M %p %Z')+'.\nThread title: '+offday.get('offtitle')+'\nURL: '+offday.get('offsub').shortlink
                            try:
                                prowlResult = prowl.notify(event, description, conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('PRIORITY'), offday.get('offsub').shortlink)
                                logger.info("Successfully sent notification to Prowl...")
                            except Exception, e:
                                logger.error("Failed to send notification to Prowl... Event: %s, Description: %s, Response: %s", event, description, e)

                        logger.info("Finished posting offday thread, going into end of day loop...")
                except Exception, err:
                    logger.info("Error posting off day thread, going into end of day loop: %s",err)
            elif not conf.SETTINGS.get('OFF_THREAD').get('ENABLED') and len(self.games) == 0:
                logger.info("Off day detected, but off day thread disabled. Going into end of day loop...")
            elif offseason and conf.SETTINGS.get('OFF_THREAD').get('SUPPRESS_OFFSEASON') and len(self.games) == 0:
                logger.info("Suppressing off day thread during off season, going into end of day loop...")

            if conf.SETTINGS.get('PRE_THREAD').get('ENABLED') and len(self.games) > 0:
                timechecker.pregamecheck(conf.SETTINGS.get('PRE_THREAD').get('TIME'))
                for k,game in self.games.items():
                    logger.info("Retrieving updated game info for Game %s...",k)
                    game.update({'gameInfo' : edit.get_teams_time(pk=game.get('gamePk'),d=today.date())})
                    game.get('gameInfo').pop('status') #remove redundant status node (it won't be kept up-to-date anyway)
                    logger.info("Preparing to post pregame thread for Game %s...",k)
                    game.update({'pretitle': edit.generate_title(k,"pre")})
                    while True:
                        try:
                            subreddit = r.subreddit(conf.SETTINGS.get('SUBREDDIT'))
                            if conf.SETTINGS.get('STICKY') and len(stale_games):
                                logger.info("Unstickying stale threads...")
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
                                    logger.error("Unsticky of stale posts failed, continuing...")
                                stale_games.clear()
                            if conf.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and game.get('doubleheader'):
                                if game.get('presub'):
                                    logger.info("Consolidated pregame thread already posted and linked to this game...")
                                    break
                                if not game.get('presub') and self.games[game.get('othergame')].get('presub'):
                                    logger.info("Linking this game to existing consolidated pregame thread from doubleheader game %s...",game.get('othergame'))
                                    game.update({'presub' : self.games[game.get('othergame')].get('presub')})
                                    break
                            original_pretitle = None
                            if game.get('status').get('abstractGameState') == 'Final':
                                logger.info("Detected Game %s is over. Checking for pre thread with previous title (subtracting win/loss from team records)...",k)
                                original_pretitle = edit.generate_title(k,"pre",True)

                            for submission in subreddit.new():
                                if submission.title in [game.get('pretitle'), original_pretitle]:
                                    if submission.title == original_pretitle: game.update({'pretitle' : original_pretitle})
                                    if game.get('doubleheader') and conf.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'):
                                        logger.info("Game %s consolidated doubleheader pregame thread already posted, submitting edits...",k)
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_thread_code('pre',k,game.get('othergame')))
                                        logger.info("Edits submitted. Sleeping for 5 seconds...")
                                        game.update({'presub' : submission})
                                    else:
                                        logger.info("Game %s pregame thread already posted, submitting edits...",k)
                                        game.update({'presub' : submission})
                                        game.get('presub').edit(edit.generate_thread_code('pre',k))
                                        logger.info("Edits submitted. Sleeping for 5 seconds...")
                                        if conf.SETTINGS.get('STICKY'):
                                            logger.info("Stickying submission...")
                                            try:
                                                game.get('presub').mod.sticky()
                                                logger.info("Submission stickied...")
                                            except:
                                                logger.error("Sticky of pregame thread failed (check mod privileges or the thread may have already been sticky), continuing...")
                                    time.sleep(5)
                                    break
                            if not game.get('presub'):
                                if conf.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES')>=0:
                                    time_to_post = timechecker.gamecheck(k,just_get_time=True)
                                    minutes_until_post_time = int((time_to_post-edit.convert_tz(datetime.utcnow(),'bot')).total_seconds() / 60)
                                    logger.debug("Minutes until game thread post time: %s",minutes_until_post_time)
                                    if minutes_until_post_time <= conf.SETTINGS.get('PRE_THREAD').get('SUPPRESS_MINUTES'):
                                        logger.info("Suppressing pregame thread for Game %s because game thread will be posted soon...",k)
                                        game.update({'presub_suppressed':True})
                                        break
                                    elif game.get('doubleheader') and conf.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and self.games[game.get('othergame')].get('presub_suppressed'):
                                        logger.info("Suppressing pregame thread for Game %s because consolidated pregame threads are enabled and Game %s thread will be posted soon...",k,game.get('othergame'))
                                        game.update({'presub_suppressed':True})
                                        break
                                logger.info("Submitting pregame thread for Game %s...",k)
                                game.update({'presub' : subreddit.submit(game.get('pretitle'), selftext=edit.generate_thread_code('pre',k,game.get('othergame')), send_replies=conf.SETTINGS.get('PRE_THREAD').get('INBOX_REPLIES'))})
                                logger.info("Pregame thread submitted...")
                                if conf.SETTINGS.get('STICKY'):
                                    logger.info("Stickying submission...")
                                    try:
                                        game.get('presub').mod.sticky()
                                        logger.info("Submission stickied...")
                                    except:
                                        logger.error("Sticky of pregame thread failed (check mod privileges), continuing...")

                                if conf.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                    if conf.SETTINGS.get('PRE_THREAD').get('FLAIR') == "":
                                        logger.error("FLAIR_MODE = submitter, but PRE_THREAD : FLAIR is blank...")
                                    else:
                                        logger.info("Adding flair to submission as submitter...")
                                        choices = game.get('presub').flair.choices()
                                        flairsuccess = False
                                        for p in choices:
                                            if p['flair_text'] == conf.SETTINGS.get('PRE_THREAD').get('FLAIR'):
                                                game.get('presub').flair.select(p['flair_template_id'])
                                                flairsuccess = True
                                        if flairsuccess:
                                            logger.info("Submission flaired...")
                                        else:
                                            logger.error("Flair not set: could not find flair in available choices")
                                elif conf.SETTINGS.get('FLAIR_MODE') == 'mod':
                                    if conf.SETTINGS.get('PRE_THREAD').get('FLAIR') == "":
                                        logger.error("FLAIR_MODE = mod, but PRE_THREAD : FLAIR is blank...")
                                    else:
                                        logger.info("Adding flair to submission as mod...")
                                        try:
                                            game.get('presub').mod.flair(conf.SETTINGS.get('PRE_THREAD').get('FLAIR'))
                                            logger.info("Submission flaired...")
                                        except:
                                            logger.error("Failed to set flair (check mod privileges or change FLAIR_MODE to submitter), continuing...")

                                if conf.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT') != "":
                                    logger.info("Setting suggested sort to %s...", conf.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT'))
                                    try:
                                        game.get('presub').mod.suggested_sort(conf.SETTINGS.get('PRE_THREAD').get('SUGGESTED_SORT'))
                                        logger.info("Suggested sort set...")
                                    except:
                                        logger.error("Setting suggested sort on pregame thread failed (check mod privileges), continuing...")

                                if conf.SETTINGS.get('PRE_THREAD').get('TWITTER').get('ENABLED'):
                                    logger.info("Preparing to tweet link to pregame thread...")
                                    if game.get('doubleheader') and conf.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'):
                                        tweetText = edit.replace_params(conf.SETTINGS.get('PRE_THREAD').get('TWITTER').get('CONSOLIDATED_DH_TEXT').replace('{link}',game.get('presub').shortlink), 'pre', 'tweet', k)
                                    elif game.get('ASG'):
                                        tweetText = edit.replace_params(conf.SETTINGS.get('PRE_THREAD').get('TWITTER').get('ASG_TEXT').replace('{link}',game.get('presub').shortlink), 'pre', 'tweet', k)
                                    else: tweetText = edit.replace_params(conf.SETTINGS.get('PRE_THREAD').get('TWITTER').get('TEXT').replace('{link}',game.get('presub').shortlink), 'pre', 'tweet', k)
                                    twt.PostUpdate(tweetText)
                                    logger.info("Tweet submitted...")

                                if conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('ENABLED') and conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('NOTIFY_WHEN').get('PRE_THREAD_SUBMITTED'):
                                    logger.info("Sending Prowl notification...")
                                    if game.get('homeaway') == 'home':
                                        vsat = game.get('gameInfo').get('home').get('team_name') + ' vs. ' + game.get('gameInfo').get('away').get('team_name')
                                    else:
                                        vsat = game.get('gameInfo').get('away').get('team_name') + ' @ ' + game.get('gameInfo').get('home').get('team_name')
                                    event = myteam.get('name') + ' Pregame Thread Posted'
                                    if game.get('doubleheader') and not conf.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'): event += ' - DH Game ' + str(game.get('gameNumber'))
                                    description = 'Pregame thread posted to r/'+conf.SETTINGS.get('SUBREDDIT')+' at '+edit.convert_tz(datetime.utcnow(),'bot').strftime('%I:%M %p %Z')+':\n' +\
                                                    vsat+'\n' +\
                                                    'First Pitch: '+game.get('gameInfo').get('date_object').strftime('%I:%M %p %Z')+'\n' +\
                                                    'Thread title: '+game.get('pretitle')+'\n' +\
                                                    'URL: '+game.get('presub').shortlink
                                    try:
                                        prowlResult = prowl.notify(event, description, conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('PRIORITY'), game.get('presub').shortlink)
                                        logger.info("Successfully sent notification to Prowl...")
                                    except Exception, e:
                                        logger.error("Failed to send notification to Prowl... Event: %s, Description: %s, Response: %s", event, description, e)

                                logger.info("Sleeping for 5 seconds...")
                                time.sleep(5)

                            if conf.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH') and game.get('doubleheader'):
                                if self.games[game.get('othergame')].get('doubleheader'):
                                    logger.info("Linking pregame submission to doubleheader Game %s...",game.get('othergame'))
                                    self.games[game.get('othergame')].update({'presub' : game.get('presub')})
                            break
                        except Exception, err:
                            logger.error("Error posting/editing pregame thread: %s: retrying after 30 seconds...",err)
                            time.sleep(30)
                logger.info("Finished posting pregame threads...")
                logger.debug("self.games: %s",self.games)
            elif not conf.SETTINGS.get('PRE_THREAD').get('ENABLED') and len(self.games):
                logger.info("Pregame thread disabled...")

            while len(self.games) > 0:
                for k,game in self.games.items():
                    if len(self.games)>1: logger.info("Game %s check",k)
                    game.update({'status' : edit.get_status(k)})
                    self.editStats[k]['checked'].append({'stamp':datetime.today().strftime('%Y-%m-%d %H:%M:%S'), 'abstractGameState':game.get('status').get('abstractGameState'), 'detailedState':game.get('status').get('detailedState')})
                    if timechecker.gamecheck(k,activegames+pendinggames) == True:
                        if not game.get('gamesub'):
                            logger.info("Generating game thread title for Games %s...",k)
                            game.update({'gametitle': edit.generate_title(k,'game')})
                        if not game.get('final'):
                            check = edit.convert_tz(datetime.utcnow(),'bot')
                            try:
                                subreddit = r.subreddit(conf.SETTINGS.get('SUBREDDIT'))
                                if conf.SETTINGS.get('STICKY'):
                                    if len(stale_games):
                                        logger.info("Unstickying stale threads...")
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
                                            logger.error("Unsticky of stale posts failed, continuing...")
                                        stale_games.clear()
                                    if game.get('presub') and not game.get('gamesub'):
                                        logger.info("Unstickying Game %s pregame thread...",k)
                                        try:
                                            game.get('presub').mod.sticky(state=False)
                                        except:
                                            logger.error("Unsticky of pregame thread failed, continuing...")
                                if not game.get('gamesub') and not game.get('skipflag'):
                                    original_gametitle = None
                                    if game.get('status').get('abstractGameState') == 'Final':
                                        logger.info("Detected Game %s is over. Checking for game thread with previous title (subtracting win/loss from team records)...",k)
                                        original_gametitle = edit.generate_title(k,'game',True)
                                    for submission in subreddit.new():
                                        if submission.title in [game.get('gametitle'), original_gametitle]:
                                            if submission.title == original_gametitle: game.update({'gametitle' : original_gametitle})
                                            logger.info("Game %s thread already posted, getting submission...",k)
                                            game.update({'gamesub' : submission, 'status' : edit.get_status(k)})
                                            threads[k].update({'game' : submission.selftext})
                                            break
                                    if game.get('gamesub'):
                                        if conf.SETTINGS.get('STICKY'):
                                            logger.info("Stickying submission...")
                                            try:
                                                game.get('gamesub').mod.sticky()
                                                logger.info("Submission stickied...")
                                            except:
                                                logger.error("Sticky of game thread failed (check mod privileges or the thread may have already been sticky), continuing...")
                                if not game.get('gamesub') and not game.get('skipflag'):
                                    logger.info("Submitting game thread for Game %s...",k)
                                    threads[k].update({'game' : edit.generate_thread_code("game",k)})
                                    if conf.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP'): 
                                        lastupdate = "^^^Last ^^^Updated: ^^^" + edit.convert_tz(datetime.utcnow(),'bot').strftime("%m/%d/%Y ^^^%I:%M:%S ^^^%p ^^^%Z")
                                    else: lastupdate = ""
                                    threadtext = threads[k].get('game') + lastupdate
                                    game.update({'gamesub' : subreddit.submit(game.get('gametitle'), selftext=threadtext, send_replies=conf.SETTINGS.get('GAME_THREAD').get('INBOX_REPLIES')), 'status' : edit.get_status(k)})
                                    logger.info("Game thread submitted...")

                                    if conf.SETTINGS.get('STICKY'):
                                        logger.info("Stickying submission...")
                                        try:
                                            game.get('gamesub').mod.sticky()
                                            logger.info("Submission stickied...")
                                        except:
                                            logger.error("Sticky of game thread failed (check mod privileges), continuing...")

                                    if conf.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT') != "":
                                        logger.info("Setting suggested sort to %s...", conf.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT'))
                                        try:
                                            game.get('gamesub').mod.suggested_sort(conf.SETTINGS.get('GAME_THREAD').get('SUGGESTED_SORT'))
                                            logger.info("Suggested sort set...")
                                        except:
                                            logger.error("Setting suggested sort on game thread failed (check mod privileges), continuing...")

                                    if conf.SETTINGS.get('GAME_THREAD').get('MESSAGE'):
                                        logger.info("Messaging Baseballbot...")
                                        r.redditor('baseballbot').message('Gamethread posted', game.get('gamesub').shortlink)
                                        logger.info("Baseballbot messaged...")

                                    if conf.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                        if conf.SETTINGS.get('GAME_THREAD').get('FLAIR') == "":
                                            logger.error("FLAIR_MODE = submitter, but GAME_THREAD : FLAIR is blank...")
                                        else:
                                            logger.info("Adding flair to submission as submitter...")
                                            choices = game.get('gamesub').flair.choices()
                                            flairsuccess = False
                                            for p in choices:
                                                if p['flair_text'] == conf.SETTINGS.get('GAME_THREAD').get('FLAIR'):
                                                    game.get('gamesub').flair.select(p['flair_template_id'])
                                                    flairsuccess = True
                                            if flairsuccess:
                                                logger.info("Submission flaired...")
                                            else:
                                                logger.error("Flair not set: could not find flair in available choices")
                                    elif conf.SETTINGS.get('FLAIR_MODE') == 'mod':
                                        if conf.SETTINGS.get('GAME_THREAD').get('FLAIR') == "":
                                            logger.error("FLAIR_MODE = mod, but GAME_THREAD : FLAIR is blank...")
                                        else:
                                            logger.info("Adding flair to submission as mod...")
                                            try:
                                                game.get('gamesub').mod.flair(conf.SETTINGS.get('GAME_THREAD').get('FLAIR'))
                                                logger.info("Submission flaired...")
                                            except:
                                                logger.error("Failed to set flair (check mod privileges or change FLAIR_MODE to submitter), continuing...")

                                    if conf.SETTINGS.get('GAME_THREAD').get('TWITTER').get('ENABLED'):
                                        logger.info("Preparing to tweet link to game thread...")
                                        if game.get('ASG'): tweetText = edit.replace_params(conf.SETTINGS.get('GAME_THREAD').get('TWITTER').get('ASG_TEXT').replace('{link}',game.get('gamesub').shortlink), 'game', 'tweet', k)
                                        else: tweetText = edit.replace_params(conf.SETTINGS.get('GAME_THREAD').get('TWITTER').get('TEXT').replace('{link}',game.get('gamesub').shortlink), 'game', 'tweet', k)
                                        twt.PostUpdate(tweetText)
                                        logger.info("Tweet submitted...")

                                    if conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('ENABLED') and conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('NOTIFY_WHEN').get('GAME_THREAD_SUBMITTED'):
                                        logger.info("Sending Prowl notification...")
                                        if game.get('homeaway') == 'home':
                                            vsat = game.get('gameInfo').get('home').get('team_name') + ' vs. ' + game.get('gameInfo').get('away').get('team_name')
                                        else:
                                            vsat = game.get('gameInfo').get('away').get('team_name') + ' @ ' + game.get('gameInfo').get('home').get('team_name')
                                        event = myteam.get('name') + ' Game Thread Posted'
                                        if game.get('doubleheader'): event += ' - DH Game ' + str(game.get('gameNumber'))
                                        description = 'Game thread posted to r/'+conf.SETTINGS.get('SUBREDDIT')+' at '+edit.convert_tz(datetime.utcnow(),'bot').strftime('%I:%M %p %Z')+':\n' +\
                                                        vsat+'\n' +\
                                                        'First Pitch: '+game.get('gameInfo').get('date_object').strftime('%I:%M %p %Z')+'\n' +\
                                                        'Thread title: '+game.get('gametitle')+'\n' +\
                                                        'URL: '+game.get('gamesub').shortlink
                                        try:
                                            prowlResult = prowl.notify(event, description, conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('PRIORITY'), game.get('gamesub').shortlink)
                                            logger.info("Successfully sent notification to Prowl...")
                                        except Exception, e:
                                            logger.error("Failed to send notification to Prowl... Event: %s, Description: %s, Response: %s", event, description, e)

                                    game.update({'skipflag':True})
                                    sleeptime = 5 + conf.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                    logger.info("Sleeping for %s seconds...",sleeptime)
                                    time.sleep(sleeptime)
                            except Exception, err:
                                logger.error("Error while getting/posting game thread: %s: continuing after 10 seconds...",err)
                                time.sleep(10)

                            check = edit.convert_tz(datetime.utcnow(),'bot')
                            if game.get('skipflag'): game.update({'skipflag':False})
                            else:
                                if game.get('gamesub') and conf.SETTINGS.get('GAME_THREAD').get('NOTABLE_PLAY_COMMENTS').get('ENABLED') and (len(conf.SETTINGS.get('GAME_THREAD').get('NOTABLE_PLAY_COMMENTS').get('MYTEAM_BATTING').get('EVENTS'))>0 or len(conf.SETTINGS.get('GAME_THREAD').get('NOTABLE_PLAY_COMMENTS').get('MYTEAM_PITCHING').get('EVENTS'))>0):
                                    logger.debug("Checking for notable plays...")
                                    notablePlayComment, notablePlayCounts = edit.generate_notable_play_comment(k)
                                    if notablePlayComment != "":
                                        logger.info("Submitting notable play comment...")
                                        try:
                                            game.get('gamesub').reply(notablePlayComment)
                                            logger.info("Notable play comment submitted...")
                                            self.editStats[k]['commented'].append(notablePlayCounts)
                                        except:
                                            logger.error("Error submitting notable play comment, continuing...")

                                while True:
                                    statusCheck = edit.get_status(k)
                                    game.update({'status' : statusCheck})
                                    threadstr = edit.generate_thread_code("game",k)
                                    if threadstr != threads[k].get('game'):
                                        threads[k].update({'game' : threadstr})
                                        logger.info("Editing thread for Game %s...",k)
                                        while True:
                                            try:
                                                if conf.SETTINGS.get('GAME_THREAD').get('CONTENT').get('UPDATE_STAMP'): threadstr += "^^^Last ^^^Updated: ^^^" + edit.convert_tz(datetime.utcnow(),'bot').strftime("%m/%d/%Y ^^^%I:%M:%S ^^^%p ^^^%Z")
                                                game.get('gamesub').edit(threadstr)
                                                sleeptime = 5 + conf.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                                logger.info("Game %s edits submitted. Sleeping for %s seconds...",k,sleeptime)
                                                self.editStats[k]['edited'].append({'stamp':datetime.today().strftime('%Y-%m-%d %H:%M:%S'), 'abstractGameState':game.get('status').get('abstractGameState'), 'detailedState':game.get('status').get('detailedState')})
                                                time.sleep(sleeptime)
                                                break
                                            except Exception, err:
                                                logger.error("Couldn't submit edits, retrying in 10 seconds...")
                                                time.sleep(10)
                                    else:
                                        sleeptime = 5 + conf.SETTINGS.get('GAME_THREAD').get('EXTRA_SLEEP')
                                        logger.info("No changes to Game %s thread. Sleeping for %s seconds...",k,sleeptime)
                                        time.sleep(sleeptime)
                                    if (game.get('status').get('abstractGameState') == 'Final' or game.get('status').get('detailedState').startswith("Suspended")) and not (statusCheck.get('abstractGameState') == 'Final' or statusCheck.get('detailedState').startswith("Suspended")):
                                        logger.info("Detected game status changed to final during last game thread update. Updating game thread one more time... ")
                                        continue
                                    else: break

                            if game.get('status').get('abstractGameState') == 'Final' or game.get('status').get('detailedState').startswith("Suspended"):
                                game.update({'gameInfo' : edit.get_teams_time(pk=game.get('gamePk'),d=today.date())})
                                game.get('gameInfo').pop('status') #remove redundant status node (it won't be kept up-to-date anyway)
                                check = edit.convert_tz(datetime.utcnow(),'bot')
                                game.update({'final' : True})
                                logger.info("Game %s Status: %s / %s",k,game.get('status').get('abstractGameState'),game.get('status').get('detailedState'))
                                if conf.SETTINGS.get('POST_THREAD').get('ENABLED'):
                                    try:
                                        myteamwon = edit.didmyteamwin(k)
                                        game.update({'posttitle' : edit.generate_title(k,"post",False,myteamwon)})
                                        subreddit = r.subreddit(conf.SETTINGS.get('SUBREDDIT'))
                                        if conf.SETTINGS.get('STICKY'):
                                            if game.get('presub'):
                                                logger.info("Unstickying Game %s pregame thread...",k)
                                                try:
                                                    game.get('presub').mod.sticky(state=False)
                                                except:
                                                    logger.error("Unsticky of pregame thread failed, continuing...")
                                            if game.get('gamesub'):
                                                logger.info("Unstickying Game %s game thread...",k)
                                                try:
                                                    game.get('gamesub').mod.sticky(state=False)
                                                except:
                                                    logger.error("Unsticky of game thread failed, continuing...")
                                        if not game.get('postsub'):
                                            for submission in subreddit.new():
                                                if submission.title == game.get('posttitle'):
                                                    logger.info("Game %s postgame thread already posted, getting submission...",k)
                                                    game.update({'postsub' : submission})
                                                    if conf.SETTINGS.get('STICKY'):
                                                        logger.info("Stickying submission...")
                                                        try:
                                                            game.get('postsub').mod.sticky()
                                                            logger.info("Submission stickied...")
                                                        except:
                                                            logger.error("Sticky of postgame thread failed (check mod privileges or the thread may have already been sticky), continuing...")
                                                    break
                                        if not game.get('postsub'):
                                            logger.info("Submitting postgame thread for Game %s...",k)
                                            game.update({'postsub' : subreddit.submit(game.get('posttitle'), selftext=edit.generate_thread_code("post",k), send_replies=conf.SETTINGS.get('POST_THREAD').get('INBOX_REPLIES'))})
                                            logger.info("Postgame thread submitted...")

                                            if conf.SETTINGS.get('STICKY'):
                                                logger.info("Stickying submission...")
                                                try:
                                                    game.get('postsub').mod.sticky()
                                                    logger.info("Submission stickied...")
                                                except:
                                                    logger.error("Sticky of postgame thread failed (check mod privileges), continuing...")

                                            if conf.SETTINGS.get('FLAIR_MODE') == 'submitter':
                                                if conf.SETTINGS.get('POST_THREAD').get('FLAIR') == "":
                                                    logger.error("FLAIR_MODE = submitter, but POST_THREAD : FLAIR is blank...")
                                                else:
                                                    logger.info("Adding flair to submission as submitter...")
                                                    choices = game.get('postsub').flair.choices()
                                                    flairsuccess = False
                                                    for p in choices:
                                                        if p['flair_text'] == conf.SETTINGS.get('POST_THREAD').get('FLAIR'):
                                                            game.get('postsub').flair.select(p['flair_template_id'])
                                                            flairsuccess = True
                                                    if flairsuccess:
                                                        logger.info("Submission flaired...")
                                                    else:
                                                        logger.error("Flair not set: could not find flair in available choices")
                                            elif conf.SETTINGS.get('FLAIR_MODE') == 'mod':
                                                if conf.SETTINGS.get('POST_THREAD').get('FLAIR') == "":
                                                    logger.error("FLAIR_MODE = mod, but POST_THREAD : FLAIR is blank...")
                                                else:
                                                    logger.info("Adding flair to submission as mod...")
                                                    try:
                                                        game.get('postsub').mod.flair(conf.SETTINGS.get('POST_THREAD').get('FLAIR'))
                                                        logger.info("Submission flaired...")
                                                    except:
                                                        logger.error("Failed to set flair (check mod privileges or change FLAIR_MODE to submitter), continuing...")

                                            if conf.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT') != "":
                                                logger.info("Setting suggested sort to %s...",conf.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT'))
                                                try:
                                                    game.get('postsub').mod.suggested_sort(conf.SETTINGS.get('POST_THREAD').get('SUGGESTED_SORT'))
                                                    logger.info("Suggested sort set...")
                                                except:
                                                    logger.error("Setting suggested sort on postgame thread failed (check mod privileges), continuing...")

                                            if conf.SETTINGS.get('POST_THREAD').get('TWITTER').get('ENABLED'):
                                                logger.info("Preparing to tweet link to postgame thread...")
                                                if game.get('ASG'): winLossOther = 'ASG'
                                                elif myteamwon=="1": winLossOther = "WIN"
                                                elif myteamwon=="0": winLossOther = "LOSS"
                                                else: winLossOther = "OTHER"
                                                tweetText = edit.replace_params(conf.SETTINGS.get('POST_THREAD').get('TWITTER').get(winLossOther+"_TEXT").replace('{link}',game.get('postsub').shortlink), 'post', 'tweet', k)
                                                twt.PostUpdate(tweetText)
                                                logger.info("Tweet submitted...")

                                            if conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('ENABLED') and conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('NOTIFY_WHEN').get('POST_THREAD_SUBMITTED'):
                                                logger.info("Sending Prowl notification...")
                                                if game.get('homeaway') == 'home':
                                                    vsat = 'vs. ' + game.get('gameInfo').get('away').get('team_name')
                                                    opp = 'away'
                                                else:
                                                    vsat = '@ ' + game.get('gameInfo').get('home').get('team_name')
                                                    opp = 'home'
                                                event = myteam.get('name') + ' Postgame Thread Posted'
                                                if game.get('doubleheader'): event += ' - DH Game ' + str(game.get('gameNumber'))
                                                description = 'Postgame thread posted to r/'+conf.SETTINGS.get('SUBREDDIT')+' at '+edit.convert_tz(datetime.utcnow(),'bot').strftime('%I:%M %p %Z')+':\n' +\
                                                                game.get('gameInfo').get(game.get('homeaway')).get('team_name')+' ('+str(game.get('gameInfo').get(game.get('homeaway'),{}).get('runs',0))+') '+vsat+' ('+str(game.get('gameInfo').get(opp,{}).get('runs',0))+')\n' +\
                                                                'First Pitch: '+game.get('gameInfo').get('date_object').strftime('%I:%M %p %Z')+'\n' +\
                                                                'Thread title: '+game.get('posttitle')+'\n' +\
                                                                'URL: '+game.get('postsub').shortlink
                                                try:
                                                    prowlResult = prowl.notify(event, description, conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('PRIORITY'), game.get('postsub').shortlink)
                                                    logger.info("Successfully sent notification to Prowl...")
                                                except Exception, e:
                                                    logger.error("Failed to send notification to Prowl... Event: %s, Description: %s, Response: %s", event, description, e)

                                            logger.info("Sleeping for 5 seconds...")
                                            time.sleep(5)
                                    except Exception, err:
                                        logger.error("Error while posting postgame thread: %s: continuing after 15 seconds...",err)
                                        time.sleep(15)
                                elif not conf.SETTINGS.get('POST_THREAD').get('ENABLED') and len(self.games):
                                    logger.info("Postgame thread disabled...")
                        else: 
                            logger.info("Game %s final or postponed, nothing to do... ",k)
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

                #logger.debug("threads: %s",threads) #uncomment if needed for debugging
                if len(offday):
                    logger.debug("offday: %s",offday)
                logger.debug("self.games: %s",self.games)
                limits = r.auth.limits
                if limits.get('used') > maxapi: maxapi = limits.get('used')
                logger.debug("Reddit API Calls: %s - Max usage today: %s",limits,maxapi)
                logger.debug("Active Games: %s ...in Preview Status: %s ...in Delayed Status: %s - Pending Games: %s - Completed Games: %s",activegames,previewgames,delayedgames,pendinggames,completedgames)

                if activegames == 0 and pendinggames == 0:
                    notifDesc = ""
                    for a,b in self.games.items(): # calculate game thread edit stats
                        checks = len(self.editStats[a]['checked'])
                        edits = len(self.editStats[a]['edited'])
                        if checks != 0:
                            overallRate = edits/(checks*1.0)*100
                        else: overallRate = '-'

                        liveChecks = sum(1 for x in self.editStats[a]['checked'] if x.get('abstractGameState') == 'Live' and not x.get('detailedState').startswith('Delayed'))
                        delayedChecks = sum(1 for x in self.editStats[a]['checked'] if x.get('detailedState').startswith('Delayed'))
                        previewChecks = sum(1 for x in self.editStats[a]['checked'] if x.get('abstractGameState') == 'Preview' and not x.get('detailedState').startswith('Delayed'))

                        liveEdits = sum(1 for x in self.editStats[a]['edited'] if x.get('abstractGameState') == 'Live' and not x.get('detailedState').startswith('Delayed'))
                        delayedEdits = sum(1 for x in self.editStats[a]['edited'] if x.get('detailedState').startswith('Delayed'))
                        previewEdits = sum(1 for x in self.editStats[a]['edited'] if x.get('abstractGameState') == 'Preview' and not x.get('detailedState').startswith('Delayed'))

                        commentCount = len(self.editStats[a].get('commented',[]))

                        self.editStatHistory.append({'checks': checks, 'edits': edits, 'liveChecks': liveChecks,
                                                        'liveEdits': liveEdits, 'delayedChecks': delayedChecks,
                                                        'delayedEdits': delayedEdits, 'previewChecks': previewChecks,
                                                        'previewEdits': previewEdits, 'comments': commentCount,
                                                        'gameDate': b.get('gameInfo').get('date_object_utc').strftime('%Y-%m-%dT%H:%M:%SZ')})

                        if liveChecks != 0:
                            liveRate = liveEdits/(liveChecks*1.0)*100
                        else: liveRate = '-'
                        if delayedChecks != 0:
                            delayedRate = delayedEdits/(delayedChecks*1.0)*100
                        else: delayedRate = '-'
                        if previewChecks != 0:
                            previewRate = previewEdits/(previewChecks*1.0)*100
                        else: previewRate = '-'

                        logger.info("Game thread edit stats for Game %s overall: %s checks, %s edits, %s%% edit rate.", a, checks, edits, overallRate)
                        logger.info("Game thread edit stats for Game %s Preview status: %s checks, %s edits, %s%% edit rate.", a, previewChecks, previewEdits, previewRate)
                        logger.info("Game thread edit stats for Game %s Live status: %s checks, %s edits, %s%% edit rate.", a, liveChecks, liveEdits, liveRate)
                        logger.info("Game thread edit stats for Game %s Delayed status: %s checks, %s edits, %s%% edit rate.", a, delayedChecks, delayedEdits, delayedRate)
                        if commentCount > 0: logger.info("Comments submitted by bot to Game %s game thread: %s.", a, commentCount)
                        logger.info("Max Reddit API utilization today: %s.", maxapi)

                        if b.get('homeaway') == 'home':
                            vsat = 'vs. ' + b.get('gameInfo').get('away').get('team_name')
                        else:
                            vsat = '@ ' + b.get('gameInfo').get('home').get('team_name')
                        notifDesc += 'Game thread edit stats for '+b.get('gameInfo').get('date_object').strftime('%I:%M %p %Z')+' '+myteam.get('name')+' game '+vsat+':\n' +\
                                        'Total checks: ' + str(checks) + '\nTotal Edits: ' + str(edits) + '\nOverall edit rate: ' + str(overallRate)[:5] + '%\n\n' + \
                                        'Preview status checks: ' + str(previewChecks) + '\nPreview status edits: ' + str(previewEdits) + '\nPreview status edit rate: ' + str(previewRate)[:5] + '%\n\n' + \
                                        'Live status checks: ' + str(liveChecks) + '\nLive status edits: ' + str(liveEdits) + '\nLive status edit rate: ' + str(liveRate)[:5] + '%\n\n'
                        if delayedChecks > 0:
                            notifDesc += 'Delayed status checks: ' + str(delayedChecks) + '\nDelayed status edits: ' + str(delayedEdits) + '\nDelayed status edit rate: ' + str(delayedRate)[:5] + '%\n\n'
                        if commentCount > 0:
                            notifDesc += 'Comments submitted by bot: ' + str(commentCount) + '\n\n'
                        notifDesc += 'Max Reddit API utilization today: ' + str(maxapi) + '\n\n'

                    if len(self.editStatHistory) > 1:
                        numDays = len(self.editStatHistory)
                        numDelayedDays = sum(1 for x in self.editStatHistory if x.get('delayedChecks')!=0)
                        sumChecks = sum(x.get('checks') for x in self.editStatHistory)
                        sumEdits = sum(x.get('edits') for x in self.editStatHistory)
                        sumLiveChecks = sum(x.get('liveChecks') for x in self.editStatHistory)
                        sumLiveEdits = sum(x.get('liveEdits') for x in self.editStatHistory)
                        sumDelayedChecks = sum(x.get('delayedChecks') for x in self.editStatHistory)
                        sumDelayedEdits = sum(x.get('delayedEdits') for x in self.editStatHistory)
                        sumPreviewChecks = sum(x.get('previewChecks') for x in self.editStatHistory)
                        sumPreviewEdits = sum(x.get('previewEdits') for x in self.editStatHistory)
                        sumCommentCount = sum(x.get('comments') for x in self.editStatHistory)

                        if sumChecks != 0:
                            sumOverallRate = sumEdits/(sumChecks*1.0)*100
                        else: sumOverallRate = '-'
                        if sumLiveChecks != 0:
                            sumLiveRate = sumLiveEdits/(sumLiveChecks*1.0)*100
                        else: sumLiveRate = '-'
                        if sumDelayedChecks != 0:
                            sumDelayedRate = sumDelayedEdits/(sumDelayedChecks*1.0)*100
                        else: sumDelayedRate = '-'
                        if sumPreviewChecks != 0:
                            sumPreviewRate = sumPreviewEdits/(sumPreviewChecks*1.0)*100
                        else: sumPreviewRate = '-'
                        if sumCommentCount != 0:
                            sumCommentRate = sumCommentCount/(numDays)

                        logger.info("Average game thread edit stats over last %s games (all statuses): %s checks, %s edits, %s%% edit rate.", numDays, sumChecks, sumEdits, sumOverallRate)
                        logger.info("Average game thread edit stats over last %s games (Preview status): %s checks, %s edits, %s%% edit rate.", numDays, sumPreviewChecks, sumPreviewEdits, sumPreviewRate)
                        logger.info("Average game thread edit stats over last %s games (Live status): %s checks, %s edits, %s%% edit rate.", numDays, sumLiveChecks, sumLiveEdits, sumLiveRate)
                        logger.info("Average game thread edit stats over last %s games (%s games with Delayed status): %s checks, %s edits, %s%% edit rate.", numDays, numDelayedDays, sumDelayedChecks, sumDelayedEdits, sumDelayedRate)
                        logger.info("Average game thread comments submitted by bot over last %s games: %s comments per game.", numDays, sumCommentRate)
                        
                        notifDesc += 'Average game thread edit stats for last '+str(numDays)+' games:\n' +\
                                        'Total checks: ' + str(sumChecks) + '\nTotal Edits: ' + str(sumEdits) + '\nOverall edit rate: ' + str(sumOverallRate)[:5] + '%\n\n' + \
                                        'Preview status checks: ' + str(sumPreviewChecks) + '\nPreview status edits: ' + str(sumPreviewEdits) + '\nPreview status edit rate: ' + str(sumPreviewRate)[:5] + '%\n\n' + \
                                        'Live status checks: ' + str(sumLiveChecks) + '\nLive status edits: ' + str(sumLiveEdits) + '\nLive status edit rate: ' + str(sumLiveRate)[:5] + '%'
                        if numDelayedDays > 0:
                            notifDesc += '\n\nDelayed status checks ('+str(numDelayedDays)+' games): ' + str(sumDelayedChecks) + '\nDelayed status edits: ' + str(sumDelayedEdits) + '\nDelayed status edit rate: ' + str(sumDelayedRate)[:5] + '%'
                        if sumCommentCount > 0:
                            notifDesc += '\n\nAverage comments submitted by bot per game: ' + str(sumCommentRate)

                    if conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('ENABLED') and conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('NOTIFY_WHEN').get('END_OF_DAY_EDIT_STATS'):
                        event = myteam.get('name') + ' Game Thread Edit Stats'
                        logger.info("Sending Prowl notification with game thread edit stats...")
                        try:
                            prowlResult = prowl.notify(event, notifDesc, conf.SETTINGS.get('NOTIFICATIONS').get('PROWL').get('PRIORITY'))
                            logger.info("Successfully sent notification to Prowl...")
                        except Exception, e:
                            logger.error("Failed to send notification to Prowl... Event: %s, Description: %s, Response: %s", event, notifDesc, e)
                    logger.info("All games final for today, going into end of day loop...")
                    break
                elif pendinggames > 0 and activegames == 0:
                    logger.info("No game threads to post yet, sleeping for 10 minutes... ")
                    time.sleep(600)
                elif activegames > 0 and previewgames == activegames:
                    logger.info("All posted games are in Preview status, sleeping for 5 minutes... ")
                    time.sleep(300)
                elif activegames > 0 and (delayedgames + previewgames) == activegames:
                    logger.info("All posted games are in Preview or Delayed status, sleeping for 1 minute... ")
                    time.sleep(60)
                elif limits.get('remaining') < 60:
                    logger.info("Approaching Reddit API rate limit. Taking a 10 second break...")
                    time.sleep(10)
            if datetime.today().day == today.day:
                timechecker.endofdaycheck()
            else:
                logger.info("NEW DAY")

    def update_settings(self,logger,conf,edit,myteam,timechecker):
        while True:
            try:
                conf.SETTINGS = conf.get_from_file()
            except Exception, e:
                logger.critical("Could not read settings file [%s]: %s. Retrying in 60 seconds...",self.settings_file,e)
                time.sleep(60)
            else:
                settings_results = conf.validate_all()
                if len(settings_results.get('critical')): 
                    logger.critical("Please address the above critical issues. Reloading settings and retrying in 60 seconds...")
                    time.sleep(60)
                else:
                    if not edit: edit = editor.Editor({})
                    if not timechecker: timechecker = timecheck.TimeCheck({})

                    while True:
                        myteam = edit.lookup_team_info(field='all',lookupfield='team_code',lookupval=conf.SETTINGS.get('TEAM_CODE'))
                        if myteam.get('error'):
                            logger.critical("Cannot start up without valid team info. Reloading settings and retrying in 60 seconds...")
                            time.sleep(60)
                        else: 
                            logger.debug("Configured team: %s, team_id: %s",myteam.get('name_display_full'),myteam.get('team_id'))
                            break
                    if myteam == {} or myteam.get('team_code') != conf.SETTINGS.get('TEAM_CODE'):
                        logger.critical("Invalid team code detected: %s -- use lookup_team_code.py to look up the correct team code; see README.md. Reloading settings and retrying in 60 seconds...",conf.SETTINGS.get('TEAM_CODE'))
                        time.sleep(60)
                    else:
                        #now that settings are loaded, reset logger, editor, and timechecker with user settings
                        logger.resetHandlers(conf.SETTINGS.get('LOGGING'),conf.SETTINGS.get('TEAM_CODE').lower()+'-bot')
                        edit.SETTINGS = conf.SETTINGS
                        timechecker.SETTINGS = conf.SETTINGS

                        logger.debug("Settings: %s",conf.SETTINGS)
                        return (logger,conf,edit,myteam,timechecker)

if __name__ == '__main__':
    import os
    settings_path = os.path.dirname(os.path.realpath(__file__)) + '/'
    settings_file = 'settings.json'
    if len(sys.argv)>1:
        settings_file = next((x.split('=')[1] for x in sys.argv if x.startswith('--settings=') or x.startswith('-settings=') or x.startswith('/settings=')),'settings.json')
    if settings_file.find('/') == -1 and settings_file.find('\\') == -1: #absolute path not provided, assume same path as main.py
        settings_file = settings_path + settings_file
    program = Bot(settings_file)
    program.run()
