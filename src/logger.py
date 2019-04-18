# handles logging to file and console

import logging, logging.handlers
import time

class Logger(object):
    def resetHandlers(self, logOptions, loggerName, removeFirst=True):
        if removeFirst:
            for h in list(self.rootLogger.handlers): #remove all handlers to prevent duplicate log entries
                self.rootLogger.removeHandler(h)

        if logOptions.get('FILE'):
            import os
            cwd = os.path.dirname(os.path.realpath(__file__))
            pardir = os.path.abspath(os.path.join(cwd, os.pardir))
            logdir = pardir + "/logs"
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            logPath = logdir + '/' + loggerName + '.log'
            fileLogLevel = getattr(logging, logOptions.get('FILE_LOG_LEVEL').upper(),30)
            for i in [2,1,0]:
                try:
                    fileHandler = logging.handlers.TimedRotatingFileHandler(logPath,
                                                                            when='midnight',interval=1,backupCount=7)
                    fileHandler.setLevel(fileLogLevel)
                    if loggerName == 'startup':
                        formatter = logging.Formatter('%(asctime)s :: %(process)d :: %(levelname)8s :: '+loggerName+'-%(module)s(%(lineno)d) :: %(funcName)s :: %(message)s',
                                                    datefmt='%Y-%m-%d %I:%M:%S %p')
                    else:
                        formatter = logging.Formatter('%(asctime)s :: %(levelname)8s :: '+loggerName+'-%(module)s(%(lineno)d) :: %(funcName)s :: %(message)s',
                                                    datefmt='%Y-%m-%d %I:%M:%S %p')
                    fileHandler.setFormatter(formatter)
                    self.rootLogger.addHandler(fileHandler)
                    break
                except IOError, e:
                    if i>=1: print "Error creating file log handler! Will retry",i,"more time(s), sleeping 3 seconds... ",e
                    else:
                        print "Could not create log file handler. There will be no",loggerName,"logging to file. Continuing in 3 seconds...",e
                        logOptions.update({'FILE':False})
                    time.sleep(3)

        if logOptions.get('CONSOLE'):
            import sys
            console = logging.StreamHandler(sys.stdout)
            consoleLogLevel = getattr(logging, logOptions.get('CONSOLE_LOG_LEVEL').upper(),30)
            console.setLevel(consoleLogLevel)
            formatter = logging.Formatter('%(asctime)s :: %(levelname)8s :: '+loggerName+'-%(module)s(%(lineno)d) :: %(funcName)s :: %(message)s',
                                            datefmt='%Y-%m-%d %I:%M:%S %p')
            console.setFormatter(formatter)
            self.rootLogger.addHandler(console)

        self.logger = logging.getLogger(loggerName)
        if logOptions.get('FILE'): self.logger.info('Logging started! Log file: %s', logPath)
        else: self.logger.info('Logging started!')

    def __init__(self, logOptions, loggerName):
        self.rootLogger = logging.getLogger()
        self.rootLogger.setLevel(logging.DEBUG)

        self.resetHandlers(logOptions, loggerName, False)

        #aliases to shorten calls (logger.logger.info -> logger.info)
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warn = self.logger.warn
        self.error = self.logger.error
        self.critical = self.logger.critical
        self.exception = self.logger.exception
