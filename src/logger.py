# handles logging to file and console

class Logger(object):

    def __init__(self, logOptions, teamCode):
        import logging, logging.handlers

        rootLogger = logging.getLogger()
        rootLogger.setLevel(logging.DEBUG)

        if logOptions.get('FILE'):
            import os
            cwd = os.path.dirname(os.path.realpath(__file__))
            pardir = os.path.abspath(os.path.join(cwd, os.pardir))
            logdir = pardir + "/logs"
            if not os.path.exists(logdir):
                os.makedirs(logdir)
            logPath = logdir + '/' + teamCode.lower() + '-bot.log'
            fileLogLevel = getattr(logging, logOptions.get('FILE_LOG_LEVEL').upper(),30)
            fileHandler = logging.handlers.TimedRotatingFileHandler(logPath,
                                                                    when='midnight',interval=1,backupCount=7)
            fileHandler.setLevel(fileLogLevel)
            formatter = logging.Formatter('%(asctime)s :: %(levelname)8s :: '+teamCode.lower()+'-bot-%(module)s :: %(funcName)s :: %(message)s',
                                            datefmt='%Y-%m-%d %I:%M:%S %p')
            fileHandler.setFormatter(formatter)
            rootLogger.addHandler(fileHandler)

        if logOptions.get('CONSOLE'):
            import sys
            console = logging.StreamHandler(sys.stdout)
            consoleLogLevel = getattr(logging, logOptions.get('CONSOLE_LOG_LEVEL').upper(),30)
            console.setLevel(consoleLogLevel)
            formatter = logging.Formatter('%(asctime)s :: %(levelname)8s :: '+teamCode.lower()+'-bot-%(module)s :: %(funcName)s :: %(message)s',
                                            datefmt='%Y-%m-%d %I:%M:%S %p')
            console.setFormatter(formatter)
            rootLogger.addHandler(console)

        self.logger = logging.getLogger(teamCode.lower()+'-bot')

        self.logger.info('Logging started! Log file: %s', logPath)

        #aliases to shorten calls (logger.logger.info -> logger.info)
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warn = self.logger.warn
        self.error = self.logger.error
        self.critical = self.logger.critical
