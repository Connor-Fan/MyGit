import os
import sys
import time
import psutil
import argparse
import datetime
import pyautogui
import battery, dash, mylog
from pywinauto import Application

# Globals section: define global variables in here

# Tool version
tool_version = "1.7.0"
# Python compiler version
python_version = "3.8.10"
# UIAutomationCore.dll of product version
product_version = "22621.2134"

# Get a directory of your current test path
test_path = os.getcwd()
# Get a directory of your user path
user_path = os.path.expanduser('~')
# Get a directory of your startup path
startup_path = os.path.join(user_path.replace('\\', '/'), "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup").replace('\\', '/')
# PwrTest folder path
pwrtest_folder_path = os.path.join(test_path, r'PwrTest')
# DeviceCompare folder path
device_compare_folder_path = os.path.join(test_path, r'DeviceCompareTest')
# LogFile folder, it is created by DeviceCompare
device_compare_log_path = os.path.join(test_path, r'DeviceCompareTest\LogFile')
# DevList folder, it is created by DeviceCompare
device_list_path = os.path.join(test_path, r'DeviceCompareTest\DevList')
# AutoStress path
tools_dir = os.path.join(user_path, r"Desktop\AutoStressTool")

# Batch file name
batch_filename = f'{os.path.splitext(os.path.basename(__file__))[0]}.bat'
# Batch file path
batch_file_path = os.path.join(startup_path, batch_filename)
# ui_handles.txt path
device_compare_ui_handle_path = os.path.join(tools_dir, r'Logs\UI_handles.txt')
# pwrtestlog.log path
pwrtestlog_path = os.path.join(tools_dir, r'PwrTest\pwrtestlog.log')
# _DeviceManager_List.txt path
devicemanager_list_path = os.path.join(tools_dir, r'DeviceCompareTest\DevList\_DeviceManager_List.txt')
# DeviceCompare path
device_compare_path = os.path.join(tools_dir, r'DeviceCompareTest\DeviceCompare.exe')
# PwrTest.exe path
pwrtest_path = os.path.join(tools_dir, r"PwrTest\pwrtest.exe")
# PlatCfg64W.exe path
platcfgw_exe_path = os.path.join(tools_dir, r"PlatCfg64W\PlatCfg64W.exe")
# PlatCfg2W64.exe path
platcfg2w_exe_path = os.path.join(tools_dir, r"PlatCfg64W\PlatCfg2W64.exe")
# The json file to save temporary values (command line arguments, ...)
current_state_path = os.path.join(test_path, "current_state.json")

# Default of standby (times)
default_standby = 0
# Default of standby time (in second)
default_standby_sec = 60
# Default of hibernate (times)
default_hibernate = 0
# Default of hibernate time (in second)
default_hibernate_sec = 60
# Default of warm boot (times)
default_warm_boot = 0
# Default time in second of warm boot
default_warm_boot_sec = 60
# Default of cold boot (times)
default_cold_boot = 0
# Default time in second of cold boot
default_cold_boot_sec = 120
# Default stop devices
default_stop_dev = None

def failstop(dev, count):
    """
    To check devices fail or not
    
    Args:
        dev(str), count(int): devices that you want to stop, a counter of counting power cycle
        
    Returns:
        (bool, bool): return code, stop flag
    """
    
    stop_flag = False
    
    if not os.path.exists(device_list_path):
        mylog.error_msg(f'Can not find the folder of {device_list_path}')
        return 1, None

    devlist_dc_pass_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_DC_Pass.txt')
    devlist_ac_pass_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_AC_Pass.txt')
    devlist_dc_fail_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_DC_Fail.txt')
    devlist_ac_fail_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_AC_Fail.txt')

    if count == 0 or dev == None:
        return 0, stop_flag
    elif os.path.exists(devlist_dc_pass_path):
        return 0, stop_flag
    elif os.path.exists(devlist_ac_pass_path):
        return 0, stop_flag
    elif os.path.exists(devlist_dc_fail_path):
        fail_devlist = dash.read_txt_file(devlist_dc_fail_path)
    elif os.path.exists(devlist_ac_fail_path):
        fail_devlist = dash.read_txt_file(devlist_ac_fail_path)
    else:
        mylog.error_msg(f'Can not find the txt file of {devlist_dc_pass_path}')
        mylog.error_msg(f'Can not find the txt file of {devlist_ac_pass_path}')
        mylog.error_msg(f'Can not find the txt file of {devlist_dc_fail_path}')
        mylog.error_msg(f'Can not find the txt file of {devlist_ac_fail_path}')
        mylog.debug_msg(f'The counter of curr_dict[stress_cycle] is {count}')
        return 1, None
    
    devlis = dash.read_txt_file(devicemanager_list_path)
    
    if devlis != fail_devlist:
        for i in range(0, len(dev)):
            # for stopping all devices
            if dev[i] == "all":
                print(f'Find out devices get lost on your system')
                mylog.info_msg(f'Find out devices get lost on your system')
                stop_flag = True
                return 0, stop_flag 
            # for devices lost
            elif dev[i] not in fail_devlist and dev[i] in devlis:
                print(f'Find out {dev[i]} get lost on your system')
                mylog.info_msg(f'Find out {dev[i]} get lost on your system')
                stop_flag = True
                return 0, stop_flag
            # for devices add
            elif dev[i] in fail_devlist and dev[i] not in devlis:
                print(f'Find out {dev[i]} is added on your system')
                mylog.info_msg(f'Find out {dev[i]} is added on your system')
                stop_flag = True
                return 0, stop_flag
            # for exceptions
            else:
                mylog.debug_msg(f'Do not find that you want to stop the device of {dev[i]}, and go next one to keep finding.')
                # no need return 1, None

        print(f'Please contact with the tool author of Kanan')
        mylog.error_msg(f'Please contact with the tool author of Kanan')
        return 1, None

    else:
        mylog.debug_msg('All devices do not get lost and not need to stopping the auto script')

    return 0, stop_flag

def create_batch_file(cmd):
    """
    To create a batch file in the startup folder
    
    Args:
        cmd(str): it is used for running in command line
        
    Returns:
        (bool): false if successful, true otherwise.
    """

    # Remove old batch file
    if os.path.exists(batch_file_path):
        os.remove(batch_file_path)

    cmd_dir = f'cd {tools_dir}'
        
    try:
        with open(batch_file_path, "w", encoding='utf-8') as f:
            f.write(f'@echo off\ncd {tools_dir}\n{cmd}')
            f.close()
            
    except Exception as err:
        mylog.handle_exception(f'Can not create a batch file of {batch_file_path}! Error: {err}')
        return 1

    return 0

def check_uac_flag():
    """
    To check EnableLUA is enabled or disabled
    
    Returns:
        (bool, bool): return code, a flag of EnableLUA
    """

    rc, std_out, std_err = dash.runcmd('REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v EnableLUA')
    if rc:
        mylog.error_msg(f'Can not get the value of EnableLUA! Error: {std_err}')
        return 1, None
        
    lines = std_out.split('\n')
    for line in lines:
        if line == '':
            break
        if 'EnableLUA' in line:
            if '0x1' in line:
                mylog.info_msg(f'EnableLUA is enabled. Set EnableLUA to be True')
                uac_flag = True
            elif '0x0' in line:
                mylog.info_msg(f'EnableLUA is disabled. Set EnableLUA to be False')
                uac_flag = False
    
    return 0, uac_flag

def get_sleep_state():
    """
    To check to know ms, s3, s4 are supported or not by this system

    Returns:
        tuple(bool, bool, bool)
    """
    
    is_ms_supported = False
    is_s3_supported = False
    is_s4_supported = False

    rc, std_out, std_err = dash.runcmd('powercfg -a')
    if rc:
        mylog.error_msg(f'Can not get the sleep state! Error: {std_err}')
        return 1

    lines = std_out.split('\n')
    for line in lines:
        line = line.strip().lower()
        if line == '':
            break
        if 'standby' in line:
            if 's3' in line:
                is_s3_supported = True
            elif 's0' in line:
                is_ms_supported = True
        if 'hibernate' in line:
            is_s4_supported = True
    
    return is_ms_supported, is_s3_supported, is_s4_supported

def parse_stop_argument():
    """
    To parse stop argument from command line
    
    Returns:
        tuple (str)
    """

    stop_dev = default_stop_dev

    if args.stop is None or len(args.stop) == 0:
        pass  # Using default stop values
    elif args.stop == 'all':
        pass
    elif len(args.stop) >= 1:
        stop_dev = args.stop
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.stop}')
        return 1, None

    return 0, stop_dev
    
def parse_cold_boot_argument():
    """
    To parse cold boot argument from command line
    
    Returns:
        tuple(int, int)
    """
    
    cold_boot_num = default_cold_boot
    cold_boot_time = default_cold_boot_sec

    if args.cb is None or len(args.cb) == 0:
        pass  # Using default cb values
    elif len(args.cb) == 1:
        cold_boot_num = abs(args.cb[0])
    elif len(args.cb) == 2:
        cold_boot_num = abs(args.cb[0])
        cold_boot_time = abs(args.cb[1])
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.cb}')
        return 1, None, None 

    mylog.info_msg(f'cold_boot_num = {cold_boot_num}, cold_boot_time = {cold_boot_time}')

    ACLineStatus, _, _, _, _, _ = battery.check_power()
    if cold_boot_time >= 120 and cold_boot_num > 0:
        if ACLineStatus:
            return 0, cold_boot_num, cold_boot_time
        else:
            print(f'Please insert your AC for Auto On Day')
            mylog.error_msg(f'Please insert your AC for Auto On Day')
            return 1, _, _
    elif cold_boot_time < 120 and cold_boot_num > 0:
        print(f'For CB, sleep time must be more than 120s')
        mylog.error_msg(f'For CB, sleep time must be more than 120s')
        return 1, _, _
    elif ACLineStatus:
        # return the defautl value of 0, 120.
        return 0, cold_boot_num, cold_boot_time
    else:
        print(f'Your system is DC only! Please check whether you need to insert AC or not')
        # return the defautl value of 0, 120.
        return 0, cold_boot_num, cold_boot_time

def parse_warm_boot_argument():
    """
    To parse warm boot argument from command line
    
    Returns:
        tuple(int, int)
    """
    
    warm_boot_num = default_warm_boot
    warm_boot_time = default_warm_boot_sec
   
    if args.wb is None or len(args.wb) == 0:
        pass  # Using default wb values
    elif len(args.wb) == 1:
        warm_boot_num = abs(args.wb[0])
    elif len(args.wb) == 2:
        warm_boot_num = abs(args.wb[0])
        warm_boot_time = abs(args.wb[1])
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.wb}')
        return 1, None, None 

    mylog.info_msg(f'warm_boot_num = {warm_boot_num}, warm_boot_time = {warm_boot_time}')

    return 0, warm_boot_num, warm_boot_time

def parse_hibernate_argument():
    """
    To parse hibernate argument from command line
    
    Returns:
        tuple(int, int)
    """

    hibernate_num = default_hibernate
    hibernate_time = default_hibernate_sec

    if args.hibernate is None or len(args.hibernate) == 0:
        pass  # Using default wb values
    elif len(args.hibernate) == 1:
        hibernate_num = abs(args.hibernate[0])
    elif len(args.hibernate) == 2:
        hibernate_num = abs(args.hibernate[0])
        hibernate_time = abs(args.hibernate[1])
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.hibernate}')
        return 1, None, None 

    mylog.info_msg(f'hibernate_num = {hibernate_num}, hibernate_time = {hibernate_time}')
    
    return 0, hibernate_num, hibernate_time

def parse_standby_argument():
    """
    To parse standby argument from command line
    
    Returns:
        tuple(int, int)
    """
    
    standby_num = default_standby
    standby_time = default_standby_sec

    if args.standby is None or len(args.standby) == 0:
        pass  # Using default standby values
    elif len(args.standby) == 1:
        standby_num = abs(args.standby[0])
    elif len(args.standby) == 2:
        standby_num = abs(args.standby[0])
        standby_time = abs(args.standby[1])
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.standby}')
        return 1, None, None 
 
    mylog.info_msg(f'standby_num = {standby_num}, standby_time = {standby_time}')
    
    return 0, standby_num, standby_time

def parse_cmdline(cmd_line=None):
    """
    To parse args from command line

    Returns:    
        arguments of the user input
    """

    parser = argparse.ArgumentParser(description='Dell Stress Tests')

    # Custom args
    parser.add_argument('--cleanup', dest='cleanup', default=None, type=str, choices=['Yes', 'No'],
                    help='Perform cleanup tasks, including removing temporary files, resetting power settings, and cleaning Windows and BIOS event logs.\n'
                        'When set to "Yes," the --backup_cleanup option is also enabled; when set to "No," the --backup_cleanup option is disabled.')
    parser.add_argument('--backup_cleanup', default=None, action='store_true', help='[Internal Use Only] Clean Windows and BIOS event logs (Not for general use).')
    parser.add_argument('--setup', default=None, action='store_true', help='Set up system settings like UAC, memory dump settings, and Windows power plan')
    parser.add_argument('--auto', default=None, action='store_true', help='Run DeviceCompare automatically')
    parser.add_argument('--stop', nargs='+', dest='stop', default=[], type=str,
                    help='If DeviceCompare gets negetive results, the autoscript will be stopped.\n'
                        'Usage: --stop all or --stop "SanDisk USB"\n'
                        'Note: Use with --auto to enable the stop functionality. Without --auto, the stop feature will not be active.')
    parser.add_argument('--standby', nargs=2, dest='standby', default=[], type=int, metavar=('iterations', 'duration'),
                    help='Enter standby mode multiple times, each time staying in standby for a specified duration.\n'
                        'Usage: --standby 3 60 (up to 2 iterations)\n'
                        'This means standby for 3 times, each time for 60 seconds before waking up the system.')
    parser.add_argument('--hibernate', nargs=2, dest='hibernate', default=[], type=int, metavar=('iterations', 'duration'),
                    help='Enter hibernation mode multiple times, each time staying in hibernation for a specified duration.\n'
                        'Usage: --hibernate 3 60 (up to 2 iterations)\n'
                        'This means hibernate for 3 times, each time for 60 seconds before waking up the system.')
    parser.add_argument('--wb', nargs=2, dest='wb', default=[], type=int, metavar=('iterations', 'duration'),
                    help='Perform warm boot multiple times, each time restarting the system after a specified duration.\n'
                        'Usage: --wb 3 60 (up to 2 iterations)\n'
                        'This means warm boot for 3 times, each time waiting for 60 seconds before restarting the system.')
    parser.add_argument('--cb', nargs=2, dest='cb', default=[], type=int, metavar=('iterations', 'duration'),
                    help='Perform cold boot multiple times, each time powering down the system for a specified duration before waking it up.\n'
                        'Usage: --cb 3 120 (up to 2 iterations)\n'
                        'This means cold boot for 3 times, each time powering down for 120 seconds before waking up the system.')
    if cmd_line:
        args = parser.parse_args(cmd_line)
    else:
        args = parser.parse_args()

    return args

def get_process_id_by_name(name):
    """
    To get process id of application by name

    Args:
        name(str): application name need to get process id

    Returns:
        (bool, int/str): return code, process id/error string
    """

    pid = None
    try:
        for proc in psutil.process_iter():
            if proc.name() == name:
                pid = proc.pid
                break

    except Exception as err:
        mylog.handle_exception(f'get_process_id_by_name: {str(err)}')
        return 1, f'get_process_id_by_name: {str(err)}'

    return 0, pid

def generate_test_mode(args):
    """
    Generate a list of valid test args based on the given args.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        list: A list of valid test args.
    """

    arr_test_args = []

    if args.cleanup is None or len(args.cleanup) == 0:   
        pass  # Using default cleanup values
    elif args.cleanup in ['Yes', 'No']:
        arr_test_args.append(f'--cleanup {args.cleanup}')
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.cleanup}')
        return 1, []  # Return an empty list and return code 1

    if args.backup_cleanup is not None:
        arr_test_args.append(f'--backup_cleanup')

    if args.setup is not None:
        arr_test_args.append(f'--setup')

    if args.auto is not None:
        arr_test_args.append(f'--auto')

    if args.stop is not None and len(args.stop) > 0:
        arr_test_args.append(f'--stop')

    if args.standby is not None and len(args.standby) > 0:
        arr_test_args.append(f'--standby')

    if args.hibernate is not None and len(args.hibernate) > 0:
        arr_test_args.append(f'--hibernate')

    if args.wb is not None and len(args.wb) > 0:
        arr_test_args.append(f'--wb')

    if args.cb is not None and len(args.cb) > 0:
        arr_test_args.append(f'--cb')
    
    mylog.debug_msg(f'The current args are {arr_test_args}')

    return 0, arr_test_args  # Return the list of valid args and return code 0

def set_current_test_mode(test_args, count, device):
    """
    To write the current args into a json file
    
    Args:
        test_args (list): List of valid test args.
        count (int): Stress cycle count.
        device (str): Device to stop.

    Returns:
        int: Return code (0 if successful, 1 if errors occurred).
    """
    
    curr_dict = {}

    if os.path.exists(current_state_path):
        curr_dict = dash.read_json_file(current_state_path)
        if curr_dict is None:
            mylog.error_msg(f'The current dict is empty! Failed in dash.read_json_file()! The file path is {current_state_path}')
            return 1

        curr_dict['curr_test_args'] = test_args
        curr_dict['stress_cycle'] = count
        curr_dict['stop_device'] = device

        mylog.debug_msg(f'curr_test_args = {test_args}, stress_cycle = {count}, stop_device = {device}')
    else:
        curr_dict = {'curr_test_args': test_args, 'stress_cycle': count, 'stop_device': device}
        mylog.debug_msg(f'curr_test_args = {test_args}, stress_cycle = {count}, stop_device = {device}')

    # Check backup flag
    if args.cleanup == 'Yes' or args.backup_cleanup:
        curr_dict['backup_flag'] = True
    else:
        curr_dict['backup_flag'] = False

    curr_dict['standby_num'] = standby_num
    curr_dict['standby_time'] = standby_time
    curr_dict['hibernate_num'] = hibernate_num
    curr_dict['hibernate_time'] = hibernate_time
    curr_dict['warm_boot_num'] = wb_num
    curr_dict['warm_boot_time'] = wb_time
    curr_dict['cold_boot_num'] = cb_num
    curr_dict['cold_boot_time'] = cb_time

    if dash.write_json_file(current_state_path, curr_dict):
        mylog.error_msg(f'Can not write the current args into {current_state_path}')
        return 1

    return 0

def cleanup():
    """
    To remove log files, kill running DeviceCompare APP, clean up Windows and BIOS event logs
    
    Returns:
        (bool): no need return 
    """
    
    print("Running clean up..., Please wait...")
    
    # clean up log files in the device compare folder
    try:
        if os.path.exists(device_list_path):
            file_list = os.listdir(device_list_path)
            for f in file_list:
                print(f'remove the old file of {f}')
                os.unlink(os.path.join(device_list_path, f))
                
    except Exception as err:
        print(f'Can not clean up files in {device_list_path}! Error: {str(err)}')
        # no need return 1
    
    # clean up log files in the device compare folder
    try:
        if os.path.exists(device_compare_log_path):
            file_list = os.listdir(device_compare_log_path)
            for f in file_list:
                print(f'remove the old file of {f}')
                os.unlink(os.path.join(device_compare_log_path, f))
                
    except Exception as err:
        print(f'Can not clean up files in {device_compare_log_path}! Error: {str(err)}')
        # no need return 1

    # clean up log files in the debuglog folder
    try:
        if os.path.exists("C:\Compal\DeviceCompare\debuglog"):
            file_list = os.listdir("C:\Compal\DeviceCompare\debuglog")
            for f in file_list:
                print(f'Remove the old file of {f}')
                os.unlink(os.path.join("C:\Compal\DeviceCompare\debuglog", f))

    except Exception as err:
        print(f'Can not clean up files in C:\Compal\DeviceCompare\debuglog! Error: {str(err)}')
        # no need return 1

    # clean up config files in the device compare folder
    try:
        if os.path.exists(device_compare_folder_path):
            file_list = os.listdir(device_compare_folder_path)
            for f in file_list:
                if ".txt" in f:
                    print(f'Remove the old file of {f}')
                    os.unlink(os.path.join(device_compare_folder_path, f)) 

    except Exception as err:
        print(f'Can not clean up files in {device_compare_folder_path}! Error: {str(err)}')
        # no need return 1

    # clean up config files in the pwrtest folder
    try:
        if os.path.exists(pwrtest_folder_path):
            file_list = os.listdir(pwrtest_folder_path)
            for f in file_list:
                # do not need to remove EXE file
                if ".exe" in f:      
                    pass
                else:
                    print(f'Remove the old file of {f}')
                    os.unlink(os.path.join(pwrtest_folder_path, f)) 

    except Exception as err:
        print(f'Can not clean up files in {pwrtest_folder_path}! Error: {str(err)}')
        # no need return 1

    # kill the running DeviceCompare.exe
    try:
        rc, pid_devicecompare = get_process_id_by_name("DeviceCompare.exe")

        if rc == 0 and pid_devicecompare is not None:
            print(f'Start turning of Device Compare...')
            app = Application(backend="uia").connect(title_re="Device Compare")
            app.kill()

    except Exception as err:
        print(f'Can not kill running DeviceCompare app! Error: {str(err)}')
        # no need return 1

    # remove old batch files
    try:
        if os.path.exists(batch_file_path):
            print(f'Remove the old batch file of {batch_file_path}')
            os.unlink(batch_file_path)

    except Exception as err:
        print(f'Can not clean up files in {startup_path}! Error: {str(err)}')
        # no need return 1

    # remove old json files
    try:
        if os.path.exists(current_state_path):
            print(f'Remove the olde json file of {current_state_path}')
            os.unlink(current_state_path)

    except Exception as err:
        print(f'Can not clean up files in {test_path}! Error: {str(err)}')
        # no need return 1

    print(f'Start resetting power plans...')
    mylog.info_msg("Reset power plans...")
    # reset and restore power plans to default settings   
    rc, _, std_err = dash.runcmd('powercfg restoredefaultschemes')
    if rc:
        print(f'Can not reset power plans! Error: {std_err}')
        mylog.error_msg(f'Can not reset power plans! Error: {std_err}')
        # no need return 1
    else:
        print(f'Reset restore power plans is successful!')

    print(f'Clean up Windows Events now...')
    mylog.info_msg("Clean up Windows Events now...")
    # clean up Windows Event, like Application, System, Setup and Security
    rc, std_out, std_err = dash.runcmd('wevtutil cl Application')
    if rc:
        print(f'Can not clean up the Windows Event of Application! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of Application! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of Application is successful!')

    rc, std_out, std_err = dash.runcmd('wevtutil cl System')
    if rc:
        print(f'Can not clean up the Windows Event of System! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of System! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of System is successful!')

    rc, std_out, std_err = dash.runcmd('wevtutil cl Setup')
    if rc:
        print(f'Can not clean up the Windows Event of Setup! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of Setup! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of Setup is successful!')

    rc, std_out, std_err = dash.runcmd('wevtutil cl Security')
    if rc:
        print(f'Can not clean up the Windows Event of Security! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of Security! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of Security is successful!')

    print(f'Clean up BIOS Events now...')
    # set the platcfg cmd for cleaning BIOS log
    cmd_bioslog = f"{platcfg2w_exe_path} -set BiosLogClear=Clear"
    
    rc, _, std_err = dash.runcmd(cmd_bioslog)
    if rc == 1 and std_err is not None:
        print(f'Can not clean up BIOS logs with the cmd of {cmd_bioslog}! Error: {std_err}')
        mylog.error_msg(f'Can not clean up BIOS logs with the cmd of {cmd_bioslog}! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up BIOS logs is successful!')
        
    # set the platcfg cmd for cleaning thermal log
    cmd_thermallog = f"{platcfg2w_exe_path} -set ThermalLogClear=Clear"
    
    rc, _, std_err = dash.runcmd(cmd_thermallog)
    if rc == 1 and std_err is not None:
        print(f'Can not clean up thermal logs with the cmd of {cmd_thermallog}! Error: {std_err}')
        mylog.error_msg(f'Can not clean up thermal logs with the cmd of {cmd_thermallog}! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up thermal logs is successful!')

    # set the platcfg cmd for cleaning power log
    cmd_powerlog = f"{platcfg2w_exe_path} -set PowerLogClear=Clear"
    
    rc, _, std_err = dash.runcmd(cmd_powerlog)
    if rc == 1 and std_err is not None:
        print(f'Can not clean up power logs with the cmd of {cmd_powerlog}! Error: {std_err}')
        mylog.error_msg(f'Can not clean up power logs with the cmd of {cmd_powerlog}! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up power logs is successful!')
        
    return 0

def backup_cleanup():
    """
    To clean Windows and BIOS event logs
    
    Returns:
        (bool): no need return 
    """

    print(f'Clean up Windows Events now...')
    mylog.info_msg("Clean up Windows Events now...")
    # clean up Windows Event, like Application, System, Setup and Security
    rc, std_out, std_err = dash.runcmd('wevtutil cl Application')
    if rc:
        print(f'Can not clean up the Windows Event of Application! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of Application! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of Application is successful!')

    rc, std_out, std_err = dash.runcmd('wevtutil cl System')
    if rc:
        print(f'Can not clean up the Windows Event of System! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of System! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of System is successful!')

    rc, std_out, std_err = dash.runcmd('wevtutil cl Setup')
    if rc:
        print(f'Can not clean up the Windows Event of Setup! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of Setup! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of Setup is successful!')

    rc, std_out, std_err = dash.runcmd('wevtutil cl Security')
    if rc:
        print(f'Can not clean up the Windows Event of Security! Error: {std_err}')
        mylog.error_msg(f'Can not clean up the Windows Event of Security! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up the Windows Event of Security is successful!')

    print(f'Clean up BIOS Events now...')
    # set the platcfg cmd for cleaning BIOS log
    cmd_bioslog = f"{platcfg2w_exe_path} -set BiosLogClear=Clear"
    
    rc, _, std_err = dash.runcmd(cmd_bioslog)
    if rc == 1 and std_err is not None:
        print(f'Can not clean up BIOS logs with the cmd of {cmd_bioslog}! Error: {std_err}')
        mylog.error_msg(f'Can not clean up BIOS logs with the cmd of {cmd_bioslog}! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up BIOS logs is successful!')
        
    # set the platcfg cmd for cleaning thermal log
    cmd_thermallog = f"{platcfg2w_exe_path} -set ThermalLogClear=Clear"
    
    rc, _, std_err = dash.runcmd(cmd_thermallog)
    if rc == 1 and std_err is not None:
        print(f'Can not clean up thermal logs with the cmd of {cmd_thermallog}! Error: {std_err}')
        mylog.error_msg(f'Can not clean up thermal logs with the cmd of {cmd_thermallog}! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up thermal logs is successful!')

    # set the platcfg cmd for cleaning power log
    cmd_powerlog = f"{platcfg2w_exe_path} -set PowerLogClear=Clear"
    
    rc, _, std_err = dash.runcmd(cmd_powerlog)
    if rc == 1 and std_err is not None:
        print(f'Can not clean up power logs with the cmd of {cmd_powerlog}! Error: {std_err}')
        mylog.error_msg(f'Can not clean up power logs with the cmd of {cmd_powerlog}! Error: {std_err}')
        # no need return 1
    else:
        print(f'Clean up power logs is successful!')
        
    return 0

def backup_args(curr_dict):
    """
    To get curr test args from a json file, and backup these args for next boot using

    Args:
        curr_dict(str): current test mode
        
    Returns:
        (bool, str): return code, backup test mode
    """
    
    curr_args = []  
    # get current args
    arr_args = curr_dict['curr_test_args']

    if arr_args is not None and len(arr_args) > 0:
        for i in range(0, len(arr_args)):
            if i > 0:
                curr_args.append(' ')   
            curr_args.append(arr_args[i])
    else:
        mylog.error_msg(f'Can not read curr_dict["curr_test_args"]! Error: arr_args is {arr_args}')
        return 1, None
    
    mylog.debug_msg(f'In backup_args, curr_args = {curr_args}')
    return 0, curr_args

def setup(curr_dict):
    """
    Any initialization will be done here
    
    Returns:
        (bool): no need return
    """

    print(f'Start setting up environment params...')
    mylog.info_msg("Start setting up environment params...")
    
    rc, _, std_err = dash.runcmd('powercfg -change -standby-timeout-dc 0')
    if rc:
        print(f'Can not set the powercfg of -standby-timeout-dc 0! Error: {std_err}')
        mylog.error_msg(f'Can not set the powercfg of -standby-timeout-dc 0! Error: {std_err}')
        # no need return 1
    else:
        print(f'Set the powercfg of -standby-timeout-dc 0 is successful!')
        
    rc, std_out, std_err = dash.runcmd('powercfg -change -standby-timeout-ac 0')
    if rc:
        print(f'Can not set the powercfg of -standby-timeout-ac 0! Error: {std_err}')
        mylog.error_msg(f'Can not set the powercfg of -standby-timeout-ac 0! Error: {std_err}')
        # no need return 1
    else:
        print(f'Set the powercfg of -standby-timeout-ac 0 is successful!')
        
    rc, std_out, std_err = dash.runcmd('powercfg -change -monitor-timeout-dc 0')
    if rc:
        print(f'Can not set the powercfg of -monitor-timeout-dc 0! Error: {std_err}')
        mylog.error_msg(f'Can not set the powercfg of -monitor-timeout-dc 0! Error: {std_err}')
        # no need return 1
    else:
        print(f'Set the powercfg of -monitor-timeout-dc 0 is successful!')
        
    rc, std_out, std_err = dash.runcmd('powercfg -change -monitor-timeout-ac 0')
    if rc:
        print(f'Can not set the powercfg of -monitor-timeout-ac 0! Error: {std_err}')
        mylog.error_msg(f'Can not set the powercfg of -monitor-timeout-ac 0! Error: {std_err}')
        # no need return 1
    else:
        print(f'Set the powercfg of -monitor-timeout-ac 0 is successful!')
 
    # config memory dump settings in Startup and Recovery 
    rc, std_out, std_err = dash.runcmd('wmic recoveros set AutoReboot = False')
    if rc:
        print(f'Can not set the checkbox of Automatically Restart to be False! Error: {std_err}')
        mylog.error_msg(f'Can not set the checkbox of Automatically Restart to be False! Error: {std_err}')
        return 1
    else:
        print(f'Set the checkbox of Automatically Restart to be False is successful!')

    rc, std_out, std_err = dash.runcmd('wmic recoveros set DebugInfoType = 1')
    if rc:
        print(f'Can not set the memory dump to be complete! Error: {std_err}')
        mylog.error_msg(f'Can not set the memory dump to be complete! Error: {std_err}')
        return 1
    else:
        print(f'Set the memory dump to be complete is successful!')
 
    rc, uac_flag = check_uac_flag()
    if rc:
        mylog.error_msg(f'Can not get the UAC flag with check_uac_flag()')
        return 1

    if uac_flag:
        # define a string variable 
        backup_cmd = ''
        
        rc, _, std_err= dash.runcmd('reg.exe ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f')
        if rc:
            mylog.error_msg(f'UAC can not be disabled! Error: {std_err}')
            return 1
        
        rc, curr_args = backup_args(curr_dict)
        if rc:
            mylog.error_msg(f'Can not get the current args with backup_args()')
            return 1
        
        for args in curr_args:
            if str(args) == '--cleanup Yes':
                backup_cmd = backup_cmd + str(args) + ' '
            elif str(args) == '--cleanup No':
                backup_cmd = backup_cmd + str(args) + ' '
            elif str(args) == '--setup':
                backup_cmd = backup_cmd + str(args) + ' '
            elif str(args) == '--auto':
                backup_cmd = backup_cmd + str(args) + ' '
            else:
                pass

        # get devices that you want to stop when they fail
        stop_dev = curr_dict['stop_device']  

        if stop_dev != None and len(stop_dev) > 0:
            new_dev = ''
            for i in range(0, len(stop_dev)):
                if len(stop_dev) == 1:
                    new_dev = stop_dev[0]
                elif len(stop_dev) > 1 and i < len(stop_dev) - 1:
                    new_dev = new_dev + stop_dev[i] + ' '
                elif i == len(stop_dev) - 1:
                    new_dev = new_dev + stop_dev[i]
                else:
                    mylog.error_msg(f'Return error! Failed in initialling str. String lenth is {len(stop_dev)}')
                    return 1
        else:
            new_dev = stop_dev

        if new_dev is not None and len(new_dev) > 0:
            backup_cmd = f'{os.path.basename(sys.argv[0])} ' + f'{backup_cmd}' + f'--stop {new_dev} --standby {standby_num} {standby_time} --hibernate {hibernate_num} {hibernate_time} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        else:
            backup_cmd = f'{os.path.basename(sys.argv[0])} ' + f'{backup_cmd}' + f'--standby {standby_num} {standby_time} --hibernate {hibernate_num} {hibernate_time} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'

        mylog.info_msg(f'The backup cmd is {backup_cmd}')
        rc = create_batch_file(backup_cmd)    
        if rc:
            mylog.error_msg(f'Can not create a batch file with create_batch_file()')
            return 1

        print('Restart your system for reseting UAC settings')
        time.sleep(5)
        cmd = "shutdown -r -t 0 -f"
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            mylog.error_msg(f'Can not shut down the system with cmd of {cmd}')
            return 1  
    else:
        print(f'UAC is {uac_flag}. We donot need to be disabled again')
        # no need return 1, err_msg

    return 0

def do_standby():
    """
    To place system in standby mode
        
    Returns:
        (bool): tuple(int[0, 1])
    """
    
    # Place the system into Standby, wait 30 seconds, then resume. Repeat three times
    if standby_num > 0 and standby_time > 0:
        for i in range(0, standby_num):
            # set the delay time of 65s for waitting DeviceCompare is ready
            for i in range(65, 0, -1):
                print(f'Wait {i}s to do standby...', end='\r')
                time.sleep(1)

            # reflash dict data from current_state.json
            curr_dict = dash.read_json_file(current_state_path)

            # Determine whether to perform backup based on the user's input value
            if curr_dict['backup_flag'] == True:
                backup_cleanup()
            else:
                print(f'Do not need to clean up Event Logs...')
                mylog.info_msg(f'Do not need to cleanup Event Logs...')

            print(f'Running a standby now...')

            cmd = f'{pwrtest_path} /cs /s:standby /c:1 /d:90 /p:{standby_time}'
            print(f'Place your system in standby mode... with cmd of {cmd}')
            mylog.info_msg(f'Place your system in standby mode... with cmd of {cmd}')

            time.sleep(5)

            rc, _, std_err = dash.runcmd(cmd)

            if rc == 1 and std_err is not None:
                mylog.error_msg(f'Can not place your system in standby mode with cmd of {cmd}! Error: {std_err}')
                return 1

            pwrtestlog = dash.read_txt_file(pwrtestlog_path)
            if  pwrtestlog is not None and pwrtestlog != 1:
                print(pwrtestlog)
                #mylog.info_msg(f'{pwrtestlog}')
            else:
                mylog.error_msg(f'Can not read pwrtestlog of {pwrtestlog_path}')
                return 1
            
            # for counting stress cycle
            if os.path.exists(current_state_path):
                curr_dict = dash.read_json_file(current_state_path)
                count = curr_dict['stress_cycle'] + 1
                mylog.info_msg(f'The current cycle of stress is {count}')
            else:
                count = 0

            rc, stop_dev = parse_stop_argument()
            if rc:
                mylog.error_msg(f'Return error! Failed in parse_stop_argument()')
                return 1

            if set_current_test_mode(arr_test_args, count, stop_dev):
                mylog.error_msg(f'Return error! Failed in set_current_test_mode()')
                return 1

            if args.stop:
                # set the delay time of 65s for waitting DeviceCompare is ready
                for i in range(65, 0, -1):
                    print(f'Wait {i}s for DeviceCompare is ready...', end='\r')
                    time.sleep(1)

                print(f'DeviceCompare is ready now..., scanning all devices to check the specific devices that you want to stop')
                time.sleep(5)

                rc, stop_flag = failstop(stop_dev, count)
                if rc:
                    mylog.error_msg(f'Test Failed in failstop()')
                    return 1
                elif stop_flag:
                    print(f'Find out the failed devices and stop running the auto script')
                    mylog.info_msg(f'Find out the failed devices and stop running the auto script')
                    return 1
                else:
                    print(f'All devices are working well')
                    mylog.info_msg(f'All devices are working well')
                    # no need return 0

    return 0

def do_hibernate():
    """
    To place system in hibernate mode
    
    Returns:
        (bool): tuple(int[0, 1])
    """
    
    # Place the system into S4, wait 60 seconds, then resume. Repeat three times
    if hibernate_num > 0 and hibernate_time > 0:
        for i in range(0, hibernate_num):
            # set the delay time of 65s for waitting DeviceCompare is ready
            for i in range(65, 0, -1):
                print(f'Wait {i}s to do hibernate...', end='\r')
                time.sleep(1)
            
            # reflash dict data from current_state.json
            curr_dict = dash.read_json_file(current_state_path)

            # Determine whether to perform backup based on the user's input value
            if curr_dict['backup_flag'] == True:
                backup_cleanup()
            else:
                print(f'Do not need to clean up Event Logs...')
                mylog.info_msg(f'Do not need to cleanup Event Logs...')

            print(f'Running a hibernate now...')
            
            _, _, is_s4_supported = get_sleep_state()
            if not is_s4_supported:
                _, _, std_err = dash.runcmd('powercfg -H ON')
                _, _, is_s4_supported = get_sleep_state()
                if not is_s4_supported:
                    print('Sleep State, Hibernate (S4), is not enabled on this platform')
                    mylog.info_msg('Sleep State, Hibernate (S4), is not enabled on this platform')
                else:
                    # Place the system into hibernate, wait 60 seconds, then resume. Repeat three times
                    cmd = f'{pwrtest_path} /sleep /s:4 /c:1 /d:90 /p:{hibernate_time}'

                    print(f'Place system in s:4 mode...by command line: {cmd}')
                    mylog.info_msg(f'Place system in Hibernate (s:4) mode by command line: {cmd}')

                    time.sleep(5)
                    rc, _, std_err = dash.runcmd(cmd)
                    if rc == 1 and std_err is not None:
                        mylog.error_msg(f'Can not place your system in hibernate mode with cmd of {cmd}! Error: {std_err}')
                        return 1
            else:
                mylog.info_msg('Sleep state S4 (Hibernate) is available in this system')
                # Place the system into Hibernate, wait 60 seconds, then resume. Repeat three times
                cmd = f'{pwrtest_path} /sleep /s:4 /c:1 /d:90 /p:{hibernate_time}'

                print(f'Place system in Hibernate mode...by command line: {cmd}')
                mylog.info_msg(f'Place system in Hibernate (s:4) mode by command line: {cmd}')

                time.sleep(5)
                rc, _, std_err = dash.runcmd(cmd)
                if rc == 1 and std_err is not None:
                    mylog.error_msg(f'Can not place your system in hibernate mode with cmd of {cmd}! Error: {std_err}')
                    return 1

            pwrtestlog = dash.read_txt_file(pwrtestlog_path)
            if  pwrtestlog is not None and pwrtestlog != 1:
                print(pwrtestlog)
                #mylog.info_msg(f'{pwrtestlog}')
            else:
                mylog.error_msg(f'Can not read pwrtestlog of {pwrtestlog_path}')
                return 1

            # for counting stress cycle
            if os.path.exists(current_state_path):
                curr_dict = dash.read_json_file(current_state_path)
                count = curr_dict['stress_cycle'] + 1
                mylog.info_msg(f'The current cycle of stress is {count}')
            else:
                count = 0

            rc, stop_dev = parse_stop_argument()
            if rc:
                mylog.error_msg(f'Return error! failed in parse_stop_argument()')
                return 1

            if set_current_test_mode(arr_test_args, count, stop_dev):
                mylog.error_msg(f'Return error! failed in set_current_test_mode()')
                return 1

            if args.stop:
                # set the delay time of 65s for waitting DeviceCompare is ready
                for i in range(65, 0, -1):
                    print(f'Wait {i}s for DeviceCompare is ready...', end='\r')
                    time.sleep(1)

                print(f'DeviceCompare is ready now..., scanning all devices to check the specific devices that you want to stop')
                time.sleep(5)
                
                rc, stop_flag = failstop(stop_dev, count)
                if rc:
                    mylog.error_msg(f'Test Failed in failstop()')
                    return 1
                elif stop_flag:
                    print(f'Find out the failed devices and stop running the auto script')
                    mylog.info_msg(f'Find out the failed devices and stop running the auto script')
                    return 1
                else:
                    print(f'All devices are working well')
                    mylog.info_msg(f'All devices are working well')
                    # no need return 0

    return 0

def do_warm_boot():
    """
    To place system in warm boot mode
    
    Returns:
        (bool): tuple(int[0, 1])
    """
    
    if wb_num > 0 and wb_time > 0:
        cmd = "shutdown -r -t 0 -f"

        time.sleep(5)
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            mylog.error_msg(f'Can not place your system in warmboot mode with cmd of {cmd}! Error: {std_err}')
            return 1

    return 0

def do_cold_boot():
    """
    To place system in cold boot mode
    
    Returns:
        (bool): tuple(int[0, 1])
    """

    if cb_num > 0 and cb_time > 0:
        # Update wake up timer
        cmd_wakeup = f"{platcfgw_exe_path} -w Auto_On:Daily"

        rc, _, std_err = dash.runcmd(cmd_wakeup)
        if rc == 1 and std_err is not None:
            mylog.error_msg(f'The wake up timer Failed in cmd of {cmd_wakeup}! Error: {std_err}')
            return 1
        # Command wakeup after shutdown according to specified number of minutes
        sleep_time_minutes = round(cb_time / 60)  # Minute
        cmd_wakeup = f'{platcfgw_exe_path} -w Auto_On_Time:{(datetime.datetime.now() + datetime.timedelta(minutes=+sleep_time_minutes)).strftime("%H:%M")} '

        # Run CMD wakeup
        rc, _, std_err = dash.runcmd(cmd_wakeup)
        if rc == 1 and std_err is not None:
            mylog.error_msg(f'The wake up timer Failed in cmd of {cmd_wakeup}! Error: {std_err}')
            return 1
        # CMD Shutdown
        cmd = "shutdown -s -t 0 -f"

        time.sleep(5)
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            mylog.error_msg(f'Can not place your system in coldboot mode with cmd of {cmd}! Error: {std_err}')
            return 1

    return 0

def test_teardown():
    """
    To reset your system state
    
    Returns:
        (bool): tuple(int[0, 1])
    """

    print(f'Start test teardown..., please wait...')
    mylog.info_msg("Start test teardown..., please wait...")

    # remove old batch files
    try:
        if os.path.exists(batch_file_path):
            print(f'remove the old batch file of {batch_file_path}')
            os.unlink(batch_file_path)

    except Exception as err:
        mylog.handle_exception(f'Can not clean files in {startup_path}! Error: {str(err)}')
        # no need return 1

    try:
        rc, pid_devicecompare = get_process_id_by_name("DeviceCompare.exe")

        if rc == 0 and pid_devicecompare is not None:
            app = Application(backend="uia").connect(title_re="Device Compare")
            main_window = app.window(title_re="Device Compare")
            # wait to be ready
            main_window.wait('visible')
            # initialize x, y coordinate
            pyautogui.moveTo(0, 0, duration=0.25)
            time.sleep(5)
            # stop
            main_window.child_window(title="Stop", auto_id="b_start", control_type="Button").click()
        else:
            mylog.info_msg(f'DeviceCompare is not working! Do not need to stop it')

    except Exception as ex:
        mylog.handle_exception(ex)
        # no need return 1

    print(f'End test teardown..., please close it')  
    mylog.info_msg("End test teardown..., please close it") 
    
    os.system("pause")
    
    return 0

def run_device_compare():
    """
    Automatically run DeveiveCompare.exe
    
    Returns:
        (bool): tuple(int[0, 1])
    """

    print("DeviceCompare is working now...")
    
    try:
        # Run DeviceCompare app
        app = Application(backend="uia").start(device_compare_path)
        main_window = app.window(title_re="Device Compare")
        # dump UI handles of DeviceCompare.
        # UnicodeEncodeError: 'charmap' codec can't encode character '\uffla'. It will be fixed on pywinauto 0.7.0
        #main_window.print_control_identifiers(filename=device_compare_ui_handle_path)
        # wait to be ready
        main_window.wait('visible')
        # initialize x, y coordinate
        pyautogui.moveTo(0, 0, duration=0.25)

        time.sleep(5)
        # reset
        main_window.child_window(title="Reset", auto_id="b_reset", control_type="Button").click()
        time.sleep(5)
        # sync
        main_window.child_window(title="Sync", auto_id="b_sync", control_type="Button").click()
        time.sleep(5)
        # start
        main_window.child_window(title="Start", auto_id="b_start", control_type="Button").click()

    except Exception as ex:
        mylog.handle_exception(ex)
        return 1
        
    return 0 
 
def test_main(args, dict):
    """
    Main test logic gets executed here
    
    Returns:
        (bool): tuple(int[0, 1])
    """

    mylog.info_msg(f'Test main with args: {args}')
   
    # get num/time of standby/hibernate/warm/cold boot and backup
    standby_num = curr_dict['standby_num']
    standby_time = curr_dict['standby_time']
    hibernate_num = curr_dict['hibernate_num']
    hibernate_time = curr_dict['hibernate_time']
    wb_num = curr_dict['warm_boot_num']
    wb_time = curr_dict['warm_boot_time']
    cb_num = curr_dict['cold_boot_num']
    cb_time = curr_dict['cold_boot_time']

    # get the current value of stress cycle
    count = curr_dict['stress_cycle']  
    # get devices that you want to stop when they fail
    stop_dev = curr_dict['stop_device']
    # get the backup flag, True or False
    backup = curr_dict['backup_flag']

    mylog.debug_msg(f'In test_main, stress_cycle = {count}')
    mylog.debug_msg(f'In test_main, stop_device = {stop_dev}')
    mylog.debug_msg(f'In test_main, backup_flag = {backup}')
    mylog.debug_msg(f'In test_main, standby_num = {standby_num}')
    mylog.debug_msg(f'In test_main, standby_time = {standby_time}')
    mylog.debug_msg(f'In test_main, hibernate_num = {hibernate_num}')
    mylog.debug_msg(f'In test_main, hibernate_time = {hibernate_time}')
    mylog.debug_msg(f'In test_main, warm_boot_num = {wb_num}')
    mylog.debug_msg(f'In test_main, warm_boot_time = {wb_time}')
    mylog.debug_msg(f'In test_main, cold_boot_num = {cb_num}')
    mylog.debug_msg(f'In test_main, cold_boot_time = {cb_time}')

    if wb_num > 0 and wb_time > 0:
        # set the delay time of wb_time for waitting DeviceCompare is ready
        for i in range(wb_time, 0, -1):
            print(f'Wait {i}s to do warm boot...', end='\r')
            time.sleep(1)

        print(f'Running a warm boot now...')
        time.sleep(5)
    elif cb_num > 0 and cb_time > 0:
        # set the delay time of 65s for waitting DeviceCompare is ready
        for i in range(65, 0, -1):
            print(f'Wait {i}s to do cold boot...', end='\r')
            time.sleep(1)

        print(f'Running a cold boot now...')
        time.sleep(5)
    else:
        # handle for finish test
        print(f'Finished {sys.argv[0]} rc=0')
        mylog.info_msg(f'Finished {sys.argv[0]} rc=0')
        # set the delay time of 65s for waitting DeviceCompare is ready
        for i in range(65, 0, -1):
            print(f'Wait {i}s to do test teardown...', end='\r')
            time.sleep(1)

        print(f'Running test teardown now...')
        time.sleep(5)
        return test_teardown()

    if count == standby_num + hibernate_num:
        count = count + 1
    elif args.stop:
        rc, stop_flag = failstop(stop_dev, count)
        if rc:
            mylog.error_msg(f'The test Failed in failstop()')
            return 1
        elif stop_flag:
            print(f'Find out the failed devices and stop running the auto script')
            mylog.info_msg(f'Find out the failed devices and stop running the auto script')
            return 1
        else:
            print(f'All devices are working well')
            mylog.info_msg(f'All devices are working well')
            # no need return 0

        count = count + 1
    else:
        count = count + 1

    if set_current_test_mode(arr_test_args, count, stop_dev):
        mylog.error_msg(f'Return error! Failed in set_current_test_mode()')
        return 1

    if stop_dev != None and len(stop_dev) > 0:
        new_dev = ''
        for i in range(0, len(stop_dev)):
            if len(stop_dev) == 1:
                new_dev = stop_dev[0]
            elif len(stop_dev) > 1 and i < len(stop_dev) - 1:
                new_dev = new_dev + stop_dev[i] + ' '
            elif i == len(stop_dev) - 1:
                new_dev = new_dev + stop_dev[i]
            else:
                mylog.error_msg(f'Return error! Failed in initialling str. String lenth is {len(stop_dev)}')
                return 1
    else:
        new_dev = stop_dev

    if wb_num > 0:
        wb_num = wb_num - 1  
        
        if (new_dev is not None and len(new_dev) > 0) and backup == True:
            cmd = f'{os.path.basename(sys.argv[0])} --backup_cleanup --stop {new_dev} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        elif (new_dev is not None and len(new_dev) > 0) and backup == False:
            cmd = f'{os.path.basename(sys.argv[0])} --stop {new_dev} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        elif (new_dev is None or len(new_dev) == 0) and backup == True:
            cmd = f'{os.path.basename(sys.argv[0])} --backup_cleanup --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        elif (new_dev is None or len(new_dev) == 0) and backup == False:
            cmd = f'{os.path.basename(sys.argv[0])} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        else:
            mylog.error_msg(f'Return error! Failed in setting the backup command of {cmd}')
            return 1

        if create_batch_file(cmd):
            mylog.error_msg(f'Return error! Failed in create_batch_file() with cmd of {cmd}')
            return 1

    elif cb_num > 0:
        cb_num = cb_num - 1

        if new_dev != None and backup == True:
            cmd = f'{os.path.basename(sys.argv[0])} --backup_cleanup --stop {new_dev} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        elif new_dev != None and backup == False:
            cmd = f'{os.path.basename(sys.argv[0])} --stop {new_dev} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        elif new_dev == None and backup == True:
            cmd = f'{os.path.basename(sys.argv[0])} --backup_cleanup --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        elif new_dev == None and backup == False:
            cmd = f'{os.path.basename(sys.argv[0])} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        else:
            mylog.error_msg(f'Return error! Failed in setting the backup command of {cmd}')
            return 1

        if create_batch_file(cmd) :
            mylog.error_msg(f'Return error! Failed in create_batch_file() with cmd of {cmd}')
            return 1

    # run backup_cleanup
    if args.backup_cleanup and backup_cleanup():
        mylog.error_msg(f'Return error! Failed in backup_cleanup()')
        return 1
    # run warmboot
    if args.wb and do_warm_boot():
        mylog.error_msg(f'Return error! Failed in do_warm_boot()')
        return 1
    # run coldboot      
    if args.cb and do_cold_boot():      
        mylog.error_msg(f'Return error! Failed in do_cold_boot()')
        return 1

    return 0

# Test Entry point
if __name__ == '__main__':
    # This is your entry point
    # Parse arguments
    # Calls to test_main(), test_teardown() done here.
    # Script should exit back to shell from here using sys.exit(rc)

    try:
        # show the basic information
        print("===========================================================================")
        print(f'Tool version {tool_version}, Python pakage {python_version}, Product version {product_version}')
        print("This is README.md, the class material's top-level user guide")
        print("Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g")
        print("===========================================================================")

        # parse arguments
        args = parse_cmdline()

        if args.cleanup:
            cleanup()

        # get time/num/device of stress
        rc, standby_num, standby_time = parse_standby_argument()
        if rc:
            print(f'Return error! Failed in parse_standby_argument()')
            raise Exception(f'Return error! Failed in parse_standby_argument()')

        rc, hibernate_num, hibernate_time = parse_hibernate_argument()
        if rc:
            print(f'Return error! Failed in parse_hibernate_argument()')
            raise Exception(f'Return error! Failed in parse_hibernate_argument()')

        rc, wb_num, wb_time = parse_warm_boot_argument()
        if rc:
            print(f'Return error! Failed in parse_warm_boot_argument()')
            raise Exception(f'Return error! Failed in parse_warm_boot_argument()')

        rc, cb_num, cb_time = parse_cold_boot_argument()
        if rc:
            print(f'Return error! Failed in parse_cold_boot_argument()')
            raise Exception(f'Return error! Failed in parse_cold_boot_argument()')

        rc, stop_dev = parse_stop_argument()
        if rc:
            print(f'Return error! Failed in parse_stop_argument()')
            raise Exception(f'Return error! Failed in parse_stop_argument()')

        # for counting stress cycle
        if os.path.exists(current_state_path):
            curr_dict = dash.read_json_file(current_state_path)
            count = curr_dict['stress_cycle']
            mylog.info_msg(f'The current cycle of stress is {count}')
        else:
            count = 0

        # back up current agrs, num and time
        rc, arr_test_args = generate_test_mode(args)
        if rc:
            print(f'Return error! Failed in generate_test_mode()')
            raise Exception(f'Return error! Failed in generate_test_mode()')

        if set_current_test_mode(arr_test_args, count, stop_dev):
            print(f'Return error! Failed in set_current_test_mode()')
            raise Exception(f'Return error! Failed in set_current_test_mode()')

        curr_dict = dash.read_json_file(current_state_path)

        if curr_dict == 1 or curr_dict is None:
            print(f'The current dict is empty! Failed in dash.read_json_file()! The file path is {current_state_path}')
            raise Exception(f'The current dict is empty! Failed in dash.read_json_file()! The file path is {current_state_path}')  

        # set environment
        if args.setup and setup(curr_dict):
            print(f'The test Failed in setup()')
            raise Exception(f'The test Failed in setup()')

        # run DeviceCompare
        if args.auto and run_device_compare():
            print(f'The test Failed in run_device_compare()')
            raise Exception(f'The test Failed in run_device_compare()')

        # run standby
        if args.standby and do_standby():
            print(f'The test Failed in do_standby()')
            raise Exception(f'The test Failed in do_standby()')

        # run hibernate
        if args.hibernate and do_hibernate():
            print(f'The test Failed in do_hibernate()')
            raise Exception(f'The test Failed in do_hibernate()')

        # reflash dict data from current_state.json
        curr_dict = dash.read_json_file(current_state_path)

        # Test main
        if test_main(args, curr_dict):
            print(f'The test Failed in test_main()')
            raise Exception(f'The test Failed in test_main()')

        #exit(rc)
    except Exception as ex:
        mylog.handle_exception(f'The test fails! Error: {ex}')
        mylog.handle_exception(f'Finished {sys.argv[0]} rc=1')
        test_teardown()
        #exit(1)