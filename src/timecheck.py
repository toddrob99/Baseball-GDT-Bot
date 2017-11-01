# does all the time checking

import urllib2
import time
from datetime import datetime, timedelta
import simplejson as json

class TimeCheck:

    def __init__(self,time_before,log_level,hold_dh_game2_thread):
        self.time_before = time_before
        self.log_level = log_level
        self.hold_dh_game2_thread = hold_dh_game2_thread

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

    def gamecheck(self,dir,thisgame={},othergame={},gamecount=1,just_get_time=False):
        if thisgame.get('gamesub'): return True #game thread is already posted
        while True:
            try:
                response = urllib2.urlopen(dir + "linescore.json")
                break
            except:
                check = datetime.today()
                if self.log_level>0: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Gamecheck couldn't find file, trying again in 20 seconds..."
                time.sleep(20)
        jsonfile = json.load(response)
        game = jsonfile.get('data').get('game')
        timestring = game.get('time_date') + " " + game.get('ampm')
        date_object = datetime.strptime(timestring, "%Y/%m/%d %I:%M %p")
        if thisgame.get('doubleheader') and thisgame.get('gamenum')=='2':
            if self.hold_dh_game2_thread and not just_get_time:
                if othergame.get('doubleheader') and not othergame.get('final'):
                    if self.log_level>1: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Holding doubleheader Game",thisgame.get('gamenum'),"until Game",othergame.get('gamenum'),"is final, sleeping for 5 seconds..."
                    time.sleep(5)
                    return False
            else:
                while True:
                    try:
                        oresponse = urllib2.urlopen(othergame.get('url') + "linescore.json")
                        break
                    except:
                        if self.log_level>0: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Gamecheck couldn't find file for other game, trying again in 20 seconds..."
                        time.sleep(20)
                ojsonfile = json.load(oresponse)
                ogame = ojsonfile.get('data').get('game')
                otimestring = ogame.get('time_date') + " " + ogame.get('ampm')
                odate_object = datetime.strptime(otimestring, "%Y/%m/%d %I:%M %p")
                if self.log_level>2: print "Doubleheader Game 2 start time:",date_object,"; Game 1 start time:",odate_object
                if odate_object > date_object: #game 1 start time is after game 2 start time
                    if self.log_level>1: print "Detected doubleheader Game 2 start time is before Game 1 start time. Using Game 1 start time + 3.5 hours for Game 2..."
                    date_object = odate_object + timedelta(hours=3, minutes=30) #use game 1 start time + 3.5 hours for game 2 start time
                    if self.log_level>2: print "Game 2 start time:",date_object,"; Game 1 start time:",odate_object
        if just_get_time: return date_object.replace(hour=date_object.hour - self.time_before/60/60)
        while True:
            check = datetime.today()
            if date_object >= check:
                if (date_object - check).seconds <= self.time_before:
                    return True
                else:
                    if self.log_level>2: print "Time to post game thread:",date_object.replace(hour=date_object.hour - self.time_before/60/60)
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
