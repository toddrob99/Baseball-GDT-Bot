# does all the time checking

import urllib2
import time
from datetime import datetime
import simplejson as json

class TimeCheck:

    def __init__(self,time_before,log_level):
        self.time_before = time_before
        self.log_level = log_level

    def endofdaycheck(self):
        today = datetime.today()
        while True:
            check = datetime.today()
            if today.day != check.day:
                if self.log_level>1: print datetime.strftime(check, "%d %I:%M:%S %p")
                if self.log_level>1: print "NEW DAY"
                return
            else:
                if self.log_level>1: print "Last date check: " + datetime.strftime(check, "%d %I:%M:%S %p")
                time.sleep(600)


    def gamecheck(self,dir):
        while True:
            try:
                response = urllib2.urlopen(dir + "linescore.json")
                break
            except:
                check = datetime.today()
                if self.log_level>0: print "gamecheck couldn't find file, trying again in twenty seconds..."
                if self.log_level>0: print datetime.strftime(check, "%d %I:%M:%S %p")
                time.sleep(20)
        jsonfile = json.load(response)
        game = jsonfile.get('data').get('game')
        timestring = game.get('time_date') + " " + game.get('ampm')
        date_object = datetime.strptime(timestring, "%Y/%m/%d %I:%M %p")
        while True:
            check = datetime.today()
            if date_object >= check:
                if (date_object - check).seconds <= self.time_before:
                    return True
                else:
                    if self.log_level>1: print "Not time to post yet, sleeping for five seconds..."
                    if self.log_level>1: print datetime.strftime(check, "%d %I:%M:%S %p")
                    time.sleep(5)
                    return False
            else:
                return True

    def ppcheck(self,dir):
        try:
            response = urllib2.urlopen(dir + "linescore.json")
        except:
            check = datetime.today()
            if self.log_level>0: print datetime.strftime(check, "%d %I:%M:%S %p")
            if self.log_level>0: print "ppcheck Couldn't find file, trying again in twenty seconds..."
            time.sleep(20)
        jsonfile = json.load(response)
        game = jsonfile.get('data').get('game')
        return (game.get('status') == "Postponed")

    def pregamecheck(self,pre_time):
        date_object = datetime.strptime(pre_time, "%I%p")
        while True:
            check = datetime.today()
            if date_object.hour <= check.hour:
                return
            else:
                if self.log_level>1: print "Last pre-game/offday check: " + datetime.strftime(check, "%d %I:%M:%S %p")
                time.sleep(600)
