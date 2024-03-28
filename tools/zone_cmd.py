import coloredlogs, logging, verboselogs
logger = verboselogs.VerboseLogger(__name__)
# logger.basicConfig(level=logger.DEBUG)
coloredlogs.install(level='VERBOSE')

from datetime import datetime

def supervise(brain_class):
    '''
    Stop and wait for HUBS supervision

    Continue auto Nav after approval, prepare for take over at anytime 

     - pause nav
     - supervise_mode = True
     - wait for approval signal
     - when supervise is done, supervise_mode = False

    '''
    logger.info(f"supervise {brain_class} { datetime.now().strftime('%Y%m%d: %H%M%S')}")

def cross_road( nav):
    '''
    Stop and wait for HUBS supervision and orient towards specific direction(e.. nearest traffic light in front of the BOT)
    '''
    logging.info('cross_road' + ' ' + datetime.now().strftime('%Y%m%d: %H%M%S'))

def take_over( nav):
    '''
    Stop and wait for remote control from HUBS
    '''
    logging.info('take_over' + ' ' + datetime.now().strftime('%Y%m%d: %H%M%S'))

