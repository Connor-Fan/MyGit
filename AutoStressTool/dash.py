import os
import json
import runtime
import datetime
import ctypes
from ctypes import wintypes
from locale import getdefaultlocale
from subprocess import run

def runcmd(cmd):
    """
    To run a cmd, and return status, output and error messages

    Args:
        cmd: it is used for running in command line

    Returns:
        (bool, str, str): return code, output, error message
    """

    try:
        subprocess = run(cmd, shell=True, capture_output=True)
        return_code = subprocess.returncode

        language, encoding = getdefaultlocale()

        if language == 'en_US':
            std_out = subprocess.stdout.decode('utf-8', errors='ignore')
            std_err = subprocess.stderr.decode('utf-8', errors='ignore')
        elif language == 'zh_TW':
            std_out = subprocess.stdout.decode('big5', errors='ignore')
            std_err = subprocess.stderr.decode('big5', errors='ignore')

    except Exception as err:
        runtime.handle_exception(f'Can not run the cmd of {cmd}! Error: {err}')
        return 1, None, None

    return return_code, std_out, std_err

def read_txt_file_to_string(src):
    """
    To read a txt file and return as a single string.

    Args:
        src(str): file name including path

    Returns:
        (bool, str): return code, the content of a txt file
    """

    if not os.path.exists(src):
        runtime.error_msg(f'Can not find the file at the specified path of {src}')
        return 1, None

    try:
        # Reads a txt file and creates string data
        with open(src, 'r', encoding='utf-8') as fin:
            data = fin.read()

    except Exception as err:
        runtime.handle_exception(f'Can not read the file of {src}! Error: {err}')
        return 1, None

    return 0, data

def read_txt_file_to_list(src):
    """
    To read a txt file and return as a list of lines.

    Args:
        src(str): file name including path

    Returns:
        (bool, str): return code, the content of a txt file
    """

    if not os.path.exists(src):
        runtime.error_msg(f'Can not find the file at the specified path of {src}')
        return 1, None

    try:
        # Reads a txt file and creates string data
        with open(src, 'r', encoding='utf-8') as fin:
            data = [line.strip() for line in fin.readlines()]

    except Exception as err:
        print(f'Cannot read the file of {src}! Error: {err}')
        return 1, None

    return 0, data

def read_json_file(src):
    """
    To read a json file

    Args:
        src(str): file name including path

    Returns:
        (bool, str): return code, the content of a json file
    """

    if not os.path.exists(src):
        runtime.error_msg(f'Can not find the file at the specified path of {src}')
        return 1, None

    try:
        # Reads a json file and creates dicts
        with open(src, 'r', encoding='utf-8') as fin:
            json_dict = json.load(fin)

    except Exception as err:
        runtime.handle_exception(f'Can not read the file of {src}! Error: {err}')
        return 1, None

    return 0, json_dict

def write_json_file(src, json_dict):
    """
    To write dicts to be a json file

    Args:
        src(str): file name including path
        json_dict(dict): dictionary containing data

    Returns:
        (bool): false if successful, true otherwise.
    """

    try:
        # Writes dicts as a json file
        with open(src, 'w', encoding='utf-8') as fout:
            json.dump(json_dict, fout)

    except Exception as err:
        runtime.handle_exception(f'Can not write the json file {src}! Error: {err}')
        return 1

    return 0

def check_power():
    """
    Retrieves the system power status, indicating whether the system is plugged in or unplugged.

    Returns:
        (int, int): A tuple representing the system power status where:
            - The first element is an error code (0 for success, 1 for error).
            - The second element is the ACLineStatus indicating whether the system is plugged in (1) or unplugged (0).
    """

    class SYSTEM_POWER_STATUS(ctypes.Structure):
        _fields_ = [
            ('ACLineStatus', wintypes.BYTE),
            ('BatteryFlag', wintypes.BYTE),
            ('BatteryLifePercent', wintypes.BYTE),
            ('SystemStatusFlag', wintypes.BYTE),
            ('BatteryLifeTime', wintypes.DWORD),
            ('BatteryFullLifeTime', wintypes.DWORD),
        ]

    try:
        SYSTEM_POWER_STATUS_P = ctypes.POINTER(SYSTEM_POWER_STATUS)

        GetSystemPowerStatus = ctypes.windll.kernel32.GetSystemPowerStatus
        GetSystemPowerStatus.argtypes = [SYSTEM_POWER_STATUS_P]
        GetSystemPowerStatus.restype = wintypes.BOOL

        status = SYSTEM_POWER_STATUS()
        if not GetSystemPowerStatus(ctypes.pointer(status)):
            raise ctypes.WinError()

        ac_line_status_msg = "Plugged in" if status.ACLineStatus == 1 else "Unplugged"
        runtime.info_msg(f'ACLineStatus: {status.ACLineStatus}({ac_line_status_msg})')

        return 0, status.ACLineStatus

    except Exception as err:
        runtime.handle_exception(f'Error getting system power status: {err}')
        return 1, None

def set_system_time():
    """
    Sets the system time, resetting the seconds to zero.

    This function retrieves the current system time, resets the seconds to zero,
    and then sets the system time using the Windows API SetLocalTime.

    Returns:
        int: An error code indicating the success (0) or failure (1) of the operation.
    """

    # Define the SYSTEMTIME structure
    class SYSTEMTIME(ctypes.Structure):
        _fields_ = [
            ( 'wYear', wintypes.WORD ),
            ( 'wMonth', wintypes.WORD ),
            ( 'wDayOfWeek', wintypes.WORD ),
            ( 'wDay', wintypes.WORD ),
            ( 'wHour', wintypes.WORD ),
            ( 'wMinute', wintypes.WORD ),
            ( 'wSecond', wintypes.WORD ),
            ( 'wMilliseconds', wintypes.WORD ),
    ]

    try:
        # Get the current system time
        current_time = datetime.datetime.now()
        # Reset the seconds to zero
        reset_time = current_time.replace(second=0, microsecond=0)
        # Create a SYSTEMTIME object
        system_time = SYSTEMTIME(
            wYear=reset_time.year,
            wMonth=reset_time.month,
            wDayOfWeek=reset_time.weekday(),  # Adjust to weekday
            wDay=reset_time.day,
            wHour=reset_time.hour,
            wMinute=reset_time.minute,
            wSecond=reset_time.second,
            wMilliseconds=0,  # Assuming milliseconds are not used
        )
        # Create a SYSTEMTIME object
        result = ctypes.windll.kernel32.SetLocalTime(ctypes.byref(system_time))
        if result == 0:
            raise ctypes.WinError()

        runtime.info_msg(f'System time set to: {reset_time}')  
        return 0

    except Exception as err:
        runtime.handle_exception(f'Error setting system time: {err}')
        return 1