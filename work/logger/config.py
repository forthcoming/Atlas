# -*- coding: utf-8 -*-
import sys
import logging.config

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'fileFormatter': {
            'format':'[%(levelname)s] %(asctime)s [%(module)s - %(filename)s - line:%(lineno)d] [proc:%(process)d] %(message)s',
            # 'datefmt': '%m-%d-%Y %H:%M:%S,%f',
        },
        'default': {
            'format':'%(asctime)s %(levelname)s [%(name)s: %(lineno)s] -- %(message)s',
            # 'datefmt': '%m-%d-%Y %H:%M:%S,%f'
        },
    },
    'handlers': {
        'consoleHandler': {
            'class': 'logging.StreamHandler',  # 输出到控制台
            'formatter': 'default',
            # logging.StreamHandler args
            'stream': sys.stdout
        },
        'AccessTimedRotatingFileHandler': {
            # 'level': 'INFO',  # 也可以设置级别
            # 'class': 'handlers.TimedRotatingFileHandler',
            'class':'multiprocessing_log.MultiProcessTimedRotatingFileHandler',
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
            # 'class': 'handlers.TimedRotatingFileHandler',
            'class':'multiprocessing_log.MultiProcessTimedRotatingFileHandler',
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
    'root': {  # 保证所有的logger都会在屏幕上显示
        'level': 'NOTSET',  # 只输出level大于等于WARNING
        'handlers': ['consoleHandler'],
        'propagate': False,
    },
    'loggers': {
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
}

logging.config.dictConfig(LOG_CONFIG)
