#!/usr/bin/env python
# encoding: utf-8

from datetime import datetime,timedelta
import time
import simplejson as json
import urllib2
from logger import Logger
import sys

logger = Logger({'CONSOLE': True, 'CONSOLE_LOG_LEVEL': 'DEBUG', 'FILE': False, 'FILE_LOG_LEVEL': 'DEBUG'},'util')

class StatsAPI:

    SETTINGS = {'STATSAPI_URL':'https://statsapi.mlb.com'}
    gamesLive = {}

    def api_download(self,link,critical=True,sleepTime=10,forceDownload=False,localWait=4,apiVer=None):
        usecache=False
        if not link:
            logger.error("No link provided to download. Returning empty dict...")
            return {}
        if apiVer:
            link = '/api/' + apiVer + link[link.find('/',link.find('/api/')+5):]
            logger.debug("updated api link per apiVer param: %s",link)
        if self.gamesLive.get(link) and (self.gamesLive.get(link).get('metaData',{}).get('timeStamp') or self.gamesLive.get(link).get('localTimestamp')) and not forceDownload:
            ts = self.gamesLive.get(link).get('metaData',{}).get('timeStamp',datetime.utcnow().strftime("%Y%m%d_%H%M%S"))
            wait = self.gamesLive.get(link).get('metaData',{}).get('wait','-1')
            logger.debug("api wait time: %s // current time: %s  // use cache (api wait): %s // use cache (local wait): %s",datetime.strptime(ts,"%Y%m%d_%H%M%S") + timedelta(seconds=int(wait)), datetime.utcnow(), datetime.strptime(ts,"%Y%m%d_%H%M%S") + timedelta(seconds=int(wait)) > datetime.utcnow(), self.gamesLive.get(link).get('localTimestamp') + timedelta(seconds=localWait) > datetime.utcnow())
            if (ts and wait and datetime.strptime(ts,"%Y%m%d_%H%M%S") + timedelta(seconds=int(wait)) > datetime.utcnow()) or (self.gamesLive.get(link).get('localTimestamp') and self.gamesLive.get(link).get('localTimestamp') + timedelta(seconds=localWait) > datetime.utcnow()):
                logger.debug("Using cached data for %s...",link)
                usecache = True
        if not usecache:
            if forceDownload:
                logger.debug("Forcing downloading of %s from MLB API...",link)
            else:
                logger.debug("Downloading %s from MLB API...",link)
            while True:
                try:
                    api_response = urllib2.urlopen(self.SETTINGS.get('STATSAPI_URL') + link)
                    self.gamesLive.update({link : json.load(api_response)})
                    self.gamesLive[link].update({'localTimestamp' : datetime.utcnow(),'localWait' : localWait})
                    break
                except urllib2.HTTPError, e:
                    if critical:
                        logger.error("Couldn't download %s from MLB API: %s: retrying in %s seconds...", link, e, sleepTime)
                        time.sleep(sleepTime)
                    else:
                        logger.error("Couldn't download %s from MLB API: %s: continuing in %s seconds...", link, e, sleepTime)
                        time.sleep(sleepTime)
                        break
                except urllib2.URLError, e:
                    if critical:
                        logger.error("Couldn't connect to MLB API to download %s: %s: retrying in %s seconds...", link, e, sleepTime)
                        time.sleep(sleepTime)
                    else:
                        logger.error("Couldn't connect to MLB API to download %s: %s: continuing in %s seconds...", link, e, sleepTime)
                        time.sleep(sleepTime)
                        break
                except Exception, e:
                    if critical:
                        logger.error("Unknown error downloading %s from MLB API: %s: retrying in %s seconds...", link, e, sleepTime)
                        time.sleep(sleepTime)
                    else:
                        logger.error("Unknown error downloading %s from MLB API: %s: continuing in %s seconds...", link, e, sleepTime)
                        time.sleep(sleepTime)
                        break
        return self.gamesLive.get(link)

    def get_schedule(self,day,teamId=None):
        todayurl = "/api/v1/schedule?language=en&sportId=1&date=" + day.strftime("%m/%d/%Y")
        if teamId: todayurl += "&teamId=" + str(teamId)

        todaydata = self.api_download(todayurl,True,30)
        todaydates = todaydata['dates']
        if len(todaydates) == 0: todaygames = {}
        else: todaygames = todaydates[next((i for i,x in enumerate(todaydates) if x.get('date') == day.strftime('%Y-%m-%d')), 0)].get('games')

        if len(todaygames) == 0:
            logger.info("There are no games on %s",day.strftime("%m/%d/%Y"))
            todaygames = {}

        if isinstance(todaygames,dict): todaygames = [todaygames]
        return todaygames

    def get_events(self,date=None,gamePk=None,teamId=None):
        if not date and not gamePk:
            logger.error("No date or gamePk supplied. Returning empty sets.")
            return {'actionEvents' : {}, 'playEvents' : {}}

        actionEvents = set()
        playEvents = set()

        if gamePk:
            logger.info("Parsing gamePk %s...",gamePk)
            gameLive = self.api_download("/api/v1/game/"+str(gamePk)+"/feed/live")
            self.flush_cache() # easier to flush cache than to mess with the api_download function
            gameAllPlays = gameLive.get('liveData').get('plays').get('allPlays')
            for play in gameAllPlays:
                for i in play.get('actions',[]):
                    actionEvents.add(play.get('playEvents')[i].get('details').get('event'))
                playEvents.add(play.get('result').get('event'))
        elif date:
            logger.info("Getting games on %s...",date)
            dayGames = self.get_schedule(date,teamId=teamId)
            for dayGame in (dayGame for dayGame in dayGames if dayGame.get('gamePk')):
                dayEvents = self.get_events(gamePk=dayGame.get('gamePk'))
                actionEvents.update(dayEvents.get('actionEvents'))
                playEvents.update(dayEvents.get('playEvents'))

        return {'actionEvents' : actionEvents, 'playEvents' : playEvents}

    def flush_cache(self):
        self.gamesLive.clear()
        return True

if __name__ == '__main__':
    params = {}
    if len(sys.argv)>1:
        for x in (x for x in sys.argv if not x.endswith('.py')):
            if x.split('=')[0].lower().replace('-','').replace('/','') == 'startdate': params.update({'startDate' : datetime.strptime(x.split('=')[1],'%Y-%m-%d').date()})
            elif x.split('=')[0].lower().replace('-','').replace('/','') == 'enddate': params.update({'endDate' : datetime.strptime(x.split('=')[1],'%Y-%m-%d').date()})
            elif x.split('=')[0].lower().replace('-','').replace('/','') == 'date': params.update({'endDate' : datetime.strptime(x.split('=')[1],'%Y-%m-%d').date(), 'numDays' : 1})
            elif x.split('=')[0].lower().replace('-','').replace('/','') == 'numdays': params.update({'numDays' : int(x.split('=')[1])})
            elif x.split('=')[0].lower().replace('-','').replace('/','') == 'gamepk': params.update({'gamePk' : int(x.split('=')[1])})
            elif x.split('=')[0].lower().replace('-','').replace('/','') == 'teamid': params.update({'teamId' : int(x.split('=')[1])})
        logger.debug("Parsed parameters: %s",params)
    else:
        logger.info("No arguments supplied. Using today's date...")
        params.update({'endDate' : datetime.now().date(), 'numDays' : 1})

    api = StatsAPI()

    if params.get('gamePk'):
        events = api.get_events(gamePk=params['gamePk'])
        logger.info("Events for gamePk %s: %s",params['gamePk'],events)
    else:
        if params.get('endDate'):
            if params.get('startDate'):
                if params.get('endDate') < params.get('startDate'):
                    logger.error("Start date is after end date. Running for end date only...")
                    params.update({'numDays' : 1})
                else:
                    if params.get('numDays'):
                        logger.warning("Both start/end dates and number of days supplied. Using start/end dates and overriding number of days...")
                    params.update({'numDays' : (params.get('endDate') - params.get('startDate')).days})
            elif not params.get('numDays'):
                logger.error("No start date or number of days supplied. Running for end date only...")
                params.update({'numDays' : 1})
        elif params.get('startDate'):
            if not params.get('numDays'):
                logger.error("No end date or number of days supplied. Running for start date only...")
                params.update({'numDays' : 1})
        elif params.get('numDays'):
            logger.error("No start or end date supplied. Using today's date and going back %s days...",params.get('numDays'))
            params.update({'endDate' : datetime.now().date()})
        logger.info("Collecting events %sfrom %s going %s %s day%s...",'for team id '+str(params.get('teamId'))+' ' if params.get('teamId') else '',params.get('endDate') if params.get('endDate') else params.get('startDate'),'back' if params.get('endDate') else 'forward',params.get('numDays'),'s' if params.get('numDays',0)>1 else '')
        events = {'actionEvents' : set(), 'playEvents' : set()}
        if params.get('endDate'):
            for day in (params.get('endDate') - timedelta(n) for n in range(params.get('numDays'))):
                tempEvents = api.get_events(date=day,teamId=params.get('teamId'))
                events['actionEvents'].update(tempEvents.get('actionEvents'))
                events['playEvents'].update(tempEvents.get('playEvents'))
        elif params.get('startDate'):
            for day in (params.get('startDate') + timedelta(n) for n in range(params.get('numDays'))):
                tempEvents = api.get_events(date=day,teamId=params.get('teamId'))
                events['actionEvents'].update(tempEvents.get('actionEvents'))
                events['playEvents'].update(tempEvents.get('playEvents'))
        logger.info("Unique events: %s",events)
