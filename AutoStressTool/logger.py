import os
import logging.config

# Get a directory of your current test path
test_path = os.getcwd()
# A path of your runtime logs
log_path = os.path.join(test_path, r'Logs')

# create a Logs folder if it does not exist
if not os.path.exists(log_path):
    os.makedirs(log_path)

# Instantiate dash connection with system logger
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("fileLogger")

# Level     Numeric value   When it’s used
# NOTSET    0                           
# DEBUG	    10              Detailed information, typically of interest only when diagnosing problems.
# INFO	    20	            Confirmation that things are working as expected.
# WARNING	30	            An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
# ERROR	    40	            Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL	50	            A serious error, indicating that the program itmsg may be unable to continue running.

def debug_msg(msg):
    """
    The function help to distribute debug msg to many channel as logger, console

    Args:
        msg: message debug need to write/send/print
    """

    # DEBUG 10 logging.debug()
    logger.debug(str(msg))

def info_msg(msg):
    """
    The function help to distribute info msg to many channel as logger, console
            
    Args:
        msg: message info need to write/send/print
    """

    # INFO 20 logging.info()
    logger.info(str(msg))

def warning_msg(msg):
    """
    The function help to distribute warning msg to many channel as logger, console

    Args:
        msg: message warning need to write/send/print
    """

    # WARNING 30 logging.warning()
    logger.warning(str(msg))

def error_msg(msg):
    """
    The function help to distribute error msg to many channel as logger, console

    Args:
        msg: message error need to write/send/print
    """

    # ERROR	40 logging.error()
    logger.error(str(msg)) 

def handle_exception(msg):
    """
    The function help to distribute exception msg to many channel as logger, console

    Args:
        msg: message exception need to write/send/print
    """

    # logging.error(exc_info=True)
    logger.exception(str(msg))

def critical_msg(msg):
    """
    The function help to distribute critical msg to many channel as logger, console

    Args:
        msg: message critical need to write/send/print
    """

    # CRITICAL 50 logging.critical()
    logger.critical(str(msg))