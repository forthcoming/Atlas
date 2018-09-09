import logging

class Log:
    def __init__(self,level=logging.INFO, name='track.log'):
        '''
        logger.debug('this is debug info')
        logger.info('this is information')
        logger.warn('this is warning message')
        logger.error('this is error message')
        logger.critical('this is critical message')
        '''
        logging.basicConfig(
            filename=name,
            filemode='a',
            # format='%(asctime)s %(filename)s %(lineno)d %(process)s %(levelname)s %(module)s %(message)s',
            format='%(asctime)s line:%(lineno)d pid:%(process)s level:%(levelname)s message:%(message)s\n',
            datefmt='%Y-%m-%d %H:%M:%S %p',
            level=level,
        )
        logging.root.name=__name__
    def __call__(self,f):
        def wrapper(*args):
            try:
                return f(*args)
            except Exception as e:
                logging.exception(e)
        return wrapper
