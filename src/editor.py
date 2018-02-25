# does all the post generating and editing

import player

import xml.etree.ElementTree as ET
import urllib2
import simplejson as json
from datetime import datetime, timedelta
import time

class Editor:

    def __init__(self,time_info,settings):
        (self.time_zone,self.time_change) = time_info
        self.SETTINGS = settings

    def generate_title(self,dir,thread,dh=False,dhnum=0):
        if thread == "pre": title = self.SETTINGS.get('PRE_THREAD').get('TAG') + " "
        elif thread == "game": title = self.SETTINGS.get('GAME_THREAD').get('TAG') + " "
        elif thread == "post":
            myteamwon = ""
            myteamwon = self.didmyteamwin(dir)
            if myteamwon == "0":
                title = self.SETTINGS.get('POST_THREAD').get('LOSS_TAG') + " "
            elif myteamwon == "1":
                title = self.SETTINGS.get('POST_THREAD').get('WIN_TAG') + " "
            else:
                title = self.SETTINGS.get('POST_THREAD').get('OTHER_TAG') + " "
        while True:
            try:
                response = urllib2.urlopen(dir + "linescore.json")
                break
            except:
                if self.SETTINGS.get('LOG_LEVEL')>0: print "Couldn't find linescore.json for title, trying again in 20 seconds..."
                time.sleep(20)
        filething = json.load(response)
        game = filething.get('data').get('game')
        timestring = game.get('time_date') + " " + game.get('ampm')
        date_object = datetime.strptime(timestring, "%Y/%m/%d %I:%M %p")
        if self.SETTINGS.get('SERIES_IN_TITLES') and game.get('series') and game.get('series_num'):
            title += game.get('series')
            if int(game.get('ser_games')) > 1:
                title += " Game " + game.get('series_num')
            title += " - "
        title = title + game.get('away_team_name') + " (" + game.get('away_win') + "-" + game.get('away_loss') + ")"
        title = title + " @ "
        title = title + game.get('home_team_name') + " (" + game.get('home_win') + "-" + game.get('home_loss') + ")"
        title = title + " - "
        title = title + date_object.strftime("%B %d, %Y")
        if dh:
            if thread == "pre" and self.SETTINGS.get('PRE_THREAD').get('CONSOLIDATE_DH'):
                title = title + " - DOUBLEHEADER"
            else:
                title = title + " - GAME " + dhnum
        if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning",thread,"title..."
        return title

    def generate_pre_code(self,games,gameid,othergameid=None):
        code = ""

        if othergameid and int(games[othergameid].get('gamenum')) < int(games[gameid].get('gamenum')):
            tempgameid = othergameid
            othergameid = gameid
            gameid = tempgameid
        
        temp_dirs = []
        temp_dirs.append(games[gameid].get('url') + "linescore.json")
        temp_dirs.append(games[gameid].get('url') + "gamecenter.xml")
        files = self.download_pre_files(temp_dirs)
        game = files["linescore"].get('data').get('game')
        if othergameid:
            code += "##[Game " + games[gameid].get('gamenum') + "](http://mlb.mlb.com/images/2017_ipad/684/" + game.get('away_file_code') + game.get('home_file_code') + "_684.jpg)\n"
        else:
            code += "##[" + game.get('away_team_name') + " @ " + game.get('home_team_name') + "](http://mlb.mlb.com/images/2017_ipad/684/" + game.get('away_file_code') + game.get('home_file_code') + "_684.jpg)\n"
        
        if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BLURB'):
            code = code + self.generate_blurb(files, self.get_homeaway(self.SETTINGS.get('TEAM_CODE'),games[gameid].get('url')))
        if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BROADCAST'): code = code + self.generate_broadcast_info(files)
        if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('PROBABLES'): code = code + self.generate_probables(files)
        if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('FIRST_PITCH'): code = code + self.generate_pre_first_pitch(files)
        if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('DESCRIPTION'): code = code + self.generate_pre_description(files)
        code = code + "\n\n"

        if othergameid:
            code = code + "---\n##Game " + games[othergameid].get('gamenum') + "\n"
            temp_dirs = []
            temp_dirs.append(games[othergameid].get('url') + "linescore.json")
            temp_dirs.append(games[othergameid].get('url') + "gamecenter.xml")
            ofiles = self.download_pre_files(temp_dirs)
            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BLURB'):
                code = code + self.generate_blurb(ofiles, self.get_homeaway(self.SETTINGS.get('TEAM_CODE'),games[othergameid].get('url')))
            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('BROADCAST'): code = code + self.generate_broadcast_info(ofiles)
            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('PROBABLES'): code = code + self.generate_probables(ofiles)
            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('FIRST_PITCH'): code = code + self.generate_pre_first_pitch(ofiles,files)
            if self.SETTINGS.get('PRE_THREAD').get('CONTENT').get('DESCRIPTION'): code = code + self.generate_pre_description(ofiles)
            code = code + "\n\n"

        if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning all pre code..."
        return code

    def download_pre_files(self,dirs):
        files = dict()
        response = urllib2.urlopen(dirs[0])
        files["linescore"] = json.load(response)
        try:
            response = urllib2.urlopen(dirs[1])
            files["gamecenter"] = ET.parse(response)
        except:
            files["gamecenter"] = ET.Element("root")
        
        return files

    def generate_probables(self,files):
        probables = ""
        pitchers = {'away' : {},'home' : {}}
        try:
            game = files["linescore"].get('data').get('game')
            subs = self.get_subreddits(game.get('home_team_name'), game.get('away_team_name'))

            root = files["gamecenter"].getroot()
            probables_xml = root.find('probables')
            pitchers['away']['firstname'] = probables_xml.find("away/useName").text
            if pitchers['away']['firstname'] == None: pitchers['away']['firstname'] = ""
            pitchers['away']['lastname'] = probables_xml.find("away/lastName").text
            if pitchers['away']['lastname'] == None: pitchers['away']['lastname'] = ""
            pitchers['away']['player_id'] = probables_xml.find("away/player_id").text
            if pitchers['away']['player_id'] == None: pitchers['away']['player_id'] = ""
            pitchers['away']['wins'] = probables_xml.find("away/wins").text
            if pitchers['away']['wins'] == None: pitchers['away']['wins'] = ""
            pitchers['away']['losses'] = probables_xml.find("away/losses").text
            if pitchers['away']['losses'] == None: pitchers['away']['losses'] = ""
            pitchers['away']['era'] = probables_xml.find("away/era").text
            if pitchers['away']['era'] == None: pitchers['away']['era'] = ""
            pitchers['away']['report'] = probables_xml.find("away/report").text
            if pitchers['away']['report'] == None: pitchers['away']['report'] = "No report posted."
            pitchers['home']['firstname'] = probables_xml.find("home/useName").text
            if pitchers['home']['firstname'] == None: pitchers['home']['firstname'] = ""
            pitchers['home']['lastname'] = probables_xml.find("home/lastName").text
            if pitchers['home']['lastname'] == None: pitchers['home']['lastname'] = ""
            pitchers['home']['player_id'] = probables_xml.find("home/player_id").text
            if pitchers['home']['player_id'] == None: pitchers['home']['player_id'] = ""
            pitchers['home']['wins'] = probables_xml.find("home/wins").text
            if pitchers['home']['wins'] == None: pitchers['home']['wins'] = ""
            pitchers['home']['losses'] = probables_xml.find("home/losses").text
            if pitchers['home']['losses'] == None: pitchers['home']['losses'] = ""
            pitchers['home']['era'] = probables_xml.find("home/era").text
            if pitchers['home']['era'] == None: pitchers['home']['era'] = ""
            pitchers['home']['report'] = probables_xml.find("home/report").text
            if pitchers['home']['report'] == None: pitchers['home']['report'] = "No report posted."

            away_pitcher = pitchers['away']['firstname'] + " " + pitchers['away']['lastname']
            if away_pitcher == " ": away_pitcher = "TBA"
            else:
                away_pitcher = "[" + away_pitcher + "](" + "http://mlb.mlb.com/team/player.jsp?player_id=" + pitchers['away']['player_id'] + ")"
                away_pitcher += " (" + pitchers['away']['wins'] + "-" + pitchers['away']['losses'] + ", " + pitchers['away']['era'] + ")"

            home_pitcher = pitchers['home']['firstname'] + " " + pitchers['home']['lastname']
            if home_pitcher == " ": home_pitcher = "TBA"
            else:
                home_pitcher = "[" + home_pitcher + "](" + "http://mlb.mlb.com/team/player.jsp?player_id=" + pitchers['home']['player_id'] + ")"
                home_pitcher += " (" + pitchers['home']['wins'] + "-" + pitchers['home']['losses'] + ", " + pitchers['home']['era'] + ")"

            probables  = " |Pitcher|Report\n"
            probables += "-|-|-\n"
            probables += "[" + game.get('away_team_name') + "](" + subs[1] + ")|" + away_pitcher + "|" + pitchers['away']['report'] + "\n"
            probables += "[" + game.get('home_team_name') + "](" + subs[0] + ")|" + home_pitcher + "|" + pitchers['home']['report'] + "\n"
            probables += "\n"

            return probables
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for probables, returning partial or empty string..."
            return probables

    def generate_pre_first_pitch(self,files,ofiles=None):
        first_pitch = ""
        try:
            game = files["linescore"].get('data').get('game')
            timestring = game.get('time_date') + " " + game.get('ampm')
            date_object = datetime.strptime(timestring, "%Y/%m/%d %I:%M %p")
            
            if game.get('time_date')[-4:] == "3:33" and ofiles != None:
                ogame = ofiles["linescore"].get('data').get('game')
                otimestring = ogame.get('time_date') + " " + ogame.get('ampm')
                odate_object = datetime.strptime(otimestring, "%Y/%m/%d %I:%M %p")
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Detected doubleheader Game 2 start time is before Game 1 start time. Using Game 1 start time + 3.5 hours for Game 2..."
                date_object = odate_object + timedelta(hours=3, minutes=30)

            t = timedelta(hours=self.time_change)
            timezone = self.time_zone
            date_object = date_object - t
            first_pitch = "**First Pitch:** " + date_object.strftime("%I:%M %p ") + timezone + "\n\n"

            return first_pitch
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for first_pitch, returning empty string..."
            return first_pitch

    def generate_pre_description(self,files):
        try:
            game = files["linescore"].get('data').get('game')
            if game.get('description',False):
                return "**Game Note:** " + game.get('description') + "\n\n"
            else:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "No game description found, returning empty string..."
                return ""
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for description, returning empty string..."
            return ""

    def generate_broadcast_info(self,files):
        broadcast_text = ""
        try:
            game = files["linescore"].get('data').get('game')
            subs = self.get_subreddits(game.get('home_team_name'), game.get('away_team_name'))

            root = files["gamecenter"].getroot()
            broadcast = root.find('broadcast')

            if not isinstance(broadcast[0][0].text, type(None)):
                home_tv_broadcast = broadcast[0][0].text
            if not isinstance(broadcast[1][0].text, type(None)):
                away_tv_broadcast = broadcast[1][0].text
            if not isinstance(broadcast[0][1].text, type(None)):
                home_radio_broadcast = broadcast[0][1].text
            if not isinstance(broadcast[1][1].text, type(None)):
                away_radio_broadcast = broadcast[1][1].text

            away_preview = "[Link](http://mlb.com" + game.get('away_preview_link') + ")"
            home_preview = "[Link](http://mlb.com" + game.get('home_preview_link') + ")"

            broadcast_text  = " |TV|Radio|Preview\n"
            broadcast_text += "-|-|-|-\n"
            broadcast_text += "[" + game.get('away_team_name') + "](" + subs[1] + ")|" + away_tv_broadcast + "|" + away_radio_broadcast + "|" + away_preview + "\n"
            broadcast_text += "[" + game.get('home_team_name') + "](" + subs[0] + ")|" + home_tv_broadcast + "|" + home_radio_broadcast + "|" + home_preview + "\n"
            broadcast_text += "\n"

            return broadcast_text
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for broadcast, returning empty string..."
            return broadcast_text
        return None

    def generate_blurb(self,files,homeaway='mlb'):
        blurb = headline = blurbtext = ""
        if homeaway not in ['home','away']:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Home or away not specified for blurb, using 'mlb'..."
            homeaway = 'mlb'
        try:
            root = files["gamecenter"].getroot()
            preview = root.find('previews').find(homeaway)
            if not isinstance(preview.find('headline').text, type(None)):
                headline = preview.find('headline').text
            elif homeaway != 'mlb':
                if self.SETTINGS.get('LOG_LEVEL')>2: print "No",homeaway,"headline avaialble, using mlb headline..."
                root2 = files["gamecenter"].getroot()
                preview2 = root2.find('previews').find('mlb')
                if not isinstance(preview2.find('headline').text, type(None)):
                    headline = preview2.find('headline').text
                else:
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "No mlb headline avaialble, using empty string..."
            if not isinstance(preview.find('blurb').text, type(None)):
                blurbtext = preview.find('blurb').text
            elif homeaway != 'mlb':
                if self.SETTINGS.get('LOG_LEVEL')>2: print "No",homeaway,"blurb avaialble, using mlb blurb..."
                root2 = files["gamecenter"].getroot()
                preview2 = root2.find('previews').find('mlb')
                if not isinstance(preview2.find('blurb').text, type(None)):
                    blurbtext = preview2.find('blurb').text
                else:
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "No mlb blurb avaialble, using empty string..."

            blurb = "**" + headline + "**\n\n" + blurbtext + "\n\n"
            return blurb
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for blurb, returning partial or empty string..."
            return blurb

    def get_homeaway(self, team_code, url):
        try:
            response = urllib2.urlopen(url+"linescore.json")
            linescore = json.load(response)
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading linescore, returning empty string for whether team is home or away..."
            return None
        game = linescore.get('data').get('game')

        if game.get('home_code') == team_code:
            return "home"
        elif game.get('away_code') == team_code:
            return "away"
        else:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Cannot determine if team is home or away, returning empty string..."
            return None
        return None

    def generate_code(self,dir,thread):
        code = ""
        dirs = []
        dirs.append(dir + "linescore.json")
        dirs.append(dir + "gamecenter.xml")
        dirs.append(dir + "boxscore.json")
        dirs.append(dir + "plays.json")
        dirs.append(dir + "inning/inning_Scores.xml")
        dirs.append(dir + "media/mobile.xml")
        files = self.download_files(dirs)
        if thread == "game":
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('HEADER'): code = code + self.generate_header(files,dir)
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('BOX_SCORE'): code = code + self.generate_boxscore(files)
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('LINE_SCORE'): code = code + self.generate_linescore(files)
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('SCORING_PLAYS'): code = code + self.generate_scoring_plays(files)
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('HIGHLIGHTS'): code = code + self.generate_highlights(files,self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('THEATER_LINK'))
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('CURRENT_STATE'): code = code + self.generate_current_state(files)
            code += self.generate_status(files,include_next_game=self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('NEXT_GAME'),url=dir)
            if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('FOOTER'): code = code + self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('FOOTER') + "\n\n"
        elif thread == "post":
            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('HEADER'): code = code + self.generate_header(files,dir)
            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('BOX_SCORE'): code = code + self.generate_boxscore(files)
            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('LINE_SCORE'): code = code + self.generate_linescore(files)
            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('SCORING_PLAYS'): code = code + self.generate_scoring_plays(files)
            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('HIGHLIGHTS'): code = code + self.generate_highlights(files,self.SETTINGS.get('POST_THREAD').get('CONTENT').get('THEATER_LINK'))
            code += self.generate_status(files,include_next_game=self.SETTINGS.get('POST_THREAD').get('CONTENT').get('NEXT_GAME'),url=dir)
            if self.SETTINGS.get('POST_THREAD').get('CONTENT').get('FOOTER'): code = code + "\n" + self.SETTINGS.get('POST_THREAD').get('CONTENT').get('FOOTER') + "\n\n"
        if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning all",thread,"code..."
        return code

    def download_files(self,dirs):
        files = dict()
        try:
            response = urllib2.urlopen(dirs[0])
            files["linescore"] = json.load(response)
        except Exception,e:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading linescore.json:",str(e)
            files["linescore"] = {}

        try:
            response = urllib2.urlopen(dirs[1])
            files["gamecenter"] = ET.parse(response)
        except Exception,e:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading gamecenter.xml:",str(e)
            files["gamecenter"] = ET.Element("root")

        try:
            response = urllib2.urlopen(dirs[2])
            files["boxscore"] = json.load(response)
        except Exception,e:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading boxscore.json:",str(e)
            files["boxscore"] = {}

        try:
            response = urllib2.urlopen(dirs[3])
            files["plays"] = json.load(response)
        except Exception,e:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading plays.json:",str(e)
            files["plays"] = {}

        try:
            response = urllib2.urlopen(dirs[4])
            files["scores"] = ET.parse(response)
        except Exception,e:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading scores.xml:",str(e)
            files["scores"] = ET.Element("root")

        try:
            response = urllib2.urlopen(dirs[5])
            files["highlights"] = ET.parse(response)
        except Exception,e:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading highlights.xml:",str(e)
            files["highlights"] = ET.Element("root")

        return files

    def generate_header(self,files,url=""):
        header = ""
        if url==None: url=""
        try:
            game = files["linescore"].get('data').get('game')
            timestring = game.get('time_date') + " " + game.get('ampm')
            date_object = datetime.strptime(timestring, "%Y/%m/%d %I:%M %p")
            if game.get('time_date')[-4:] == "3:33" and game.get('double_header_sw') == 'Y':
                try:
                    otherurl = url[:-2] + "1/"
                    oresponse = urllib2.urlopen(otherurl+"linescore.json")
                    olinescore = json.load(oresponse)
                    ogame = olinescore.get('data').get('game')
                    otimestring = ogame.get('time_date') + " " + ogame.get('ampm')
                    odate_object = datetime.strptime(otimestring, "%Y/%m/%d %I:%M %p")
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Detected doubleheader Game 2 start time is before Game 1 start time. Using Game 1 start time + 3.5 hours for Game 2..."
                    date_object = odate_object + timedelta(hours=3, minutes=30)
                except Exception as e:
                    if self.SETTINGS.get('LOG_LEVEL')>1: print "Error updating doubleheader Game 2 start time in generate_header, continuing..."
            t = timedelta(hours=self.time_change)
            timezone = self.time_zone
            date_object = date_object - t
            myteamis = ""
            if game.get('home_code') == self.SETTINGS.get('TEAM_CODE'):
                myteamis = "home"
            elif game.get('away_code') == self.SETTINGS.get('TEAM_CODE'):
                myteamis = "away"
            matchup = "[" + game.get('away_team_name') + " @ " + game.get('home_team_name') + "](http://mlb.mlb.com/images/2017_ipad/684/" + game.get('away_file_code') + game.get('home_file_code') + "_684.jpg)"
            if game.get('status') in ['Preview', 'Pre-Game']:
                header += "##" + matchup + "\n"
                if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('PREVIEW_BLURB'): header += self.generate_blurb(files,myteamis)
                if self.SETTINGS.get('GAME_THREAD').get('CONTENT').get('PREVIEW_PROBABLES'): header += self.generate_probables(files)
                if game.get('status') == 'Preview': header += "**First Pitch:** " + date_object.strftime("%I:%M %p ") + timezone + "\n\n"
                if game.get('description',False) and game.get('status') == 'Preview': header += "**Game Note:** " + game.get('description') + "\n\n"
                if game.get('status') == 'Preview': header += "[Preview](http://mlb.mlb.com/mlb/gameday/index.jsp?gid=" + game.get('gameday_link') + ")\n\n"
                header += "\n"
            weather = files["plays"].get('data',{"game":{"weather":{"condition":"","wind":"","temp":""}}}).get('game').get('weather')
            root = files["gamecenter"].getroot()
            broadcast = root.find('broadcast')
            notes = self.get_notes(game.get('home_team_name'), game.get('away_team_name'))
            header += "|" + matchup + " Game Info|Links|\n"
            header += "|:--|:--|\n"
            header += "|**First Pitch:** " + date_object.strftime("%I:%M %p ") + timezone + " @ " + game.get(
                'venue') + "|[Gameday](http://mlb.mlb.com/mlb/gameday/index.jsp?gid=" + game.get(
                'gameday_link') + ")|\n"
            header += "|**Weather:** " + weather.get('condition') + ", " + weather.get(
                'temp') + " F, " + "Wind " + weather.get('wind')
            if "Y" in game.get('double_header_sw') or "S" in game.get('double_header_sw'):
                header += "|[Game Graph](http://www.fangraphs.com/livewins.aspx?date=" + date_object.strftime(
                    "%Y-%m-%d") + "&team=" + game.get('home_team_name') + "&dh=" + game.get(
                    'game_nbr') + "&season=" + date_object.strftime("%Y") + ")|\n"
            else:
                header += "|[Game Graph](http://www.fangraphs.com/livewins.aspx?date=" + date_object.strftime(
                    "%Y-%m-%d") + "&team=" + game.get('home_team_name') + "&dh=0&season=" + date_object.strftime(
                    "%Y") + ")|\n"
            header += "|**TV:** "
            if not isinstance(broadcast[0][0].text, type(None)):
                header += broadcast[0][0].text
            if not isinstance(broadcast[1][0].text, type(None)) and not broadcast[0][0].text == broadcast[1][0].text:
                header += ", " + broadcast[1][0].text
            header += "|[Strikezone Map](http://www.brooksbaseball.net/pfxVB/zoneTrack.php?month=" + date_object.strftime(
                "%m") + "&day=" + date_object.strftime("%d") + "&year=" + date_object.strftime(
                "%Y") + "&game=gid_" + game.get('gameday_link') + "%2F)|\n"
            header += "|**Radio:** "
            if not isinstance(broadcast[0][1].text, type(None)):
                header += broadcast[0][1].text
            if not isinstance(broadcast[1][1].text, type(None)):
                header += ", " + broadcast[1][1].text
            header += "|**Notes:** [Away](http://mlb.mlb.com/mlb/presspass/gamenotes.jsp?c_id=" + notes[
                1] + "), [Home](http://mlb.mlb.com/mlb/presspass/gamenotes.jsp?c_id=" + notes[0] + ")|\n"
            if game.get('description',False): header += "|**Game Note:** " + game.get('description') + "||\n"
            header += "\n\n"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning header..."
            return header
        except Exception, e:
            if self.SETTINGS.get('LOG_LEVEL')>3: print "Caught exception in generate_header():",str(e)
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for header, returning partial header or empty string..."
            return header

    def generate_boxscore(self,files):
        boxscore = ""
        try:
            homebatters = []
            awaybatters = []
            homepitchers = []
            awaypitchers = []
            game = files["boxscore"].get('data').get('boxscore')
            team = files["linescore"].get('data').get('game')
            batting = game.get('batting')
            for i in range(0, len(batting)):
                players = batting[i].get('batter')
                for b in range(0, len(players)):
                    if players[b].get('bo') != None:
                        if batting[i].get('team_flag') == "home":
                            homebatters.append(
                                player.batter(players[b].get('name'), players[b].get('pos'), players[b].get('ab'),
                                              players[b].get('r'), players[b].get('h'), players[b].get('rbi'),
                                              players[b].get('bb'), players[b].get('so'), players[b].get('avg'),
                                              players[b].get('id')))
                        else:
                            awaybatters.append(
                                player.batter(players[b].get('name'), players[b].get('pos'), players[b].get('ab'),
                                              players[b].get('r'), players[b].get('h'), players[b].get('rbi'),
                                              players[b].get('bb'), players[b].get('so'), players[b].get('avg'),
                                              players[b].get('id')))
            pitching = game.get('pitching')
            for i in range(0, len(pitching)):
                players = pitching[i].get('pitcher')
                if type(players) is list:
                    for p in range(0, len(players)):
                        if pitching[i].get('team_flag') == "home":
                            homepitchers.append(
                                player.pitcher(players[p].get('name'), players[p].get('out'), players[p].get('h'),
                                               players[p].get('r'), players[p].get('er'), players[p].get('bb'),
                                               players[p].get('so'), players[p].get('np'), players[p].get('s'),
                                               players[p].get('era'), players[p].get('id')))
                        else:
                            awaypitchers.append(
                                player.pitcher(players[p].get('name'), players[p].get('out'), players[p].get('h'),
                                               players[p].get('r'), players[p].get('er'), players[p].get('bb'),
                                               players[p].get('so'), players[p].get('np'), players[p].get('s'),
                                               players[p].get('era'), players[p].get('id')))
                elif type(players) is dict:
                    if pitching[i].get('team_flag') == "home":
                        homepitchers.append(
                            player.pitcher(players.get('name'), players.get('out'), players.get('h'), players.get('r'),
                                           players.get('er'), players.get('bb'), players.get('so'), players.get('np'),
                                           players.get('s'), players.get('era'), players.get('id')))
                    else:
                        awaypitchers.append(
                            player.pitcher(players.get('name'), players.get('out'), players.get('h'), players.get('r'),
                                           players.get('er'), players.get('bb'), players.get('so'), players.get('np'),
                                           players.get('s'), players.get('era'), players.get('id')))
            while len(homebatters) < len(awaybatters):
                homebatters.append(player.batter())
            while len(awaybatters) < len(homebatters):
                awaybatters.append(player.batter())
            while len(homepitchers) < len(awaypitchers):
                homepitchers.append(player.pitcher())
            while len(awaypitchers) < len(homepitchers):
                awaypitchers.append(player.pitcher())
            boxscore = boxscore + team.get('away_team_name') + "|Pos|AB|R|H|RBI|BB|SO|BA|"
            boxscore = boxscore + team.get('home_team_name') + "|Pos|AB|R|H|RBI|BB|SO|BA|"
            boxscore = boxscore + "\n"
            boxscore = boxscore + ":--|:--|:--|:--|:--|:--|:--|:--|:--|"
            boxscore = boxscore + ":--|:--|:--|:--|:--|:--|:--|:--|:--|"
            boxscore = boxscore + "\n"
            for i in range(0, len(homebatters)):
                boxscore = boxscore + str(awaybatters[i]) + "|" + str(homebatters[i]) + "\n"
            boxscore = boxscore + "\n"
            boxscore = boxscore + team.get('away_team_name') + "|IP|H|R|ER|BB|SO|P-S|ERA|"
            boxscore = boxscore + team.get('home_team_name') + "|IP|H|R|ER|BB|SO|P-S|ERA|"
            boxscore = boxscore + "\n"
            boxscore = boxscore + ":--|:--|:--|:--|:--|:--|:--|:--|:--|"
            boxscore = boxscore + ":--|:--|:--|:--|:--|:--|:--|:--|:--|"
            boxscore = boxscore + "\n"
            for i in range(0, len(homepitchers)):
                boxscore = boxscore + str(awaypitchers[i]) + "|" + str(homepitchers[i]) + "\n"
            boxscore = boxscore + "\n\n"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning boxscore..."
            return boxscore
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for boxscore, returning empty string..."
            return boxscore

    def generate_linescore(self,files):
        linescore = ""
        try:
            game = files["linescore"].get('data').get('game')
            subreddits = self.get_subreddits(game.get('home_team_name'), game.get('away_team_name'))
            if game.get('status') in ['Preview','Pre-Game']:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning linescore (none)..."
                return linescore
            lineinfo = game.get('linescore')
            innings = len(lineinfo) if len(lineinfo) > 9 else 9
            linescore = linescore + "Linescore|"
            for i in range(1, innings + 1):
                linescore = linescore + str(i) + "|"
            linescore = linescore + "R|H|E\n"
            for i in range(0, innings + 4):
                linescore = linescore + ":--|"
            linescore = linescore + "\n" + "[" + game.get('away_team_name') + "](" + subreddits[1] + ")" + "|"
            x = 1
            if type(lineinfo) is list:
                for v in lineinfo:
                    linescore = linescore + v.get('away_inning_runs') + "|"
                    x = x + 1
            elif type(lineinfo) is dict:
                linescore = linescore + lineinfo.get('away_inning_runs') + "|"
                x = x + 1
            for i in range(x, innings + 1):
                linescore = linescore + "|"
            linescore = linescore + game.get('away_team_runs') + "|" + game.get('away_team_hits') + "|" + game.get(
                'away_team_errors')
            linescore = linescore + "\n" + "[" + game.get('home_team_name') + "](" + subreddits[0] + ")" "|"
            x = 1
            if type(lineinfo) is list:
                for v in lineinfo:
                    linescore = linescore + v.get('home_inning_runs') + "|"
                    x = x + 1
            elif type(lineinfo) is dict:
                linescore = linescore + lineinfo.get('home_inning_runs') + "|"
                x = x + 1
            for j in range(x, innings + 1):
                linescore = linescore + "|"
            linescore = linescore + game.get('home_team_runs') + "|" + game.get('home_team_hits') + "|" + game.get(
                'home_team_errors')
            linescore = linescore + "\n\n\n"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning linescore..."
            return linescore
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for linescore, returning empty string..."
            return linescore

    def generate_scoring_plays(self,files):
        scoringplays = ""
        try:
            root = files["scores"].getroot()
            scores = root.findall("score")
            currinning = ""
            hometeam_abbrev = self.lookup_team_info(field="name_abbrev", lookupfield="team_code", lookupval=root.get("home_team"))
            awayteam_abbrev = self.lookup_team_info(field="name_abbrev", lookupfield="team_code", lookupval=root.get("away_team"))
            scoringplays = scoringplays + "Inning|Scoring Play Description|Score\n"
            scoringplays = scoringplays + ":--|:--|:--\n"
            if len(scores) == 0:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning scoringplays (none)..."
                return ""
            else:
                for s in scores:
                    if s.get("top_inning") == "Y":
                        inningcheck = "Top "
                    else:
                        inningcheck = "Bottom "
                    inningcheck = inningcheck + s.get("inn") + "|"
                    if inningcheck != currinning:
                        currinning = inningcheck
                        scoringplays = scoringplays + currinning
                    else:
                        scoringplays = scoringplays + " |"

                    actions = s.findall("action")
                    try:
                        if s.find('atbat').get('score') == "T":
                            scoringplays = scoringplays + s.find('atbat').get('des')
                        elif s.find('action').get("score") == "T":
                            scoringplays = scoringplays + s.find('action').get('des')
                        else:
                            scoringplays = scoringplays + s.get('pbp')
                    except:
                        scoringplays = scoringplays + "Scoring play description currently unavailable."

                    scoringplays = scoringplays + "|"
                    if int(s.get("home")) < int(s.get("away")):
                        scoringplays = scoringplays + s.get("away") + "-" + s.get("home") + " " + awayteam_abbrev.upper()
                    elif int(s.get("home")) > int(s.get("away")):
                        scoringplays = scoringplays + s.get("home") + "-" + s.get("away") + " " + hometeam_abbrev.upper()
                    else:
                        scoringplays = scoringplays + s.get("home") + "-" + s.get("away")
                    scoringplays = scoringplays + "\n"
                scoringplays = scoringplays + "\n\n"
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning scoringplays..."
                return scoringplays
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for scoringplays, returning empty string..."
            return scoringplays

    def generate_highlights(self,files,theater_link=False):
        highlight = ""
        try:
            root = files["highlights"].getroot()
            video = root.findall("media")
            highlight = highlight + "|Team|Highlight|\n"
            highlight = highlight + "|:--|:--|\n"
            for v in video:
                if v.get('type') == "video" and v.get('media-type') == "T":              
                    try:
                        team = self.get_team(v.get('team_id'))
                        highlight = highlight + "|" + team[0] + "|[" + v.find("headline").text + "](" + v.find("url").text + ")|\n"                   
                    except:
                        highlight = highlight + "|[](/MLB)|[" + v.find("headline").text + "](" + v.find("url").text + ")|\n"                     
            if theater_link:
                game = files["linescore"].get('data').get('game')
                gamedate = game.get("time_date").split(" ",1)[0].replace("/","")
                game_pk = game.get("game_pk")
                highlight = highlight + "||See all highlights at [Baseball.Theater](http://baseball.theater/game/" + gamedate + "/" + game_pk + ")|\n"
            highlight = highlight + "\n\n"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning highlight..."
            return highlight
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for highlight, returning empty string..."
            return highlight

    def generate_current_state(self,files):
        current_state = ""
        try:
            game = files["linescore"].get('data').get('game')
            if game.get('status') not in ['In Progress','Delayed','Delayed Start']:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Game status is not In Progress or Delayed, returning empty string for current_state..."
                return current_state
            elif game.get('status') in ['Delayed', 'Delayed Start']:
                return "###Game is currently delayed...\n\n"
            elif game.get('status') == 'In Progress':
                topbottom = game.get('inning_state') + " of the "
                ordinal = lambda n: str(n) + {1: 'st', 2: 'nd', 3: 'rd'}.get(10<=n%100<=20 and n or n % 10, 'th')
                inning = ordinal(int(game.get('inning')))
                current_state += topbottom + inning
                
                if game.get('outs') == '3':
                    if inning == 'Middle of the 7th': current_state = "Seventh inning stretch"
                    dueup = game.get('due_up_batter').get('first_name') + " " + game.get('due_up_batter').get('last_name')
                    current_state += " with " + dueup
                    
                    ondeck = game.get('due_up_ondeck').get('first_name') + " " + game.get('due_up_ondeck').get('last_name')
                    current_state += ", " + ondeck
                    
                    inhole = game.get('due_up_inhole').get('first_name') + " " + game.get('due_up_inhole').get('last_name')
                    current_state += ", and " + inhole

                    teamcomingup = game.get('home_team_name') if game.get('inning_state')=='Middle' else game.get('away_team_name')
                    current_state += " coming up for the " + teamcomingup + "."
                else:                
                    runner_desc = {'0': 'bases empty', '1' : 'runner on first', '2' : 'runner on second', '3' : 'runner on third', '4' : 'runners on first and second', '5' : 'runners on first and third', '6' : 'runners on second and third', '7' : 'bases loaded'}
                    runners = runner_desc[game.get('runner_on_base_status')]
                    current_state += ", " + runners
                                    
                    outs = game.get('outs')
                    outs += " out" if outs=='1' else " outs"
                    current_state += ", " + outs
                    
                    count = game.get('balls') + "-" + game.get('strikes')
                    current_state += ", and a count of " + count
                    
                    atbat = game.get('current_batter').get('first_name') + " " + game.get('current_batter').get('last_name')
                    current_state += " with " + atbat + " batting"
                    
                    pitcher = game.get('current_pitcher').get('first_name') + " " + game.get('current_pitcher').get('last_name')
                    current_state += " and " + pitcher + " pitching."
                    
                    ondeck = game.get('current_ondeck').get('first_name') + " " + game.get('current_ondeck').get('last_name')
                    current_state += " " + ondeck + " is on deck"
                    
                    inhole = game.get('current_inhole').get('first_name') + " " + game.get('current_inhole').get('last_name')
                    current_state += ", and " + inhole + " is in the hole."
                
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning current_state..."
            return current_state + "\n\n"
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for current_state, returning empty string..."
            return current_state

    def generate_decisions(self,files):
        decisions = ""
        try:
            homepitchers = []
            awaypitchers = []
            game = files["boxscore"].get('data').get('boxscore')
            team = files["linescore"].get('data').get('game')
            subreddits = self.get_subreddits(team.get('home_team_name'), team.get('away_team_name'))
            pitching = game.get('pitching')
            for i in range(0, len(pitching)):
                players = pitching[i].get('pitcher')
                if type(players) is list:
                    for p in range(0, len(players)):
                        if pitching[i].get('team_flag') == "home":
                            homepitchers.append(
                                player.decision(players[p].get('name'), players[p].get('note'), players[p].get('id')))
                        else:
                            awaypitchers.append(
                                player.decision(players[p].get('name'), players[p].get('note'), players[p].get('id')))
                elif type(players) is dict:
                    if pitching[i].get('team_flag') == "home":
                        homepitchers.append(
                            player.decision(players.get('name'), players.get('note'), players.get('id')))
                    else:
                        awaypitchers.append(
                            player.decision(players.get('name'), players.get('note'), players.get('id')))
            decisions = decisions + "|Decisions||" + "\n"
            decisions = decisions + "|:--|:--|" + "\n"
            decisions = decisions + "|" + "[" + team.get('away_team_name') + "](" + subreddits[1] + ")|"
            for i in range(0, len(awaypitchers)):
                decisions = decisions + str(awaypitchers[i]) + " "
            decisions = decisions + "\n" + "|" + "[" + team.get('home_team_name') + "](" + subreddits[0] + ")|"
            for i in range(0, len(homepitchers)):
                decisions = decisions + str(homepitchers[i])
            decisions = decisions + "\n\n"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning decisions..."
            return decisions
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for decisions, returning empty string..."
            return decisions

    def get_status(self,url):
        try:
            response = urllib2.urlopen(url+"linescore.json")
            linescore = json.load(response)
            return linescore.get('data').get('game').get('status')
        except:
            return None
        return None

    def generate_status(self,files,include_next_game=False,url=""):
        status = ""
        try:
            game = files["linescore"].get('data').get('game')
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Status:",game.get('status')
            if game.get('status') == "Game Over" or game.get('status') == "Final":
                s = files["linescore"].get('data').get('game')
                status = status + "##FINAL: "
                if int(s.get("home_team_runs")) < int(s.get("away_team_runs")):
                    status = status + s.get("away_team_runs") + "-" + s.get("home_team_runs") + " " + s.get(
                        "away_team_name") + "\n"
                    status = status + self.generate_decisions(files)
                    if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                    return status
                elif int(s.get("home_team_runs")) > int(s.get("away_team_runs")):
                    status = status + s.get("home_team_runs") + "-" + s.get("away_team_runs") + " " + s.get(
                        "home_team_name") + "\n"
                    status = status + self.generate_decisions(files)
                    if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                    return status
                elif int(s.get("home_team_runs")) == int(s.get("away_team_runs")):
                    status = status + "TIE"
                    if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                    return status
            elif game.get('status') == "Completed Early":
                s = files["linescore"].get('data').get('game')
                status = status + "##COMPLETED EARLY: "
                if int(s.get("home_team_runs")) < int(s.get("away_team_runs")):
                    status = status + s.get("away_team_runs") + "-" + s.get("home_team_runs") + " " + s.get(
                        "away_team_name") + "\n"
                    status = status + self.generate_decisions(files)
                    if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                    return status
                elif int(s.get("home_team_runs")) > int(s.get("away_team_runs")):
                    status = status + s.get("home_team_runs") + "-" + s.get("away_team_runs") + " " + s.get(
                        "home_team_name") + "\n"
                    status = status + self.generate_decisions(files)
                    if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                    return status
                elif int(s.get("home_team_runs")) == int(s.get("away_team_runs")):
                    status = status + "TIE"
                    if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                    return status
            elif game.get('status') == "Postponed":
                status = status + "##POSTPONED\n\n"
                if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                return status
            elif game.get('status') == "Suspended":
                status = status + "##SUSPENDED\n\n"
                if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                return status
            elif game.get('status') == "Cancelled":
                status = status + "##CANCELLED\n\n"
                if include_next_game: status += "\n" + self.generate_next_game(url=url) + "\n\n"
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning status..."
                return status
            else:
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Status not final or postponed, returning empty string..."
                return status
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Missing data for status, returning empty string..."
            return status

    def generate_next_game(self,next_game=None,url=""):
        next = ""
        if not next_game: next_game = self.next_game(7,url)
        if next_game.get('date'):
            if next_game.get('event_time') == '3:33 AM': next_game.update({'event_time' : 'Time TBD'})
            next += "**Next Game:** " + next_game.get('date').strftime("%A, %B %d") + ", " + next_game.get('event_time')
            if next_game.get('homeaway') == 'away':
                next += " @ " + next_game.get('home_team_name')
            else:
                next += " vs " + next_game.get('away_team_name')
            if next_game.get('series') and next_game.get('series_num'):
                next += " (" + next_game.get('series') 
                if next_game.get('series_num') != '0' and next_game.get('series') != 'Spring Training':
                    next += " Game " + next_game.get('series_num')
                next += ")"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning next game..."
            return next
        if self.SETTINGS.get('LOG_LEVEL')>2: print "Next game not found, returning empty string..."
        return next

    def didmyteamwin(self, url):
    #returns 0 for loss, 1 for win, 2 for tie, 3 for postponed/suspended/canceled, blank for exception
        myteamwon = ""
        myteamis = ""
        try:
            response = urllib2.urlopen(url+"linescore.json")
            linescore = json.load(response)
        except:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Error downloading linescore, returning empty string for whether my team won..."
            return myteamwon
        game = linescore.get('data').get('game')

        if game.get('home_code') == self.SETTINGS.get('TEAM_CODE'):
            myteamis = "home"
        elif game.get('away_code') == self.SETTINGS.get('TEAM_CODE'):
            myteamis = "away"
        else:
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Cannot determine if my team is home or away, returning empty string for whether my team won..."
            return myteamwon
        if game.get('status') == "Game Over" or game.get('status') == "Final" or game.get('status') == "Completed Early":
            hometeamruns = int(game.get("home_team_runs"))
            awayteamruns = int(game.get("away_team_runs"))
            if int(hometeamruns == awayteamruns):
                myteamwon = "2"
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning whether my team won (TIE)..."
                return myteamwon
            else:
                if hometeamruns < awayteamruns:
                    if myteamis == "home":
                        myteamwon = "0"
                    elif myteamis == "away":
                        myteamwon = "1"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning whether my team won..."
                    return myteamwon
                elif hometeamruns > awayteamruns:
                    if myteamis == "home":
                        myteamwon = "1"
                    elif myteamis == "away":
                        myteamwon = "0"
                    if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning whether my team won..."
                    return myteamwon
        elif game.get('status') == "Postponed" or game.get('status') == "Suspended" or game.get('status') == "Cancelled":
            myteamwon = "3"
            if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning whether my team won (postponed, suspended, or canceled)..."
            return myteamwon
        if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning whether my team won (exception)..." + myteamwon
        return myteamwon

    def next_game(self,check_days=14,thisurl=""):
        if self.SETTINGS.get('LOG_LEVEL')>2: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Searching for next game..."
        if thisurl==None: thisurl=""
        base_url = "http://gd2.mlb.com/components/game/mlb/"
        today = datetime.today().date()
        #today = datetime.strptime('2018-02-23','%Y-%m-%d').date() # leave commented unless testing
        for d in (today + timedelta(days=x) for x in range(0, check_days)):
            next_game = {}
            if self.SETTINGS.get('LOG_LEVEL')>3: print "Searching for games on",d
            dayurl = base_url + d.strftime("year_%Y/month_%m/day_%d")
            gridurl = dayurl + "/grid.json"
            while True:
                try:
                    gridresponse = urllib2.urlopen(gridurl)
                except urllib2.HTTPError, e:
                    if e.code == 404:
                        daygames = {}
                        break
                    else:
                        if self.SETTINGS.get('LOG_LEVEL')>0: print "Couldn't find URL for next game lookup, returning empty string..."
                        return {}
                else:
                    daygames = json.load(gridresponse).get('data',{}).get('games',{}).get('game',{})
                    break

            i=0
            if isinstance(daygames,dict): daygames = [daygames]
            for daygame in daygames:
                homeaway = None
                if daygame.get('home_code') == self.SETTINGS.get('TEAM_CODE'): homeaway = 'home'
                if daygame.get('away_code') == self.SETTINGS.get('TEAM_CODE'): homeaway = 'away'
                if homeaway != None:
                    gid = 'gid_' + daygame.get('id').replace('/','_').replace('-','_') + '/'
                    if gid == 'gid_/':
                        if homeaway == 'home' and daygame.get('series') == 'Exhibition Game':
                            gid = 'gid_' + d.strftime("%Y_%m_%d_") + daygame.get('away_code') + 'bbc_' + daygame.get('home_code') + 'mlb_' + daygame.get('game_nbr') + '/'
                        elif homeaway == 'away' and daygame.get('series') == 'Exhibition Game':
                            gid = 'gid_' + d.strftime("%Y_%m_%d_") + daygame.get('away_code') + 'mlb_' + daygame.get('home_code') + 'bbc_' + daygame.get('game_nbr') + '/'
                        else:
                            gid = 'gid_' + d.strftime("%Y_%m_%d_") + daygame.get('away_code') + 'mlb_' + daygame.get('home_code') + 'mlb_' + daygame.get('game_nbr') + '/'
                    if dayurl + "/" + gid != thisurl:
                        if daygame.get('game_nbr')=='2' and dayurl+ "/" +gid[:-2]!=thisurl[:-2]: continue
                        else:
                            next_game[i] = {'url' : dayurl+ "/" +gid, 'date' : d, 'days_away' : (d - today).days, 'homeaway' : homeaway, 'home_code' : daygame.get('home_code'), 'away_code' : daygame.get('away_code'), 'home_team_name' : daygame.get('home_team_name'), 'away_team_name' : daygame.get('away_team_name'), 'event_time' : daygame.get('event_time'), 'series' : daygame.get('series'), 'series_num' : daygame.get('series_num')}
                            i += 1

            if len(next_game)==0:
                if self.SETTINGS.get('LOG_LEVEL')>3: print "No games found on",d
            else:
                if self.SETTINGS.get('LOG_LEVEL')>3: print "next_game found game(s):",next_game
                if len(next_game)>1:
                    for ngk,ng in next_game.items():
                        if (ng.get('homeaway')=='home' and self.lookup_team_info(field='team_code',lookupfield='team_code',lookupval=ng.get('away_code'))==None) or (ng.get('homeaway')=='away' and self.lookup_team_info(field='team_code',lookupfield='team_code',lookupval=ng.get('home_code'))==None):
                            if self.SETTINGS.get('LOG_LEVEL')>2: print "Found game with placeholder opponent, skipping " + ng.get('url').replace(dayurl,"") + "..."
                        else:
                            if self.SETTINGS.get('LOG_LEVEL')>3: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Found next game:",ng.get('url').replace(dayurl,"")
                            if self.SETTINGS.get('LOG_LEVEL')>2: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Found next game",(d - today).days,"day(s) away on",d.strftime('%m/%d/%Y') + "..."
                            return ng
                    if dayurl[dayurl.find("year"):] == thisurl[thisurl.find("year"):thisurl.find("gid")]: continue
                    else:
                        if self.SETTINGS.get('LOG_LEVEL')>2: print "Next game lookup found only games with placeholder opponents, returning the first one..."
                        return next_game[0]
                else: return next_game[0]
        if self.SETTINGS.get('LOG_LEVEL')>2: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Found no games in next",check_days,"days..."
        return {}

    def last_game(self,check_days):
        if self.SETTINGS.get('LOG_LEVEL')>2: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Searching for last game..."
        
        last_game = {}
        base_url = "http://gd2.mlb.com/components/game/mlb/"
        today = datetime.today().date()
        for d in (today - timedelta(days=x) for x in range(1, check_days)):
            if self.SETTINGS.get('LOG_LEVEL')>3: print "Searching for games on",d
            url = base_url + d.strftime("year_%Y/month_%m/day_%d")
            response = ""
            while not response:
                try:
                    response = urllib2.urlopen(url)
                except:
                    if self.SETTINGS.get('LOG_LEVEL')>0: print "Couldn't find URL for last_game, retrying in 30 seconds..."
                    time.sleep(30)

            html = response.readlines()
            directories = []
            for v in html:
                if self.SETTINGS.get('TEAM_CODE') + 'mlb' in v:
                    if self.SETTINGS.get('LOG_LEVEL')>2: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Found last game",(today-d).days,"day(s) ago on",d.strftime('%m/%d/%Y') + "..."
                    v = v[v.index("\"") + 1:len(v)]
                    v = v[0:v.index("\"")]
                    last_game.update({'url' : url + "/" + v, 'date' : d, 'days_ago' : (today-d).days})
                    return last_game
                else:
                    if self.SETTINGS.get('LOG_LEVEL')>3: print "No games found on",d
        if self.SETTINGS.get('LOG_LEVEL')>2: print datetime.strftime(datetime.today(), "%d %I:%M:%S %p"),"Found no games in last",check_days,"days..."
        return last_game

    def get_subreddits(self, homename, awayname):
        subreddits = []
        options = {
            "Twins": "/r/minnesotatwins",
            "White Sox": "/r/WhiteSox",
            "Tigers": "/r/MotorCityKitties",
            "Royals": "/r/KCRoyals",
            "Indians": "/r/WahoosTipi",
            "Rangers": "/r/TexasRangers",
            "Astros": "/r/Astros",
            "Athletics": "/r/OaklandAthletics",
            "Angels": "/r/AngelsBaseball",
            "Mariners": "/r/Mariners",
            "Red Sox": "/r/RedSox",
            "Yankees": "/r/NYYankees",
            "Blue Jays": "/r/TorontoBlueJays",
            "Rays": "/r/TampaBayRays",
            "Orioles": "/r/Orioles",
            "Cardinals": "/r/Cardinals",
            "Reds": "/r/Reds",
            "Pirates": "/r/Buccos",
            "Cubs": "/r/CHICubs",
            "Brewers": "/r/Brewers",
            "Giants": "/r/SFGiants",
            "Diamondbacks": "/r/azdiamondbacks",
            "D-backs": "/r/azdiamondbacks",
            "Rockies": "/r/ColoradoRockies",
            "Dodgers": "/r/Dodgers",
            "Padres": "/r/Padres",
            "Phillies": "/r/Phillies",
            "Mets": "/r/NewYorkMets",
            "Marlins": "/r/letsgofish",
            "Nationals": "/r/Nationals",
            "Braves": "/r/Braves"
        }
        subreddits.append(options[homename])
        subreddits.append(options[awayname])
        return subreddits

    def get_notes(self, homename, awayname):
        notes = []
        options = {
            "Twins": "min",
            "White Sox": "cws",
            "Tigers": "det",
            "Royals": "kc",
            "Indians": "cle",
            "Rangers": "tex",
            "Astros": "hou",
            "Athletics": "oak",
            "Angels": "ana",
            "Mariners": "sea",
            "Red Sox": "bos",
            "Yankees": "nyy",
            "Blue Jays": "tor",
            "Rays": "tb",
            "Orioles": "bal",
            "Cardinals": "stl",
            "Reds": "cin",
            "Pirates": "pit",
            "Cubs": "chc",
            "Brewers": "mil",
            "Giants": "sf",
            "Diamondbacks": "ari",
            "D-backs": "ari",
            "Rockies": "col",
            "Dodgers": "la",
            "Padres": "sd",
            "Phillies": "phi",
            "Mets": "nym",
            "Marlins": "mia",
            "Nationals": "was",
            "Braves": "atl"
        }
        notes.append(options[homename])
        notes.append(options[awayname])
        return notes

    def lookup_team_info(self, field="name_abbrev", lookupfield="team_code", lookupval=None):
        try:
            response = urllib2.urlopen("http://mlb.com/lookup/json/named.team_all.bam?sport_code=%27mlb%27&active_sw=%27Y%27&all_star_sw=%27N%27")
            teaminfo = json.load(response)
        except Exception as e:
            if self.SETTINGS.get('LOG_LEVEL')>1: print e
            return None

        teamlist = teaminfo.get('team_all').get('queryResults').get('row')
        for team in teamlist:
            if team.get(lookupfield,None).lower() == lookupval.lower(): return team.get(field)

        if self.SETTINGS.get('LOG_LEVEL')>1: print "Couldn't look up",field,"from",lookupfield,"=",lookupval
        return None

    def get_teams_time(self, url):
        teams = {}
        try:
            response = urllib2.urlopen(url+"linescore.json")
            linescore = json.load(response)
            game = linescore.get('data').get('game')
        except Exception as e:
            if self.SETTINGS.get('LOG_LEVEL')>1: print "Error downloading linescore in get_teams_time, returning empty string..."
            return teams

        timestring = game.get('time_date') + " " + game.get('ampm')
        date_object = datetime.strptime(timestring, "%Y/%m/%d %I:%M %p")

        if game.get('time_date')[-4:] == "3:33" and game.get('double_header_sw') == 'Y':
            try:
                otherurl = url[:-2] + "1/"
                oresponse = urllib2.urlopen(otherurl+"linescore.json")
                olinescore = json.load(oresponse)
                ogame = olinescore.get('data').get('game')
                otimestring = ogame.get('time_date') + " " + ogame.get('ampm')
                odate_object = datetime.strptime(otimestring, "%Y/%m/%d %I:%M %p")
                if self.SETTINGS.get('LOG_LEVEL')>2: print "Detected doubleheader Game 2 start time is before Game 1 start time. Using Game 1 start time + 3.5 hours for Game 2..."
                date_object = odate_object + timedelta(hours=3, minutes=30)
            except Exception as e:
                if self.SETTINGS.get('LOG_LEVEL')>1: print "Error updating doubleheader Game 2 start time in get_teams_time, continuing..."
                return teams
        t = timedelta(hours=self.time_change)
        timezone = self.time_zone
        date_object = date_object - t
        first_pitch = date_object.strftime("%I:%M %p ") + timezone
        
        teams.update({'home' : {'name_abbrev' : game.get('home_name_abbrev'), 'team_code' : game.get('home_code'), 'team_name' : game.get('home_team_name'), 'win' : game.get('home_win'), 'loss' : game.get('home_loss'), 'runs' : game.get('home_team_runs')},
                        'away' : {'name_abbrev' : game.get('away_name_abbrev'), 'team_code' : game.get('away_code'), 'team_name' : game.get('away_team_name'), 'win' : game.get('away_win'), 'loss' : game.get('away_loss'), 'runs' : game.get('away_team_runs')},
                        'time' : first_pitch,
                        'status' : game.get('status')})

        if self.SETTINGS.get('LOG_LEVEL')>2: print "Returning teams and time for specified game..."
        return teams

    def get_team(self, team_id):
        team = []
        options = {
            "142": "[MIN](/r/minnesotatwins)",
            "145": "[CWS](/r/WhiteSox)",
            "116": "[DET](/r/MotorCityKitties)",
            "118": "[KCR](/r/KCRoyals)",
            "114": "[CLE](/r/WahoosTipi)",
            "140": "[TEX](/r/TexasRangers)",
            "117": "[HOU](/r/Astros)",
            "133": "[OAK](/r/OaklandAthletics)",
            "108": "[LAA](/r/AngelsBaseball)",
            "136": "[SEA](/r/Mariners)",
            "111": "[BOS](/r/RedSox)",
            "147": "[NYY](/r/NYYankees)",
            "141": "[TOR](/r/TorontoBlueJays)",
            "139": "[TBR](/r/TampaBayRays)",
            "110": "[BAL](/r/Orioles)",
            "138": "[STL](/r/Cardinals)",
            "113": "[CIN](/r/Reds)",
            "134": "[PIT](/r/Buccos)",
            "112": "[CHC](/r/CHICubs)",
            "158": "[MIL](/r/Brewers)",
            "137": "[SFG](/r/SFGiants)",
            "109": "[ARI](/r/azdiamondbacks)",
            "115": "[COL](/r/ColoradoRockies)",
            "119": "[LAD](/r/Dodgers)",
            "135": "[SDP](/r/Padres)",
            "143": "[PHI](/r/Phillies)",
            "121": "[NYM](/r/NewYorkMets)",
            "146": "[MIA](/r/letsgofish)",
            "120": "[WSH](/r/Nationals)",
            "144": "[ATL](/r/Braves)"
        }
        team.append(options[team_id])
        return team        
