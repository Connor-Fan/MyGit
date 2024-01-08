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
tool_version = "1.5.0"
# Python compiler version
python_version = "3.11.0"
# UIAutomationCore.dll of product version
product_version = "10.0.22621.755"

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
            if dev[i] == "all" or dev[i] == 'ALL':
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

    if args.stop is None:
        pass
    elif args.stop == 'all' or args.stop == 'ALL':
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
   
    if args.cb is None:
        pass
    elif len(args.cb) == 1:
        cold_boot_num = abs(args.cb[0])
    elif len(args.cb) >= 2:
        cold_boot_num = abs(args.cb[0])
        cold_boot_time = abs(args.cb[1])
    else:
        mylog.error_msg(f'Please check the help info for how to type a correct arg! Error: {args.cb}')
        return 1, None, None 

    mylog.info_msg(f'cold_boot_num = {cold_boot_num}, cold_boot_time = {cold_boot_time}')
    
    ACLineStatus, _, _, _, _, _ = battery.check_power()

    if cold_boot_time >= 120 and ACLineStatus == 1:
        return 0, cold_boot_num, cold_boot_time
    else:
        print(f'For CB, sleep time must be more than 120s and insert AC')
        mylog.error_msg(f'For CB, sleep time must be more than 120s and insert AC')
        return 1, _, _

def parse_warm_boot_argument():
    """
    To parse warm boot argument from command line
    
    Returns:
        tuple(int, int)
    """
    
    warm_boot_num = default_warm_boot
    warm_boot_time = default_warm_boot_sec
   
    if args.wb is None:
        pass
    elif len(args.wb) == 1:
        warm_boot_num = abs(args.wb[0])
    elif len(args.wb) >= 2:
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

    if args.hibernate is None:
        pass
    elif len(args.hibernate) == 1:
        hibernate_num = abs(args.hibernate[0])
    elif len(args.hibernate) >= 2:
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

    if args.standby is None:
        pass
    elif len(args.standby) == 1:
        standby_num = abs(args.standby[0])
    elif len(args.standby) >= 2:
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
    parser.add_argument('--cleanup', default=None, action='store_true', help='Clean up all the temporary files, reset power settings and clean Windows event logs')
    parser.add_argument('--setup', default=None, action='store_true', help='Set up all the settings on your system, like UAC, memory dump settings, and Windows power plan')
    parser.add_argument('--auto', default=None, action='store_true', help='Run DeviceCompare automatically')
    parser.add_argument('--stop', nargs='*', dest='stop', default=None, type=str,
                        help='You can fill the specific devices that you want to stop them if DeviceCompare fails '
                             'Example: --stop all or --stop ALL, the script will stop on any devices if DeviceCompare fails '
                             'Example: --stop SanDisk USB, the script will stop on the specific device if SanDisk or USB fails '
                             'Note: The command of --stop has to use togther with --auto')
    parser.add_argument('--standby', nargs='*', dest='standby', default=None, type=int,
                        help='Example: --standby 3 60, it means standby total 3 times, each time stay in standby for '
                             '30 sec and wakeup system, default=%(default)s')
    parser.add_argument('--hibernate', nargs='*', dest='hibernate', default=None, type=int,
                        help='Example: --hibernate 3 60, it means hibernate total 3 times, each time stay in hibernate for '
                             '60 sec and wakeup system, default=%(default)s')
    parser.add_argument('--wb', nargs='*', dest='wb', default=None, type=int,
                        help='Example: --wb 3 60, it means warmboot total 3 times, each time stay in warmboot for '
                             '60 sec and restart system, default=%(default)s')
    parser.add_argument('--cb', nargs='*', dest='cb', default=None, type=int,
                        help='Example: --cb 3 120, it means do cold boot 3 times, each time power down in '
                             '120 sec and wakeup system default=%(default)s')
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

def generate_test_mode():
    """
    To generate a list of test args
    
    Returns:
        (str): a list of test args
    """

    arr_test_args = []
    
    if args.cleanup is not None:
        arr_test_args.append('--cleanup')

    if args.setup is not None:
        arr_test_args.append('--setup')

    if args.auto is not None:
        arr_test_args.append('--auto')

    if args.stop is not None:
        arr_test_args.append('--stop')

    if args.standby is not None and len(args.standby) > 0:
        arr_test_args.append('--standby')

    if args.hibernate is not None and len(args.hibernate) > 0:
        arr_test_args.append('--hibernate')

    if args.wb is not None and len(args.wb) > 0:
        arr_test_args.append('--wb')

    if args.cb is not None and len(args.cb) > 0:
        arr_test_args.append('--cb')
    
    mylog.info_msg(f'The current args are {arr_test_args}')

    return arr_test_args

def set_current_test_mode(test_args, count, dev, backup=False):
    """
    To write the current args into a json file
    
    Args:
        test_args(str): application name need to get process id
    
    Returns:
        (bool): return code
    """
    
    if os.path.exists(current_state_path):
        curr_dict = dash.read_json_file(current_state_path)
        if curr_dict is None:
            mylog.error_msg(f'The current dict is empty! Fail in dash.read_json_file()! The file path is {current_state_path}')
            return 1
        curr_dict['curr_test_args'] = test_args
        curr_dict['stress_cycle'] = count
        curr_dict['stop_device'] = dev
        mylog.debug_msg(f'curr_test_args = {test_args}, stress_cycle = {count}, stop_device = {dev}')
    else:
        curr_dict = {'curr_test_args': test_args, 'stress_cycle': 0, 'stop_device': dev}
        mylog.debug_msg(f'curr_test_args = {test_args}, stress_cycle = 0, stop_device = None')
    
    if backup:
        curr_dict['standby_num'] = standby_num
        curr_dict['standby_time'] = standby_time
        curr_dict['hibernate_num'] = hibernate_num
        curr_dict['hibernate_time'] = hibernate_time
        curr_dict['warm_boot_num'] = wb_num
        curr_dict['warm_boot_time'] = wb_time
        curr_dict['cold_boot_num'] = cb_num
        curr_dict['cold_boot_time'] = cb_time
        
    rc = dash.write_json_file(current_state_path, curr_dict)
    if rc:
        mylog.error_msg(f'Can not write the current args into {current_state_path}')
        return 1
        
    return 0

def check_dell_bios():
    """
    To check is dell system or not

    Returns:
        (bool): 0, None if your SUT is Dell bios, otherwise return 1
    """

    cmd = 'wmic bios get manufacturer'
    _, std_out, _ = dash.runcmd(cmd)
    if not 'Dell Inc' in std_out and not 'Alienware' in std_out:
        mylog.error_msg(f'Test main fail, must be Dell bios!')
        return 1

    return 0

def cleanup():
    """
    To remove log files and kill running DeviceCompare apps
    
    Returns:
        (bool): no need return 
    """
    
    print("clean up now...")
    
    # clean log files in the device compare folder
    try:
        if os.path.exists(device_list_path):
            file_list = os.listdir(device_list_path)
            for f in file_list:
                print(f'remove the old file of {f}')
                os.unlink(os.path.join(device_list_path, f))
                
    except Exception as err:
        print(f'Can not clean files in {device_list_path}! Error: {str(err)}')
        # no need return 1
    
    # clean log files in the device compare folder
    try:
        if os.path.exists(device_compare_log_path):
            file_list = os.listdir(device_compare_log_path)
            for f in file_list:
                print(f'remove the old file of {f}')
                os.unlink(os.path.join(device_compare_log_path, f))
                
    except Exception as err:
        print(f'Can not clean files in {device_compare_log_path}! Error: {str(err)}')
        # no need return 1

    # clean log files in the debuglog folder
    try:
        if os.path.exists("C:\Compal\DeviceCompare\debuglog"):
            file_list = os.listdir("C:\Compal\DeviceCompare\debuglog")
            for f in file_list:
                print(f'remove the old file of {f}')
                os.unlink(os.path.join("C:\Compal\DeviceCompare\debuglog", f))

    except Exception as err:
        print(f'Can not clean files in C:\Compal\DeviceCompare\debuglog! Error: {str(err)}')
        # no need return 1

    # clean config files in the device compare folder
    try:
        if os.path.exists(device_compare_folder_path):
            file_list = os.listdir(device_compare_folder_path)
            for f in file_list:
                if ".txt" in f:
                    print(f'remove the old file of {f}')
                    os.unlink(os.path.join(device_compare_folder_path, f)) 

    except Exception as err:
        print(f'Can not clean files in {device_compare_folder_path}! Error: {str(err)}')
        # no need return 1
        
    # clean config files in the pwrtest folder
    try:
        if os.path.exists(pwrtest_folder_path):
            file_list = os.listdir(pwrtest_folder_path)
            for f in file_list:
                # do not need to remove EXE file
                if ".exe" in f:      
                    pass
                else:
                    print(f'remove the old file of {f}')
                    os.unlink(os.path.join(pwrtest_folder_path, f)) 

    except Exception as err:
        print(f'Can not clean files in {pwrtest_folder_path}! Error: {str(err)}')
        # no need return 1

    # kill the running DeviceCompare.exe
    try:
        rc, pid_devicecompare = get_process_id_by_name("DeviceCompare.exe")

        if rc == 0 and pid_devicecompare is not None:
            app = Application(backend="uia").connect(title_re="Device Compare")
            app.kill()

    except Exception as err:
        print(f'Can not kill running DeviceCompare app! Error: {str(err)}')
        # no need return 1

    # remove old batch files
    try:
        if os.path.exists(batch_file_path):
            print(f'remove the old batch file of {batch_file_path}')
            os.unlink(batch_file_path)

    except Exception as err:
        print(f'Can not clean files in {startup_path}! Error: {str(err)}')
        # no need return 1

    # remove old json files
    try:
        if os.path.exists(current_state_path):
            print(f'remove the olde json file of {current_state_path}')
            os.unlink(current_state_path)

    except Exception as err:
        print(f'Can not clean files in {test_path}! Error: {str(err)}')
        # no need return 1

    print(f'Reset power plans...')
    mylog.info_msg("Reset power plans...")
    # reset and restore power plans to default settings   
    rc, _, std_err = dash.runcmd('powercfg restoredefaultschemes')
    if rc:
        print(f'Can not reset power plans! Error: {std_err}')
        mylog.error_msg(f'Can not reset power plans! Error: {std_err}')
        # no need return 1

    print(f'Clean Windows Events now...')
    mylog.info_msg("Clean Windows Events now...")
    # clean Windows Event, like Application, System, Setup and Security
    rc, std_out, std_err = dash.runcmd('wevtutil cl Application')
    if rc:
        print(f'Can not clean the Windows Event of Application! Error: {std_err}')
        mylog.error_msg(f'Can not clean the Windows Event of Application! Error: {std_err}')
        # no need return 1

    rc, std_out, std_err = dash.runcmd('wevtutil cl System')
    if rc:
        print(f'Can not clean the Windows Event of System! Error: {std_err}')
        mylog.error_msg(f'Can not clean the Windows Event of System! Error: {std_err}')
        # no need return 1

    rc, std_out, std_err = dash.runcmd('wevtutil cl Setup')
    if rc:
        print(f'Can not clean the Windows Event of Setup! Error: {std_err}')
        mylog.error_msg(f'Can not clean the Windows Event of Setup! Error: {std_err}')
        # no need return 1

    rc, std_out, std_err = dash.runcmd('wevtutil cl Security')
    if rc:
        print(f'Can not clean the Windows Event of Security! Error: {std_err}')
        mylog.error_msg(f'Can not clean the Windows Event of Security! Error: {std_err}')
        # no need return 1

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
    
    return 0, curr_args

def setup(curr_dict):
    """
    Any initialization will be done here
    
    Returns:
        (bool): no need return
    """

    mylog.info_msg("setup environment params...")
    
    rc, _, std_err = dash.runcmd('powercfg -change -standby-timeout-dc 0')
    if rc:
        mylog.error_msg(f'Can not set the powercfg of -standby-timeout-dc 0! Error: {std_err}')
        return 1
        
    rc, std_out, std_err = dash.runcmd('powercfg -change -standby-timeout-ac 0')
    if rc:
        mylog.error_msg(f'Can not set the powercfg of -standby-timeout-ac 0! Error: {std_err}')
        return 1
        
    rc, std_out, std_err = dash.runcmd('powercfg -change -monitor-timeout-dc 0')
    if rc:
        mylog.error_msg(f'Can not set the powercfg of -monitor-timeout-dc 0! Error: {std_err}')
        return 1
        
    rc, std_out, std_err = dash.runcmd('powercfg -change -monitor-timeout-ac 0')
    if rc:
        mylog.error_msg(f'Can not set the powercfg of -monitor-timeout-ac 0! Error: {std_err}')
        return 1
 
    # config memory dump settings in Startup and Recovery 
    rc, std_out, std_err = dash.runcmd('wmic recoveros set AutoReboot = False')
    if rc:
        mylog.error_msg(f'Can not set the checkbox of Automatically Restart to be False! Error: {std_err}')
        return 1

    rc, std_out, std_err = dash.runcmd('wmic recoveros set DebugInfoType = 1')
    if rc:
        mylog.error_msg(f'Can not set the memory dump to be complete! Error: {std_err}')
        return 1
 
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
            if str(args) == '--cleanup':
                backup_cmd = backup_cmd + str(args) + ' '
            elif str(args) == '--setup':
                backup_cmd = backup_cmd + str(args) + ' '
            elif str(args) == '--auto':
                backup_cmd = backup_cmd + str(args) + ' '
            else:
                pass

        # get devices that you want to stop when they fail
        stop_dev = curr_dict['stop_device']  
    
        if stop_dev != None:
            new_dev = ''
            for i in range(0, len(stop_dev)):
                if len(stop_dev) == 1:
                    new_dev = stop_dev[0]
                elif len(stop_dev) > 1 and i < len(stop_dev) - 1:
                    new_dev = new_dev + stop_dev[i] + ' '
                elif i == len(stop_dev) - 1:
                    new_dev = new_dev + stop_dev[i]
                else:
                    mylog.error_msg(f'Return error! Fail in initialling str. String lenth is {len(stop_dev)}')
                    return 1
        else:
            new_dev = stop_dev

        if new_dev != None:
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
                mylog.error_msg(f'Return error! Fail in parse_stop_argument()')
                return 1
            
            if set_current_test_mode(arr_test_args, count, stop_dev, backup=True):
                mylog.error_msg(f'Return error! Fail in set_current_test_mode()')
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
                    mylog.error_msg(f'Test fails in failstop()')
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

            if set_current_test_mode(arr_test_args, count, stop_dev, backup=True):
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
                    mylog.error_msg(f'Test fails in failstop()')
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
            mylog.error_msg(f'The wake up timer fails in cmd of {cmd_wakeup}! Error: {std_err}')
            return 1
        # Command wakeup after shutdown according to specified number of minutes
        sleep_time_minutes = round(cb_time / 60)  # Minute
        cmd_wakeup = f'{platcfgw_exe_path} -w Auto_On_Time:{(datetime.datetime.now() + datetime.timedelta(minutes=+sleep_time_minutes)).strftime("%H:%M")} '
    
        # Run CMD wakeup
        rc, _, std_err = dash.runcmd(cmd_wakeup)
        if rc == 1 and std_err is not None:
            mylog.error_msg(f'The wake up timer fails in cmd of {cmd_wakeup}! Error: {std_err}')
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

    mylog.info_msg("Start test teardown...")
    print(f'Start test teardown...')

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

    mylog.info_msg("End test teardown...")
    print(f'End test teardown...')   
    
    os.system("pause")
    
    return 0

def run_device_compare():
    """
    Automatically run DeveiveCompare.exe
    
    Returns:
        (bool): tuple(int[0, 1])
    """

    mylog.info_msg("DeviceCompare is working now...")
    
    try:
        # Run DeviceCompare app
        app = Application(backend="uia").start(device_compare_path)
        app.wait_cpu_usage_lower(threshold=10)
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
    
    if check_dell_bios():
        mylog.error_msg(f'Return error! Fail in check_dell_bios()')
        return 1
   
    # get num/time of standby/hibernate/warm/cold boot
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

    mylog.debug_msg(f'In test_main, stress_cycle = {count}')
    mylog.debug_msg(f'In test_main, stop_device = {stop_dev}')
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
            mylog.error_msg(f'The test fails in failstop()')
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

    if set_current_test_mode(arr_test_args, count, stop_dev, backup=True):
        mylog.error_msg(f'Return error! Fail in set_current_test_mode()')
        return 1
   
    if stop_dev != None:
        new_dev = ''
        for i in range(0, len(stop_dev)):
            if len(stop_dev) == 1:
                new_dev = stop_dev[0]
            elif len(stop_dev) > 1 and i < len(stop_dev) - 1:
                new_dev = new_dev + stop_dev[i] + ' '
            elif i == len(stop_dev) - 1:
                new_dev = new_dev + stop_dev[i]
            else:
                mylog.error_msg(f'Return error! Fail in initialling str. String lenth is {len(stop_dev)}')
                return 1
    else:
        new_dev = stop_dev

    if wb_num > 0:
        wb_num = wb_num - 1  
        
        if new_dev != None:
            cmd = f'{os.path.basename(sys.argv[0])} --stop {new_dev} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        else:
            cmd = f'{os.path.basename(sys.argv[0])} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
 
        if create_batch_file(cmd):
            mylog.error_msg(f'Return error! Fail in create_batch_file() with cmd of {cmd}')
            return 1

    elif cb_num > 0:
        cb_num = cb_num - 1

        if new_dev != None:
            cmd = f'{os.path.basename(sys.argv[0])} --stop {new_dev} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'
        else:
            cmd = f'{os.path.basename(sys.argv[0])} --wb {wb_num} {wb_time} --cb {cb_num} {cb_time}'

        if create_batch_file(cmd) :
            mylog.error_msg(f'Return error! Fail in create_batch_file() with cmd of {cmd}')
            return 1

    if args.wb:
        # run warmboot
        if do_warm_boot():
            mylog.error_msg(f'Return error! Fail in do_warm_boot()')
            return 1
            
    if args.cb:      
        # run coldboot
        if do_cold_boot():
            mylog.error_msg(f'Return error! Fail in do_cold_boot()')
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
            print(f'Return error! Fail in parse_standby_argument()')
            raise Exception(f'Return error! Fail in parse_standby_argument()')

        rc, hibernate_num, hibernate_time = parse_hibernate_argument()
        if rc:
            print(f'Return error! Fail in parse_hibernate_argument()')
            raise Exception(f'Return error! Fail in parse_hibernate_argument()')

        rc, wb_num, wb_time = parse_warm_boot_argument()
        if rc:
            print(f'Return error! Fail in parse_warm_boot_argument()')
            raise Exception(f'Return error! Fail in parse_warm_boot_argument()')

        rc, cb_num, cb_time = parse_cold_boot_argument()
        if rc:
            print(f'Return error! Fail in parse_cold_boot_argument()')
            raise Exception(f'Return error! Fail in parse_cold_boot_argument()')

        rc, stop_dev = parse_stop_argument()
        if rc:
            print(f'Return error! Fail in parse_stop_argument()')
            raise Exception(f'Return error! Fail in parse_stop_argument()')
        
        # for counting stress cycle
        if os.path.exists(current_state_path):
            curr_dict = dash.read_json_file(current_state_path)
            count = curr_dict['stress_cycle']
            mylog.info_msg(f'The current cycle of stress is {count}')
        else:
            count = 0

        # back up current agrs, num and time
        arr_test_args = generate_test_mode()
        if set_current_test_mode(arr_test_args, count, stop_dev, backup=True):
            print(f'Return error! Fail in set_current_test_mode()')
            raise Exception(f'Return error! Fail in set_current_test_mode()')

        curr_dict = dash.read_json_file(current_state_path)
        if curr_dict == 1 or curr_dict is None:
            print(f'The current dict is empty! Fail in dash.read_json_file()! The file path is {current_state_path}')
            raise Exception(f'The current dict is empty! Fail in dash.read_json_file()! The file path is {current_state_path}')  
       
        # set environment
        if args.setup:
            if setup(curr_dict):
                print(f'The test fails in setup()')
                raise Exception(f'The test fails in setup()')

        # run DeviceCompare
        if args.auto:
            if run_device_compare():
                print(f'The test fails in run_device_compare()')
                raise Exception(f'The test fails in run_device_compare()')

        # run standby
        if args.standby:
            if do_standby():
                print(f'The test fails in do_standby()')
                raise Exception(f'The test fails in do_standby()')
        
        # run hibernate
        if args.hibernate:
            if do_hibernate():
                print(f'The test fails in do_hibernate()')
                raise Exception(f'The test fails in do_hibernate()')
        
        # reflash dict data from current_state.json
        curr_dict = dash.read_json_file(current_state_path)
        
        # Test main
        if test_main(args, curr_dict):
            print(f'The test fails in test_main()')
            raise Exception(f'The test fails in test_main()')
        
        #exit(rc)
    except Exception as ex:
        mylog.handle_exception(f'The test fails! Error: {ex}')
        mylog.handle_exception(f'Finished {sys.argv[0]} rc=1')
        test_teardown()
        #exit(1)