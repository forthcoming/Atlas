# -*- coding: utf-8 -*-
# todo: 为什么handlers和loggers两处都有level参数,如何做到多进程日志
import sys
import logging.config

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'fileFormatter': {
            'format':
                '[%(levelname)s] %(asctime)s [%(module)s - %(filename)s - line:%(lineno)d] [proc:%(process)d] %(message)s',
            # 'datefmt': '%m-%d-%Y %H:%M:%S,%f',
        },
        'consoleFormatter': {
            'format':
                '[%(levelname)s] %(asctime)s [%(module)s - %(filename)s - line:%(lineno)d] [proc:%(process)d] %(message)s',
            # 'datefmt': '%m-%d-%Y %H:%M:%S,%f',
        },
        'default': {
            'format':
                '%(asctime)s %(levelname)s [%(name)s: %(lineno)s] -- %(message)s',
            # 'datefmt': '%m-%d-%Y %H:%M:%S,%f'
        },
    },
    'handlers': {
        'consoleHandler': {
            'level': 'NOTSET',
            'class': 'logging.StreamHandler',  # 输出到控制台
            'formatter': 'consoleFormatter',
            # logging.StreamHandler args
            'stream': sys.stdout
        },
        'AccessTimedRotatingFileHandler': {
            'level':'INFO',
            # 'class': 'handlers.TimedRotatingFileHandler',
            'class':'logger.multiprocessing_log.MultiProcessTimedRotatingFileHandler',
            'formatter':'fileFormatter',
            # TimedRotatingFileHandler args:
            # (filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False）
            'filename':'/home/avatar/Desktop/access.log',
            'when':'MIDNIGHT',
            'interval':1,
            'backupCount':60,
            'encoding':None,
            'delay':False,
            'utc':False
        },
        'ErrorTimedRotatingFileHandler': {
            'level':'ERROR',
            # 'class': 'handlers.TimedRotatingFileHandler',
            'class':'logger.multiprocessing_log.MultiProcessTimedRotatingFileHandler',
            'formatter':'fileFormatter',
            # TimedRotatingFileHandler args:
            # (filename, when='h', interval=1, backupCount=0, encoding=None, delay=False, utc=False）
            'filename':'/home/avatar/Desktop/error.log',
            'when':'MIDNIGHT',
            'interval':1,
            'backupCount':60,
            'encoding':None,
            'delay':False,
            'utc':False
        },
    },
    'loggers': {
        'vsing': {
            'level': 'NOTSET',
            'handlers': ['consoleHandler'],
            'propagate': False,
        },
        'all': {
            'level':'NOTSET',
            'handlers': [
                'AccessTimedRotatingFileHandler',
                'ErrorTimedRotatingFileHandler'
            ],
            'propagate':True,
        },
        'access': {
            'level': 'INFO', # 小于该级别的日志不输出
            'handlers': ['AccessTimedRotatingFileHandler'],
            'propagate': True,
        },
        'error': {
            'level': 'ERROR',
            'handlers': ['ErrorTimedRotatingFileHandler'],
            'propagate': True,
        },
    },
    'root': {
        'level': 'NOTSET',
        'handlers': ['consoleHandler'],
        'propagate': False,
    },
}

logging.config.dictConfig(LOG_CONFIG)
