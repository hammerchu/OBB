import logging
from datetime import datetime

def supervise(a, b, c, d):
    '''
    Stop and wait for HUBS supervision

    '''
    logging.info('supervise' + ' ' +  datetime.now().strftime('%Y%m%d: %H%M%S'))

def cross_road():
    '''
    
    '''
    logging.info('cross_road' + ' ' + datetime.now().strftime('%Y%m%d: %H%M%S'))


def tunnel():
    '''
   
    '''
    logging.info('tunnel' + ' ' + datetime.now().strftime('%Y%m%d: %H%M%S'))


