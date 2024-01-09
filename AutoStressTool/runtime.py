import os
import logging.config
import tkinter as tk
from tkinter import messagebox

# Get a directory of your current test path
test_path = os.getcwd()
# A path of your runtime logs
log_path = os.path.join(test_path, r'logs')

# create a Logs folder if it does not exist
if not os.path.exists(log_path):
    os.makedirs(log_path)

# Instantiate dash connection with system logger
logging.config.fileConfig("logging.conf")
logger = logging.getLogger("fileLogger")

# Level     Numeric value   When it’s used
# NOTSET    0                           
# DEBUG	    10              Detailed information, typically of interest only when diagnosing problems.
# INFO      20              Confirmation that things are working as expected.
# WARNING   30              An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.
# ERROR     40              Due to a more serious problem, the software has not been able to perform some function.
# CRITICAL  50              A serious error, indicating that the program may be unable to continue running.

def debug_msg(message):
    """
    The function help to distribute debug message to many channel as logger, console

    Args:
        msg: message debug need to write/send/print
    """

    #print(message)  no needed with debug level
    # DEBUG 10 logging.debug()
    logger.debug(message)

def info_msg(message):
    """
    The function help to distribute info message to many channel as logger, console
            
    Args:
        message: message info need to write/send/print
    """

    print(message)
    # INFO 20 logging.info()
    logger.info(message)

def warning_msg(message):
    """
    The function help to distribute warning message to many channel as logger, console

    Args:
        message: message warning need to write/send/print
    """

    print(message)
    # WARNING 30 logging.warning()
    logger.warning(message)

def error_msg(message):
    """
    The function help to distribute error message to many channel as logger, console

    Args:
        message: message error need to write/send/print
    """

    print(message)
    # ERROR	40 logging.error()
    logger.error(message)

def handle_exception(message):
    """
    The function help to distribute exception message to many channel as logger, console

    Args:
        message: message exception need to write/send/print
    """

    print(message)
    # logging.error(exc_info=True)
    logger.exception(message)

def critical_msg(message):
    """
    The function help to distribute critical message to many channel as logger, console

    Args:
        message: message critical need to write/send/print
    """

    print(message)
    # CRITICAL 50 logging.critical()
    logger.critical(message)

def info_msgbox(message):
    """
    Displays a info message using Tkinter messagebox and logs the message.

    Args:
        message (str): The info message to be displayed.
    """
    
    print(message)
    # INFO 20 logging.info()
    logger.info(message)
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Information", message)

def warning_msgbox(message):
    """
    Displays a warning message using Tkinter messagebox and logs the message.

    Args:
        message (str): The warning message to be displayed.
    """
    
    print(message)
    # WARNING 30 logging.warning()
    logger.warning(message)
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Warning", message)

def error_msgbox(message):
    """
    Displays a error message using Tkinter messagebox and logs the message.

    Args:
        message (str): The error message to be displayed.
    """
    
    print(message)
    # ERROR	40 logging.error()
    logger.error(message)
    
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Error", message)