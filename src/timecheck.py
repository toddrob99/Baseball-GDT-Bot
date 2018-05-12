# does all the time checking

import urllib2
import time
from datetime import datetime, timedelta
import pytz as tz
import tzlocal
import simplejson as json
import games

class TimeCheck:

    games = games.Games().games

    def __init__(self,time_before,log_level,hold_dh_game2_thread,post_thread_enabled):
        self.time_before = time_before
        self.log_level = log_level
        self.hold_dh_game2_thread = hold_dh_game2_thread
        self.post_thread_enabled = post_thread_enabled

    def endofdaycheck(self):
        today = datetime.today()
        while True:
            check = datetime.today()
            if today.day != check.day:
                if self.log_level>1: print datetime.strftime(check, "%d %I:%M:%S %p") + " NEW DAY"
                return
            else:
                if self.log_level>1: print "Last date check: " + datetime.strftime(check, "%d %I:%M:%S %p")
                time.sleep(600)

    def gamecheck(self,thisgame=1,gamecount=1,just_get_time=False):
        if self.games[thisgame].get('gamesub'): return True #game thread is already posted
        if self.games[thisgame].get('doubleheader') and str(self.games[thisgame].get('gameNumber'))=='2':
            if self.hold_dh_game2_thread and not just_get_time:
                if self.games[self.games[thisgame].get('othergame')].get('doubleheader') and not self.games[self.games[thisgame].get('othergame')].get('final'):
                    if self.log_level>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Holding doubleheader Game",self.games[thisgame].get('gameNumber'),"until Game",self.games[self.games[thisgame].get('othergame')].get('gameNumber'),"is final, sleeping for 5 seconds..."
                    time.sleep(5)
                    return False
            else:
                if self.log_level>2: print "Doubleheader Game 2 start time:",self.games[thisgame].get('gameInfo').get('date_object'),"; Game 1 start time:",self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object')
                if self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object') > self.games[thisgame].get('gameInfo').get('date_object'): #game 1 start time is after game 2 start time
                    if self.log_level>1: print "Detected doubleheader Game 2 start time is before Game 1 start time. Using Game 1 start time + 3.5 hours for Game 2..."
                    self.games[thisgame]['gameInfo'].update({'date_object' : self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object') + timedelta(hours=3, minutes=30)}) #use game 1 start time + 3.5 hours for game 2 start time
                    if self.log_level>2: print "Game 2 start time:",self.games[thisgame].get('gameInfo').get('date_object'),"; Game 1 start time:",self.games[self.games[thisgame].get('othergame')].get('gameInfo').get('date_object')
        if just_get_time: return self.games[thisgame].get('gameInfo').get('date_object').replace(hour=self.games[thisgame].get('gameInfo').get('date_object').hour - self.time_before/60/60)
        if self.games[thisgame].get('status').get('detailedState').startswith('Postponed') or self.games[thisgame].get('status').get('detailedState').startswith('Suspended') or self.games[thisgame].get('status').get('detailedState').startswith('Cancelled'):
            if self.post_thread_enabled:
                if self.log_level>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Game",thisgame,"is",self.games[thisgame].get('status').get('detailedState')+", skipping game thread..." 
                self.games[thisgame].update({'skipflag':True})
            else:
                if self.log_level>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Game",thisgame,"is",self.games[thisgame].get('status').get('detailedState')+", overriding hours before setting for game thread since postgame thread is disabled..." 
            return True #go ahead and post the postgame thread since the game is postponed/suspended/canceled
        while True:
            check = datetime.utcnow().replace(tzinfo=tz.utc).astimezone(tzlocal.get_localzone())
            if self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()) >= check:
                if (self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()) - check).seconds <= self.time_before:
                    return True
                else:
                    if self.log_level>2: print "Time to post game thread:",self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()).replace(hour=self.games[thisgame].get('gameInfo').get('date_object_utc').astimezone(tzlocal.get_localzone()).hour - self.time_before/60/60)
                    if gamecount>1:
                        if self.log_level>1: print datetime.strftime(check, "%d %I:%M:%S %p"),"Not time to post game thread yet, sleeping for 5 seconds..."
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
                if self.log_level>1: print "Last pre-game/offday check: " + datetime.strftime(check, "%d %I:%M:%S %p")
                time.sleep(600)
