# handles loading and validation of settings

import simplejson as json
import logging

class Config:
    import os
    FILE = os.path.dirname(os.path.realpath(__file__)) + '/settings.json'
    SETTINGS = {}

    def get_from_file(self, field=None, file=None):
        if not file: file = self.FILE
        with open(file) as data:
            all_settings = json.load(data)
        if field: self.get_setting(field,all_settings)
        else: return all_settings

    def get_setting(self, field, settings=None):
        if not settings: settings = self.SETTINGS

        if field.find(':') == -1: return settings.get(field)

        fieldParts = field.split(':')
        parsedField = settings.get(fieldParts[0])
        for i in range(1,len(fieldParts)):
            if not isinstance(parsedField,dict):
                return None
            parsedField = parsedField.get(fieldParts[i])
        return parsedField

    def set_setting(self, field, value=None, settings=None):
        if not settings: settings = self.SETTINGS
        if not value: value = self.get_setting(field, self.SETTINGS_CONFIG).get('default')
        #TODO: may break if parent key does not exist
        if field.find(':') == -1:
            settings.update({field : value})
            return {'success':'success'}

        fieldParts = field.split(':')
        #logging.debug("Found fieldParts: %s",fieldParts)
        parsedField = settings.get(fieldParts[0])
        for i in range(1,len(fieldParts)):
            if not isinstance(parsedField,dict) and i < len(fieldParts)-1:
                return {'error':'Key ['+str(parsedField)+'] is not a dict.'}
            if i < len(fieldParts)-1:
                parsedField = parsedField.get(fieldParts[i])
            else:
                logging.debug("Updating key: [%s] to: [%s]",fieldParts[i],value)
                parsedField.update({fieldParts[i] : value})
        logging.debug("Result: [%s] = [%s].",field,self.get_setting(field,settings))
        return {'success' : 'success'}

    def validate(self, field, value=None, fix=False, settings=None, config=None):
        if not settings: settings = self.SETTINGS
        if not config: config = self.SETTINGS_CONFIG
        if not value: value = self.get_setting(field,settings)
        logging.debug("Validating field [%s], value: [%s]",field,value)

        fieldSettings = self.get_setting(field, config)
        #logging.debug("fieldSettings for [" + field + "]: %s",fieldSettings)

        warning=[]
        error=[]
        critical=[]

        #is the value blank/missing?
        if value == None:# and fieldSettings.get('default') not in ['',None]:
            if fieldSettings.get('critical'): #is the field critical?
                logging.critical("Critical field [%s] is missing!",field)
                critical.append('Critical field ['+field+'] is missing!')
            else:
                if fix:
                    self.set_setting(field,fieldSettings.get('default'),settings)
                    if not fieldSettings.get('hidden'):
                        logging.warning("Non-critical field [%s] is missing. Updating to default: [%s].",field,fieldSettings.get('default'))
                        warning.append('Non-critical field ['+field+'] is missing. Updating to default: ['+str(fieldSettings.get('default'))+'].')
                else:
                    logging.error("Non-critical field [%s] is missing.",field)
                    error.append('Non-critical field ['+field+'] is missing.')
        # check data type if not missing
        elif (fieldSettings.get('type') == 'bool' and not isinstance(value,bool)) or \
                (fieldSettings.get('type') == 'str' and not (isinstance(value,str) or isinstance(value,unicode))) or \
                (fieldSettings.get('type') == 'int' and not isinstance(value,int)) or \
                (fieldSettings.get('type') == 'dict' and not isinstance(value,dict)):
            if fieldSettings.get('critical'): #is the field critical?
                logging.critical("Type mismatch for critical field [%s]! Expected [%s] and found [%s].",field,fieldSettings.get('type'),type(value))
                critical.append('Type mismatch for critical field ['+field+']! Expected ['+fieldSettings.get('type')+'] and found ['+str(type(value))+'].')
            else:
                if fix:
                    self.set_setting(field,fieldSettings.get('default'),settings)
                    logging.warning("Type mismatch for non-critical field [%s]. Expected [%s] and found [%s]. Updating to default: [%s].",field,fieldSettings.get('type'),type(value),fieldSettings.get('default'))
                    warning.append('Type mismatch for non-critical field ['+field+']. Expected ['+fieldSettings.get('type')+'] and found ['+str(type(value))+']. Updating to default: ['+str(fieldSettings.get('default'))+'].')
                else:
                    logging.error("Type mismatch for non-critical field [%s]. Expected [%s] and found [%s].",field,fieldSettings.get('type'),type(value))
                    error.append('Type mismatch for non-critical field ['+field+']. Expected ['+fieldSettings.get('type')+'] and found ['+str(type(value))+'].')

        if fieldSettings.get('options'): #check if field conforms to defined values
            if value not in fieldSettings.get('options'):
                if fieldSettings.get('critical'): #is the field critical?
                    logging.critical("Invalid value detected for critical field [%s]! Expected %s and found [%s].",field, ",".join(fieldSettings.get('options')), value)
                    critical.append('Invalid value detected for critical field ['+field+']! Expected '+ ",".join(fieldSettings.get('options')) +' and found ['+str(value)+'].')
                else:
                    if fix:
                        self.set_setting(field,fieldSettings.get('default'),settings)
                        logging.warning("Invalid value detected for non-critical field [%s]. Expected %s and found [%s]. Updating to default: [%s].",field,fieldSettings.get('options'),value,fieldSettings.get('default'))
                        warning.append('Invalid value detected for non-critical field ['+field+']. Expected '+ str(fieldSettings.get('options')) +' and found ['+str(value)+']. Updating to default: ['+str(fieldSettings.get('default'))+'].')
                    else:
                        logging.error("Invalid value detected for non-critical field [%s]. Expected %s and found [%s].",field,fieldSettings.get('options'),value)
                        error.append('Invalid value detected for non-critical field ['+field+']. Expected '+ str(fieldSettings.get('options')) +' and found ['+str(value)+'].')

        if fieldSettings.get('xoptions'): #check if field contains blacklisted values
            if value in fieldSettings.get('xoptions'):
                if fieldSettings.get('critical'): #is the field critical?
                    logging.critical("Invalid value detected for critical field [%s]: [%s]!",field,value)
                    critical.append('Invalid value detected for critical field ['+field+']: ['+str(value)+']!')
                else:
                    if fix:
                        self.set_setting(field,fieldSettings.get('default'),settings)
                        logging.warning("Invalid value detected for non-critical field [%s]: [%s]. Updating to default: [%s].",field,value,fieldSettings.get('default'))
                        warning.append('Invalid value detected for non-critical field ['+field+']: ['+str(value)+']. Updating to default: ['+str(fieldSettings.get('default'))+'].')
                    else:
                        logging.error("Invalid value detected for non-critical field [%s]: [%s].",field,value)
                        error.append('Invalid value detected for non-critical field ['+field+']: ['+str(value)+'].')

        if fieldSettings.get('conditions'): #does the field have conditions?
            logging.debug("Field [%s] conditions: %s",field,fieldSettings.get('conditions'))
            for x in fieldSettings.get('conditions'): #iterate through list of conditions
                xl = x.split(",")
                if (not value and 'NONE' in xl) or (value and value in xl) or ('BLANK' in xl and value==""):
                    for f,v in fieldSettings.get(x).items():
                        actual = self.get_setting(f,settings)
                        if actual != v:
                            if fix:
                                self.set_setting(f,v,settings)
                                self.validate(f,v,fix,settings)
                                logging.warning("Condition not met for field [%s]: Condition says [%s] should be [%s], actual value is [%s]. Updated to [%s].",field,f,v,actual,v)
                                warning.append('Condition not met for field ['+field+']: Condition says ['+f+'] should be ['+str(v)+'], actual value is ['+str(actual)+']. Updated to ['+str(v)+'].')
                            else:
                                logging.error("Condition not met for field [%s]. Condition says [%s] should be [%s], actual value is [%s]. Not updating.",field,f,v,actual)
                                error.append('Condition not met for field ['+field+']. Condition says ['+f+'] should be ['+str(v)+'], actual value is ['+str(actual)+']. Not updating.')

        if len(critical)==0 and len(error)==0 and len(warning)==0: return {'success':'success'}
        else: return {'critical':critical, 'error':error, 'warning':warning}

    def validate_all(self, settings=None, config=None, fix=True):
        if not settings: settings = self.SETTINGS
        if not config: config = self.SETTINGS_CONFIG
        warnings = []
        errors = []
        criticals = []
        for k,v in config.items():
            setting = [k]
            val = self.get_setting(k,settings)
            result = self.validate(":".join(setting),val,fix,settings)
            if result.get('warning'): warnings.extend(result.get('warning'))
            if result.get('error'): errors.extend(result.get('error'))
            if result.get('critical'): criticals.extend(result.get('critical'))
            if v.get('type') == 'dict':
                for v2 in v.get('children',[]):
                    setting2 = list(setting)
                    setting2.append(v2)
                    val2 = self.get_setting(":".join(setting2),settings)
                    result = self.validate(":".join(setting2),val2,fix,settings)
                    if result.get('warning'): warnings.extend(result.get('warning'))
                    if result.get('error'): errors.extend(result.get('error'))
                    if result.get('critical'): criticals.extend(result.get('critical'))
                    if v.get(v2).get('type') == 'dict':
                        for v3 in v.get(v2).get('children',[]):
                            setting3 = list(setting2)
                            setting3.append(v3)
                            val3 = self.get_setting(":".join(setting3),settings)
                            result = self.validate(":".join(setting3),val3,fix,settings)
                            if result.get('warning'): warnings.extend(result.get('warning'))
                            if result.get('error'): errors.extend(result.get('error'))
                            if result.get('critical'): criticals.extend(result.get('critical'))
                            if v.get(v2).get(v3).get('type') == 'dict':
                                for v4 in v.get(v2).get(v3).get('children',[]):
                                    setting4 = list(setting3)
                                    setting4.append(v4)
                                    val4 = self.get_setting(":".join(setting4),settings)
                                    result = self.validate(":".join(setting4),val4,fix,settings)
                                    if result.get('warning'): warnings.extend(result.get('warning'))
                                    if result.get('error'): errors.extend(result.get('error'))
                                    if result.get('critical'): criticals.extend(result.get('critical'))
                                    if v.get(v2).get(v3).get(v4).get('type') == 'dict':
                                        for v5 in v.get(v2).get(v3).get(v4).get('children',[]):
                                            setting5 = list(setting4)
                                            setting5.append(v5)
                                            val5 = self.get_setting(":".join(setting5),settings)
                                            result = self.validate(":".join(setting5),val5,fix,settings)
                                            if result.get('warning'): warnings.extend(result.get('warning'))
                                            if result.get('error'): errors.extend(result.get('error'))
                                            if result.get('critical'): criticals.extend(result.get('critical'))
                                            if v.get(v2).get(v3).get(v4).get(v5).get('type') == 'dict':
                                                for v6 in v.get(v2).get(v3).get(v4).get(v5).get('children',[]):
                                                    setting6 = list(setting5)
                                                    setting6.append(v6)
                                                    val6 = self.get_setting(":".join(setting6),settings)
                                                    result = self.validate(":".join(setting6),val6,fix,settings)
                                                    if result.get('warning'): warnings.extend(result.get('warning'))
                                                    if result.get('error'): errors.extend(result.get('error'))
                                                    if result.get('critical'): criticals.extend(result.get('critical'))
                                                    if v.get(v2).get(v3).get(v4).get(v5).get(v6).get('type') == 'dict':
                                                        for v7 in v.get(v2).get(v3).get(v4).get(v5).get(v6).get('children',[]):
                                                            setting7 = list(setting6)
                                                            setting7.append(v7)
                                                            val7 = self.get_setting(":".join(setting7),settings)
                                                            result = self.validate(":".join(setting7),val7,fix,settings)
                                                            if result.get('warning'): warnings.extend(result.get('warning'))
                                                            if result.get('error'): errors.extend(result.get('error'))
                                                            if result.get('critical'): criticals.extend(result.get('critical'))

        return {'critical':criticals, 'error':errors, 'warning':warnings}

    def __init__(self, settings_file_path=None):
        if settings_file_path: self.FILE = settings_file_path

    SETTINGS_CONFIG =   {
                            "CLIENT_ID": {"default":None,"type":"str","critical":True,"xoptions":["XXX",""]},
                            "CLIENT_SECRET": {"default":None,"type":"str","critical":True,"xoptions":["XXX",""]},
                            "REDIRECT_URI": {"default":"http://localhost:8080","type":"str","critical":False},
                            "REFRESH_TOKEN": {"default":None,"type":"str","critical":True,"xoptions":["XXX",""]},
                            "USER_AGENT": {"default":"","type":"str","critical":False},
                            "SUBREDDIT": {"default":None,"type":"str","critical":True,"xoptions":["XXX",""]},
                            "TEAM_CODE": {"default":None,"type":"str","critical":True,"xoptions":["XXX",""]},
                            "STICKY": {"default":True,"type":"bool","critical":False},
                            "FLAIR_MODE": {"default":"none","type":"str","critical":False,"options":["none","mod","submitter"]},
                            "LOGGING": {"default":{},"type":"dict","critical":False,"children":["FILE","FILE_LOG_LEVEL","CONSOLE","CONSOLE_LOG_LEVEL"],
                                "FILE": {"default":True,"type":"bool","critical":False},
                                "FILE_LOG_LEVEL": {"default":"DEBUG","type":"str","critical":False,"options":["DEBUG","INFO","WARNING","ERROR","CRITICAL"]},
                                "CONSOLE": {"default":True,"type":"bool","critical":False},
                                "CONSOLE_LOG_LEVEL": {"default":"INFO","type":"str","critical":False,"options":["DEBUG","INFO","WARNING","ERROR","CRITICAL"]}
                            },
                            "NOTIFICATIONS": {"default":{},"type":"dict","critical":False,"children":["PROWL"],
                                "PROWL": {"default":{},"type":"dict","critical":False,"children":["ENABLED","API_KEY","PRIORITY","NOTIFY_WHEN"],
                                    "ENABLED": {"default":False,"type":"bool","critical":False},
                                    "API_KEY": {"default":"","type":"str","critical":False,"conditions":["BLANK,NONE,XXX"],"BLANK,NONE,XXX":{"NOTIFICATIONS:PROWL:ENABLED":False}},
                                    "PRIORITY": {"default":0,"type":"int","critical":False,"options":[-2,-1,0,1,2]},
                                    "NOTIFY_WHEN": {"default":{},"type":"dict","critical":False,"children":["OFF_THREAD_SUBMITTED","PRE_THREAD_SUBMITTED","GAME_THREAD_SUBMITTED","POST_THREAD_SUBMITTED","END_OF_DAY_EDIT_STATS"],
                                        "OFF_THREAD_SUBMITTED": {"default":True,"type":"bool","critical":False},
                                        "PRE_THREAD_SUBMITTED": {"default":True,"type":"bool","critical":False},
                                        "GAME_THREAD_SUBMITTED": {"default":True,"type":"bool","critical":False},
                                        "POST_THREAD_SUBMITTED": {"default":True,"type":"bool","critical":False},
                                        "END_OF_DAY_EDIT_STATS": {"default":True,"type":"bool","critical":False}
                                    }
                                }
                            },
                            "OFF_THREAD": {"default":{},"type":"dict","critical":False,"children":["ENABLED","TITLE","TIME","SUGGESTED_SORT","INBOX_REPLIES","FLAIR","SUPPRESS_OFFSEASON","FOOTER","TWITTER"],
                                "ENABLED": {"default":True,"type":"bool","critical":False},
                                "TITLE": {"default":"OFF DAY THREAD: The {myTeam:name} ({myTeam:wins}-{myTeam:losses}) are off today - {date:%A, %B %d}","type":"str","critical":False},
                                "TIME": {"default":"8AM","type":"str","critical":False},
                                "SUGGESTED_SORT": {"default":"new","type":"str","critical":False,"options":["confidence","top","new","controversial","old","random","qa",""]},
                                "INBOX_REPLIES": {"default":False,"type":"bool","critical":False},
                                "FLAIR": {"default":"","type":"str","critical":False},
                                "SUPPRESS_OFFSEASON": {"default":True,"type":"bool","critical":False},
                                "FOOTER": {"default":"No game today. Feel free to discuss whatever you want in this thread.","type":"str","critical":False},
                                "TWITTER": {"default":{},"type":"dict","critical":False,"children":["ENABLED","TEXT"],
                                    "ENABLED": {"default":False,"type":"bool","critical":False},
                                    "TEXT": {"default":"The {myTeam:name} are off today. Pass the time in our off day thread: {link} #{myTeam:name%stripspaces}","type":"str","critical":False}
                                }
                            },
                            "PRE_THREAD": {"default":{},"type":"dict","critical":False,"children":["ENABLED","TITLE","CONSOLIDATED_DH_TITLE","TIME","SUPPRESS_MINUTES","SUGGESTED_SORT","INBOX_REPLIES","FLAIR","CONSOLIDATE_DH","CONTENT","TWITTER"],
                                "ENABLED": {"default":True,"type":"bool","critical":False},
                                "TITLE": {"default":"PREGAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}","type":"str","critical":False},
                                "CONSOLIDATED_DH_TITLE": {"default":"PREGAME THREAD:{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d}{dh: - DOUBLEHEADER}","type":"str","critical":False},
                                "TIME": {"default":"8AM","type":"str","critical":False},
                                "SUPPRESS_MINUTES": {"default":0,"type":"int","critical":False},
                                "SUGGESTED_SORT": {"default":"new","type":"str","critical":False,"options":["confidence","top","new","controversial","old","random","qa",""]},
                                "INBOX_REPLIES": {"default":False,"type":"bool","critical":False},
                                "FLAIR": {"default":"","type":"str","critical":False},
                                "CONSOLIDATE_DH": {"default":True,"type":"bool","critical":False},
                                "CONTENT": {"default":{},"type":"dict","critical":False,"children":["HEADER","BLURB","PROBABLES","FOOTER"],
                                    "HEADER": {"default":True,"type":"bool","critical":False},
                                    "BLURB": {"default":True,"type":"bool","critical":False},
                                    "PROBABLES": {"default":True,"type":"bool","critical":False},
                                    "FOOTER": {"default":"","type":"str","critical":False}
                                },
                                "TWITTER": {"default":{},"type":"dict","critical":False,"children":["ENABLED","TEXT","CONSOLIDATED_DH_TEXT"],
                                    "ENABLED": {"default":False,"type":"bool","critical":False},
                                    "TEXT": {"default":"Game day!{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%I:%M%p %Z}. Join the discussion in our pregame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader game %N}","type":"str","critical":False},
                                    "CONSOLIDATED_DH_TEXT": {"default":"Doubleheader day!{series: %D -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}). Join the discussion in our pregame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}","type":"str","critical":False}
                                }
                            },
                            "GAME_THREAD": {"default":{},"type":"dict","critical":False,"children":["TITLE","HOURS_BEFORE","SUGGESTED_SORT","INBOX_REPLIES","FLAIR","MESSAGE","HOLD_DH_GAME2_THREAD","EXTRA_SLEEP","CONTENT","TWITTER"],
                                "TITLE": {"default":"GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}","type":"str","critical":False},
                                "HOURS_BEFORE": {"default":3,"type":"int","critical":False},
                                "SUGGESTED_SORT": {"default":"new","type":"str","critical":False,"options":["confidence","top","new","controversial","old","random","qa",""]},
                                "INBOX_REPLIES": {"default":False,"type":"bool","critical":False},
                                "FLAIR": {"default":"","type":"str","critical":False},
                                "MESSAGE": {"default":False,"type":"bool","critical":False},
                                "HOLD_DH_GAME2_THREAD": {"default":True,"type":"bool","critical":False},
                                "EXTRA_SLEEP": {"default":0,"type":"int","critical":False},
                                "CONTENT": {"default":{},"type":"dict","critical":False,"children":["HEADER","BOX_SCORE","EXTENDED_BOX_SCORE","LINE_SCORE","SCORING_PLAYS","HIGHLIGHTS","CURRENT_STATE","FOOTER","UPDATE_STAMP","THEATER_LINK","PREVIEW_BLURB","PREVIEW_PROBABLES","NEXT_GAME"],
                                    "HEADER": {"default":True,"type":"bool","critical":False},
                                    "BOX_SCORE": {"default":True,"type":"bool","critical":False},
                                    "EXTENDED_BOX_SCORE": {"default":False,"type":"bool","critical":False},
                                    "LINE_SCORE": {"default":True,"type":"bool","critical":False},
                                    "SCORING_PLAYS": {"default":True,"type":"bool","critical":False},
                                    "HIGHLIGHTS": {"default":True,"type":"bool","critical":False},
                                    "CURRENT_STATE": {"default":True,"type":"bool","critical":False},
                                    "FOOTER": {"default":"Remember to **sort by new** to keep up!","type":"str","critical":False},
                                    "UPDATE_STAMP": {"default":True,"type":"bool","critical":False},
                                    "THEATER_LINK": {"default":False,"type":"bool","critical":False},
                                    "PREVIEW_BLURB": {"default":True,"type":"bool","critical":False},
                                    "PREVIEW_PROBABLES": {"default":True,"type":"bool","critical":False},
                                    "NEXT_GAME": {"default":True,"type":"bool","critical":False}
                                },
                                "TWITTER": {"default":{},"type":"dict","critical":False,"children":["ENABLED","TEXT"],
                                    "ENABLED": {"default":False,"type":"bool","critical":False},
                                    "TEXT": {"default":"{series:%D Game %N - }{dh:DH Game %N - }{awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%I:%M%p %Z}. Join the discussion in our game thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}","type":"str","critical":False}
                                }
                            },
                            "POST_THREAD": {"default":{},"type":"dict","critical":False,"children":["ENABLED","WIN_TITLE","LOSS_TITLE","OTHER_TITLE","SUGGESTED_SORT","INBOX_REPLIES","FLAIR","CONTENT","TWITTER"],
                                "ENABLED": {"default":True,"type":"bool","critical":False},
                                "WIN_TITLE": {"default":"WIN THREAD:{series: %D Game %N -} The {myTeam:name} ({myTeam:wins}-{myTeam:losses}) defeated the {oppTeam:name} ({oppTeam:wins}-{oppTeam:losses}) by a score of {myTeam:runs}-{oppTeam:runs} - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}","type":"str","critical":False},
                                "LOSS_TITLE": {"default":"LOSS THREAD:{series: %D Game %N -} The {myTeam:name} ({myTeam:wins}-{myTeam:losses}) fell to the {oppTeam:name} ({oppTeam:wins}-{oppTeam:losses}) by a score of {oppTeam:runs}-{myTeam:runs} - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}","type":"str","critical":False},
                                "OTHER_TITLE": {"default":"POST GAME THREAD:{series: %D Game %N -} {awayTeam:name} ({awayTeam:wins}-{awayTeam:losses}) @ {homeTeam:name} ({homeTeam:wins}-{homeTeam:losses}) - {date:%a %b %d @ %I:%M%p %Z}{dh: - DH Game %N}","type":"str","critical":False},
                                "SUGGESTED_SORT": {"default":"new","type":"str","critical":False,"options":["confidence","top","new","controversial","old","random","qa",""]},
                                "INBOX_REPLIES": {"default":False,"type":"bool","critical":False},
                                "FLAIR": {"default":"","type":"str","critical":False},
                                "CONTENT": {"default":{},"type":"dict","critical":False,"children":["HEADER","BOX_SCORE","EXTENDED_BOX_SCORE","LINE_SCORE","SCORING_PLAYS","HIGHLIGHTS","FOOTER","THEATER_LINK","NEXT_GAME"],
                                    "HEADER": {"default":True,"type":"bool","critical":False},
                                    "BOX_SCORE": {"default":True,"type":"bool","critical":False},
                                    "EXTENDED_BOX_SCORE": {"default":True,"type":"bool","critical":False},
                                    "LINE_SCORE": {"default":True,"type":"bool","critical":False},
                                    "SCORING_PLAYS": {"default":True,"type":"bool","critical":False},
                                    "HIGHLIGHTS": {"default":True,"type":"bool","critical":False},
                                    "FOOTER": {"default":"","type":"str","critical":False},
                                    "THEATER_LINK": {"default":True,"type":"bool","critical":False},
                                    "NEXT_GAME": {"default":True,"type":"bool","critical":False}
                                },
                                "TWITTER": {"default":{},"type":"dict","critical":False,"children":["ENABLED","WIN_TEXT","LOSS_TEXT","OTHER_TEXT"],
                                    "ENABLED": {"default":False,"type":"bool","critical":False},
                                    "WIN_TEXT": {"default":"{series:%D Game %N - }{dh:DH Game %N - }The {myTeam:name} defeated the {oppTeam:name} {myTeam:runs}-{oppTeam:runs}! Join the discussion in our postgame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}","type":"str","critical":False},
                                    "LOSS_TEXT": {"default":"{series:%D Game %N - }{dh:DH Game %N - }The {myTeam:name} fell to the {oppTeam:name} {oppTeam:runs}-{myTeam:runs}. Join the discussion in our postgame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}","type":"str","critical":False},
                                    "OTHER_TEXT": {"default":"{series:%D Game %N - }{dh:DH Game %N - }The discussion continues in our postgame thread: {link} #{myTeam:name%stripspaces}{dh: #doubleheader}","type":"str","critical":False}
                                }
                            },
                            "TWITTER": {"default":{},"type":"dict","critical":False,"children":["CONSUMER_KEY","CONSUMER_SECRET","ACCESS_TOKEN","ACCESS_SECRET"],
                                "CONSUMER_KEY": {"default":"","type":"str","critical":False,"conditions":["BLANK,NONE,XXX"],"BLANK,NONE,XXX":{"OFF_THREAD:TWITTER:ENABLED":False,"PRE_THREAD:TWITTER:ENABLED":False,"GAME_THREAD:TWITTER:ENABLED":False,"POST_THREAD:TWITTER:ENABLED":False}},
                                "CONSUMER_SECRET": {"default":"","type":"str","critical":False,"conditions":["BLANK,NONE,XXX"],"BLANK,NONE,XXX":{"OFF_THREAD:TWITTER:ENABLED":False,"PRE_THREAD:TWITTER:ENABLED":False,"GAME_THREAD:TWITTER:ENABLED":False,"POST_THREAD:TWITTER:ENABLED":False}},
                                "ACCESS_TOKEN": {"default":"","type":"str","critical":False,"conditions":["BLANK,NONE,XXX"],"BLANK,NONE,XXX":{"OFF_THREAD:TWITTER:ENABLED":False,"PRE_THREAD:TWITTER:ENABLED":False,"GAME_THREAD:TWITTER:ENABLED":False,"POST_THREAD:TWITTER:ENABLED":False}},
                                "ACCESS_SECRET": {"default":"","type":"str","critical":False,"conditions":["BLANK,NONE,XXX"],"BLANK,NONE,XXX":{"OFF_THREAD:TWITTER:ENABLED":False,"PRE_THREAD:TWITTER:ENABLED":False,"GAME_THREAD:TWITTER:ENABLED":False,"POST_THREAD:TWITTER:ENABLED":False}},
                            },
                            "STATSAPI_URL": {"default":"https://statsapi.mlb.com","type":"str","critical":False,"hidden":True}
                        }
