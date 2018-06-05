# does all the time checking

import urllib2
import time
from datetime import datetime, timedelta
import pytz as tz
import tzlocal
import simplejson as json
import games
import logging

class TimeCheck:

    games = games.Games().games

    def __init__(self,settings):
        self.SETTINGS = settings
        self.time_before = self.SETTINGS.get('GAME_THREAD').get('HOURS_BEFORE') * 60 * 60
        self.hold_dh_game2_thread = self.SETTINGS.get('GAME_THREAD').get('HOLD_DH_GAME2_THREAD')
        self.post_thread_enabled = self.SETTINGS.get('POST_THREAD').get('ENABLED')

    def endofdaycheck(self):
        today = datetime.today()
        while True:
            check = datetime.today()
            if today.day != check.day:
                logging.info("NEW DAY")
                return
            else:
                logging.info("It's not the next day yet. Sleeping for 10 minutes...")
                time.sleep(600)

    def gamecheck(self,thisgame=1,gamecount=1,just_get_time=False):
        if self.games[thisgame].get('gamesub'): return True #game thread is already posted
        if self.games[thisgame].get('doubleheader') and str(self.games[thisgame].get('gameNumber'))=='2':
            if self.hold_dh_game2_thread and not just_get_time:
                if self.games[self.games[thisgame].get('othergame')].get('doubleheader') and not self.games[self.games[thisgame].get('othergame')].get('final'):
                    logging.info("Holding doubleheader Game %s until Game %s is final, sleeping for 5 seconds...", self.games[thisgame].get('gameNumber'), self.games[self.games[thisgame].get('othergame')].get('gameNumber'))
                    time.sleep(5)
                    return False
            else:
                logging.debug("Doubleheader Game 2 start time: %s; Game 1 start time: %s", self.games[thisgame].get('gameInfo').get('date_object'), self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object'))
                if self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object') > self.games[thisgame].get('gameInfo').get('date_object'): #game 1 start time is after game 2 start time
                    logging.info("Detected doubleheader Game 2 start time is before Game 1 start time. Using Game 1 start time + 3.5 hours for Game 2...")
                    self.games[thisgame]['gameInfo'].update({'date_object' : self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object') + timedelta(hours=3, minutes=30)}) #use game 1 start time + 3.5 hours for game 2 start time
                    logging.debug("Game 2 start time: %s; Game 1 start time: %s", self.games[thisgame].get('gameInfo').get('date_object'), self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object'))
        if just_get_time: return self.games[thisgame].get('gameInfo').get('date_object').replace(hour=self.games[thisgame].get('gameInfo').get('date_object').hour - self.time_before/60/60)
        if self.games[thisgame].get('status').get('detailedState').startswith('Postponed') or self.games[thisgame].get('status').get('detailedState').startswith('Suspended') or self.games[thisgame].get('status').get('detailedState').startswith('Cancelled'):
            if self.post_thread_enabled:
                logging.info("Game %s is %s, skipping game thread...",thisgame, self.games[thisgame].get('status').get('detailedState'))
                self.games[thisgame].update({'skipflag':True})
            else:
                logging.info("Game %s is %s, overriding hours before setting for game thread since postgame thread is disabled...", thisgame, self.games[thisgame].get('status').get('detailedState'))
            return True #go ahead and post the postgame thread since the game is postponed/suspended/canceled
        while True:
            check = datetime.utcnow().replace(tzinfo=tz.utc).astimezone(tzlocal.get_localzone())
            if self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()) >= check:
                if (self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()) - check).seconds <= self.time_before:
                    return True
                else:
                    logging.debug("Time to post game thread: %s", self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()).replace(hour=self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()).hour - self.time_before/60/60))
                    if gamecount>1:
                        logging.info("Not time to post Game %s game thread yet, sleeping for 5 seconds...", thisgame)
                        time.sleep(5)
                    return False
            else:
                return True

    def pregamecheck(self,pre_time):
        date_object = datetime.strptime(pre_time, "%I%p")
        while True:
            check = datetime.today()
            if date_object.hour <= check.hour:
                return
            else:
                logging.info("Not time to post pregame/offday thread yet. Sleeping for 10 minutes...")
                time.sleep(600)
