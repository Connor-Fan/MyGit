import os
import sys
import time
import psutil
import argparse
import datetime
import pyautogui
import dash, runtime
from pywinauto import Application

# Globals section: define global variables here

# Disable Fail-Safe mode in pyautogui. This allows the mouse cursor to move to (0, 0) without triggering a Fail-Safe halt.
pyautogui.FAILSAFE = False
# Tool version
tool_version = "2.7.0"
# Python compiler version
python_version = "3.8.10"
# Get a directory of your current test path
test_path = os.getcwd()
# Get a directory of your user path
user_path = os.path.expanduser('~')
# Get a directory of your startup path
startup_path = os.path.join(user_path, "AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup")
# PwrTest folder path
pwrtest_folder_path = os.path.join(test_path, r"PwrTest")
# DeviceCompare folder path
device_compare_folder_path = os.path.join(test_path, r"DeviceCompareTest")
# LogFile folder, it is created by DeviceCompare
device_compare_log_path = os.path.join(test_path, r"DeviceCompareTest\LogFile")
# DevList folder, it is created by DeviceCompare
device_list_path = os.path.join(test_path, r"DeviceCompareTest\DevList")
# Temp folder, it is created by DeviceCompare
Temp_path = os.path.join(test_path, r"Temp")
# AutoStress path
tools_path = os.path.join(user_path, r"Desktop\AutoStressTool")

# Batch file name
batch_filename = f'{os.path.splitext(os.path.basename(__file__))[0]}.bat'
# Batch file path
batch_file_path = os.path.join(startup_path, batch_filename)
# ui_handles.txt path
device_compare_ui_handle_path = os.path.join(test_path, r"Logs\UI_handles.txt")
# pwrtestlog.log path
pwrtestlog_path = os.path.join(test_path, r"PwrTest\pwrtestlog.log")
# DeviceManager_List.txt path
devicemanager_list_path = os.path.join(test_path, r"DeviceCompareTest\DevList\DeviceManager_List.txt")
# DeviceCompare path
device_compare_path = os.path.join(test_path, r"DeviceCompareTest\DeviceCompare.exe")
# PwrTest.exe path
pwrtest_path = os.path.join(test_path, r"PwrTest\pwrtest.exe")
# PlatCfg64W.exe path
platcfgw_exe_path = os.path.join(test_path, r"MfgTools\PlatCfg64W.exe")
# PlatCfg2W64.exe path
platcfg2w_exe_path = os.path.join(test_path, r"MfgTools\PlatCfg2W64.exe")
# FPTW64.exe path
fpt_exe_path = os.path.join(test_path, r"FPT\FPTW64.exe")
# The json file to save temporary values (command line arguments, ...)
current_state_path = os.path.join(test_path, "current_state.json")
# Initialize backup parameters
delay_time = 0  # backup for args.delay
stop_device = None  # backup for args.stop
curr_dict = {}  # backup for current_state.json]
# backup_num[0] is for args.standby[0]
# backup_num[1] is for args.hibernate[0]
# backup_num[2] is for args.wb
# backup_num[3] is for args.cb[0]
# backup_num[4] is for args.greset
backup_num = [0, 0, 0, 0, 0]

def failstop(device, count):
    """
    Check whether devices have failed.

    Args:
        device (str): Devices that you want to stop.
        count (int): A counter for counting power cycles.

    Returns:
        (int, bool): Return code, stop flag.
    """

    stop_flag = False

    if not os.path.exists(device_list_path):
        runtime.error_msgbox(f'Can not find the folder of {device_list_path}')
        return 1, None

    devlist_dc_pass_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_DC_Pass.txt')
    devlist_ac_pass_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_AC_Pass.txt')
    devlist_dc_fail_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_DC_Fail.txt')
    devlist_ac_fail_path = os.path.join(test_path, f'DeviceCompareTest\DevList\DeviceManager_List_{count}_AC_Fail.txt')

    if count == 0 or device == None:
        return 0, stop_flag
    elif os.path.exists(devlist_dc_pass_path):
        return 0, stop_flag
    elif os.path.exists(devlist_ac_pass_path):
        return 0, stop_flag
    elif os.path.exists(devlist_dc_fail_path):
        fail_devlist = dash.read_txt_file(devlist_dc_fail_path)
        runtime.debug_msg(f'The fail devlist goes with {devlist_dc_fail_path}')
    elif os.path.exists(devlist_ac_fail_path):
        fail_devlist = dash.read_txt_file(devlist_ac_fail_path)
        runtime.debug_msg(f'The fail devlist goes with {devlist_dc_fail_path}')
    else:
        runtime.error_msgbox(f'Can not find the txt file of {devlist_dc_pass_path}')
        runtime.error_msgbox(f'Can not find the txt file of {devlist_ac_pass_path}')
        runtime.error_msgbox(f'Can not find the txt file of {devlist_dc_fail_path}')
        runtime.error_msgbox(f'Can not find the txt file of {devlist_ac_fail_path}')
        runtime.debug_msg(f'The counter of curr_dict[stress_cycle] is {count}')
        return 1, None

    devlis = dash.read_txt_file(devicemanager_list_path)

    if devlis != fail_devlist:
        for i in range(0, len(device)):
            # for stopping all devices
            if device[i].lower() == "all":
                runtime.info_msg(f'Find out devices get lost on your system')
                stop_flag = True
                return 0, stop_flag 
            # for devices lost
            elif device[i] not in fail_devlist and device[i] in devlis:
                runtime.info_msg(f'Find out {device[i]} get lost on your system')
                stop_flag = True
                return 0, stop_flag
            # for devices add
            elif device[i] in fail_devlist and device[i] not in devlis:
                runtime.info_msg(f'Find out {device[i]} is added on your system')
                stop_flag = True
                return 0, stop_flag
            else:
                runtime.debug_msg(f'Do not find that you want to stop the device of {device[i]}, and goes with next one to keep finding')
    else:
        runtime.info_msg('All devices remain connected, and there is no need to stop the auto script')

    return 0, stop_flag

def create_batch_file(cmd):
    """
    Create a batch file in the startup folder

    Args:
        cmd(str): it is used for running in command line
        
    Returns:
        (bool): false if successful, true otherwise.
    """

    # Remove old batch file
    if os.path.exists(batch_file_path):
        os.remove(batch_file_path)

    cmd_dir = f'cd {tools_path}'
        
    try:
        with open(batch_file_path, "w", encoding='utf-8') as f:
            f.write(f'@echo off\ncd {tools_path}\n{cmd}')
            f.close()

    except Exception as err:
        runtime.error_msgbox(f'Can not create a batch file of {batch_file_path}! Error: {err}')
        return 1

    return 0

def check_uac_flag():
    """
    Check EnableLUA is enabled or disabled

    Returns:
        (bool, bool): return code, a flag of EnableLUA
    """

    rc, std_out, std_err = dash.runcmd('REG QUERY HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Policies\System\ /v EnableLUA')
    if rc == 1 and std_err is not None:
        runtime.error_msgbox(f'Can not retrieve the value of EnableLUA! Error: {std_err}')
        return 1, None

    lines = std_out.split('\n')
    for line in lines:
        if line == '':
            break
        if 'EnableLUA' in line:
            if '0x1' in line:
                runtime.info_msg(f'EnableLUA is enabled. Setting EnableLUA to be True')
                uac_flag = True
            elif '0x0' in line:
                runtime.info_msg(f'EnableLUA is disabled. Setting EnableLUA to be False')
                uac_flag = False

    return 0, uac_flag

def get_sleep_state():
    """
    Check to know ms, s3, s4 are supported or not by this system

    Returns:
        tuple(bool, bool, bool)
    """

    is_ms_supported = False
    is_s3_supported = False
    is_s4_supported = False

    rc, std_out, std_err = dash.runcmd('powercfg -a')
    if rc == 1 and std_err is not None:
        runtime.error_msgbox(f'Can not retrieve the sleep state! Error: {std_err}')
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

def parse_cmdline(cmd_line=None):
    """
    Parse args from command line

    Returns:
        arguments of the user input
    """

    parser = argparse.ArgumentParser(description='Compal Stress Tool')

    # Custom args
    parser.add_argument('--cleanup', dest='cleanup', default=None, type=str.lower, choices=['yes', 'no'],
                    help='Perform cleanup tasks and close DeviceCompare if it is running,\n'
                        'including removing temporary files, resetting power settings, deleting WLAN profiles, and cleaning Windows events and BIOS logs.\n'
                        'When set to "yes," the --backup_cleanup option is also enabled; when set to "no," the --backup_cleanup option is disabled.\n'
                        'If --backup_cleanup is enabled, the program will clean Windows and BIOS event logs with each power cycle.')
    parser.add_argument('--backup_cleanup', default=None, action='store_true', help='[Internal Use Only] Clean Windows events and BIOS logs (Not for general use).')
    parser.add_argument('--setup', default=None, action='store_true', help='Set up system settings like UAC, memory dump settings, and Windows power plan.')
    parser.add_argument('--auto', default=None, action='store_true', 
                    help='Run DeviceCompare automatically. If DeviceCompare is running, please double click AutoStress.exe to teardown your system first.')
    parser.add_argument('--stop', nargs='+', dest='stop', default=None, type=str,
                    help='If DeviceCompare gets negetive results, the autoscript will be stopped.\n'
                        'Usage: --stop all or --stop "SanDisk" "SoundWire Speakers".\n'
                        'Note: Use with --auto to enable the stop functionality. Without --auto, the stop feature will not be active.')
    parser.add_argument('--standby', nargs=2, dest='standby', default=None, type=int, metavar=('iterations', 'duration'),
                    help='Enter standby mode multiple times, each time staying in standby for a specified duration.\n'
                        'Usage: --standby 3 60 (up to 2 iterations).\n'
                        'This means standby for 3 times, each time for 60 seconds before waking up the system.')
    parser.add_argument('--hibernate', nargs=2, dest='hibernate', default=None, type=int, metavar=('iterations', 'duration'),
                    help='Enter hibernation mode multiple times, each time staying in hibernation for a specified duration.\n'
                        'Usage: --hibernate 3 60 (up to 2 iterations).\n'
                        'This means hibernate for 3 times, each time for 60 seconds before waking up the system.')
    parser.add_argument('--wb', dest='wb', default=None, type=int, metavar=('iterations'),
                    help='Perform warm boot multiple times, each time restarting the system after a specified duration.\n'
                        'Usage: --wb 3 (up to 1 iterations).\n'
                        'This means warm boot for 3 times.')
    parser.add_argument('--cb', nargs=2, dest='cb', default=None, type=int, metavar=('iterations', 'duration'),
                    help='Perform cold boot multiple times, each time powering down the system for a specified duration before waking it up.\n'
                        'Usage: --cb 3 60 (up to 2 iterations).\n'
                        'This means cold boot for 3 times, each time powering down for 60 seconds before waking up the system.')
    parser.add_argument('--greset', dest='greset', default=None, type=int, metavar=('iterations'),
                    help='Perform global reset multiple times, each time restarting the system after a specified duration.\n'
                        'Usage: --greset 3 (up to 1 iterations).\n'
                        'This means global reset for 3 times.')
    parser.add_argument('--delay', dest='delay', default=None, type=int, metavar=('duration'),
                    help='Set the delay time (in seconds) before each power cycle.\n'
                        'Usage: --delay 60 (up to 1 iterations).')
    if cmd_line:
        args = parser.parse_args(cmd_line)
    else:
        args = parser.parse_args()

    return args

def get_process_id_by_name(name):
    """
    Get process id of application by name

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
        runtime.error_msgbox(f'get_process_id_by_name: {err}')
        return 1, None

    return 0, pid

def parse_argument(args):
    """
    Parses command-line arguments related to system backup.

    Args:
        args: Command-line arguments.

    Returns:
        list[int]: A list containing standby, hibernate, warmboot, coldboot, and global reset.
    """

    standby_num = args.standby[0] if args.standby is not None else 0
    hibernate_num = args.hibernate[0] if args.hibernate is not None else 0
    wb_num = args.wb if args.wb is not None else 0
    cb_num = args.cb[0] if args.cb is not None else 0
    greset_num = args.greset if args.greset is not None else 0
    backup_num = [standby_num, hibernate_num, wb_num, cb_num, greset_num]

    return backup_num

def set_current_test_mode(args, count, backup_num):
    """
    Write the current arguments into a JSON file.

    Args:
        args (Namespace): Namespace containing parsed command-line arguments.
        count (int): Stress cycle count.
        backup_number (list): List containing standby, hibernate, write-back, clean backup, and global reset numbers.

    Returns:
        int: Return code (0 if successful, 1 if errors occurred).
    """

    runtime.debug_msg(f'argparse: {args}, argparse type: {type(args)} in set_current_test_mode()')
    test_args = []

    if args.cleanup is not None:
        test_args.append(f'--cleanup')
        curr_dict['cleanup_value'] = args.cleanup.lower()

    if args.backup_cleanup is not None:
        test_args.append(f'--backup_cleanup')

    if args.setup is not None:
        test_args.append(f'--setup')

    if args.auto is not None:
        test_args.append(f'--auto')

    if args.stop is not None:
        test_args.append(f'--stop')
        curr_dict['stop_device'] = args.stop

    if args.standby is not None:
        test_args.append(f'--standby')
        curr_dict['standby_num'] = backup_num[0]
        curr_dict['standby_time'] = args.standby[1]

    if args.hibernate is not None:
        test_args.append(f'--hibernate')
        curr_dict['hibernate_num'] = backup_num[1]
        curr_dict['hibernate_time'] = args.hibernate[1]

    if args.wb is not None:
        test_args.append(f'--wb')
        curr_dict['wb_num'] = backup_num[2]

    if args.cb is not None:
        test_args.append(f'--cb')
        curr_dict['cb_num'] = backup_num[3]
        curr_dict['cb_time'] = args.cb[1]

    if args.greset is not None:
        test_args.append(f'--greset')
        curr_dict['greset_num'] = backup_num[4]

    if args.delay is not None:
        test_args.append(f'--delay')
        curr_dict['delay_time'] = args.delay

    curr_dict['stress_cycle'] = count
    curr_dict['curr_test_args'] = test_args

    runtime.debug_msg(f'The dict of stress_cycle = {count}')
    runtime.debug_msg(f'The dict of curr_test_args = {test_args}')

    if dash.write_json_file(current_state_path, curr_dict):
        runtime.error_msgbox(f'Can not write the current args into {current_state_path}')
        return 1

    return 0

def cleanup():
    """
    Remove log files, kill running DeviceCompare APP, clean up Windows and BIOS event logs

    Returns:
        (bool): Return code (0 if successful, 1 if errors occurred).
    """

    # kill the running DeviceCompare.exe
    try:
        rc, pid_devicecompare = get_process_id_by_name("DeviceCompare.exe")

        if rc == 0 and pid_devicecompare is not None:
            app = Application(backend="uia").connect(title_re="Device Compare")
            app.kill()
            time.sleep(1)  # Wait for app.kill() to be done
            runtime.info_msg(f'Closing DeviceCompare is done')

    except Exception as err:
        runtime.error_msgbox(f'Can not close DeviceCompare! Error: {err}')
        return 1

    # clean up temp files in the device compare folder
    try:
        if os.path.exists(device_list_path):
            file_list = os.listdir(device_list_path)
            for f in file_list:
                runtime.info_msg(f'remove the old file of {f}')
                os.remove(os.path.join(device_list_path, f))

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {device_list_path}! Error: {err}')
        return 1

    # clean up temp files in the device compare folder
    try:
        if os.path.exists(device_compare_log_path):
            file_list = os.listdir(device_compare_log_path)
            for f in file_list:
                runtime.info_msg(f'remove the old file of {f}')
                os.remove(os.path.join(device_compare_log_path, f))

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {device_compare_log_path}! Error: {err}')
        return 1

    # clean up temp files in the debuglog folder
    try:
        if os.path.exists("C:\Compal\DeviceCompare\debuglog"):
            file_list = os.listdir("C:\Compal\DeviceCompare\debuglog")
            for f in file_list:
                runtime.info_msg(f'Remove the old file of {f}')
                os.remove(os.path.join("C:\Compal\DeviceCompare\debuglog", f))

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up the log files in C:\Compal\DeviceCompare\debuglog! Error: {err}')
        return 1

    # clean up config files in the device compare folder
    try:
        if os.path.exists(device_compare_folder_path):
            file_list = os.listdir(device_compare_folder_path)
            for f in file_list:
                if ".txt" in f:
                    runtime.info_msg(f'Remove the old file of {f}')
                    os.remove(os.path.join(device_compare_folder_path, f))

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {device_compare_folder_path}! Error: {err}')
        return 1

    # clean up temp files in the Temp folder
    try:
        if os.path.exists(Temp_path):
            file_list = os.listdir(Temp_path)
            for f in file_list:
                if ".log" in f:
                    runtime.info_msg(f'Remove the old file of {f}')
                    os.remove(os.path.join(Temp_path, f)) 

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {Temp_path}! Error: {err}')
        return 1

    # clean up config files in the pwrtest folder
    try:
        if os.path.exists(pwrtest_folder_path):
            file_list = os.listdir(pwrtest_folder_path)
            for f in file_list:
                # do not need to remove EXE file
                if ".exe" in f:      
                    pass
                else:
                    runtime.info_msg(f'Remove the old file of {f}')
                    os.remove(os.path.join(pwrtest_folder_path, f)) 

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {pwrtest_folder_path}! Error: {err}')
        return 1

    # remove the old batch files
    try:
        if os.path.exists(batch_file_path):
            runtime.info_msg(f'Remove the old batch file of {batch_file_path}')
            os.remove(batch_file_path)

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {startup_path}! Error: {err}')
        return 1

    # remove the old json files
    try:
        if os.path.exists(current_state_path):
            runtime.info_msg(f'Remove the olde json file of {current_state_path}')
            os.remove(current_state_path)

    except Exception as err:
        runtime.error_msgbox(f'Can not clean up files in {test_path}! Error: {err}')
        return 1

    # delete WLAN profiles from interface Wi-Fi
    rc, std_out, std_err = dash.runcmd('netsh wlan delete profile name=*')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not delete WLAN profiles from interface Wi-Fi! Warning: {std_err}')
    else:
        runtime.info_msg(f'{std_out}')

    # reset and restore power plan to default settings
    rc, _, std_err = dash.runcmd('powercfg restoredefaultschemes')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not reset power plans! Warning: {std_err}')
    else:
        runtime.info_msg(f'Restore default settings for the power plans was successful!')

    # clean up Windows Event, like Application, System, Setup and Security
    rc, _, std_err = dash.runcmd('wevtutil cl Application')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of Application! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of Application was successful!')

    rc, _, std_err = dash.runcmd('wevtutil cl System')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of System! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of System was successful!')

    rc, _, std_err = dash.runcmd('wevtutil cl Setup')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of Setup! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of Setup was successful!')

    rc, _, std_err = dash.runcmd('wevtutil cl Security')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of Security! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of Security was successful!')

    # set the platcfg cmd for cleaning BIOS log
    cmd = f'"{platcfg2w_exe_path}" -set BiosLogClear=Clear'

    rc, _, std_err = dash.runcmd(cmd)
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up BIOS logs with the cmd of {cmd}! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning BIOS logs was successful!')

    # set the platcfg cmd for cleaning thermal log
    cmd = f'"{platcfg2w_exe_path}" -set ThermalLogClear=Clear'

    rc, _, std_err = dash.runcmd(cmd)
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up thermal logs with the cmd of {cmd}! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning thermal logs was successful!')

    # set the platcfg cmd for cleaning power log
    cmd = f'"{platcfg2w_exe_path}" -set PowerLogClear=Clear'

    rc, _, std_err = dash.runcmd(cmd)
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up power logs with the cmd of {cmd}! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning power logs was successful!')

    return 0

def backup_cleanup():
    """
    Cleans Windows and BIOS event logs.

    Returns:
        (bool): no need return 
    """

    # clean up Windows Event, like Application, System, Setup and Security
    rc, _, std_err = dash.runcmd('wevtutil cl Application')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of Application! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of Application was successful!')

    rc, _, std_err = dash.runcmd('wevtutil cl System')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of System! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of System was successful!')

    rc, _, std_err = dash.runcmd('wevtutil cl Setup')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of Setup! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of Setup was successful!')

    rc, _, std_err = dash.runcmd('wevtutil cl Security')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up the Windows Event of Security! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning the Windows Event of Security was successful!')

    # set the platcfg cmd for cleaning BIOS log
    cmd = f'"{platcfg2w_exe_path}" -set BiosLogClear=Clear'

    rc, _, std_err = dash.runcmd(cmd)
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up BIOS logs with the cmd of {cmd}! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning BIOS logs was successful!')

    # set the platcfg cmd for cleaning thermal log
    cmd = f'"{platcfg2w_exe_path}" -set ThermalLogClear=Clear'

    rc, _, std_err = dash.runcmd(cmd)
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up thermal logs with the cmd of {cmd}! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning thermal logs was successful!')

    # set the platcfg cmd for cleaning power log
    cmd = f'"{platcfg2w_exe_path}" -set PowerLogClear=Clear'

    rc, _, std_err = dash.runcmd(cmd)
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not clean up power logs with the cmd of {cmd}! Warning: {std_err}')
    else:
        runtime.info_msg(f'Cleaning power logs was successful!')

    return 0

def setup(curr_dict):
    """
    Initializes system settings.

    Args:
        curr_dict (dict): Current test settings.

    Returns:
        (bool): Return code (0 if successful, 1 if errors occurred).
    """

    rc, _, std_err = dash.runcmd('powercfg -change -standby-timeout-dc 0')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not set the standby timeout to 0 in DC mode! Error: {std_err}')
    else:
        runtime.info_msg(f'Setting the standby timeout to 0 in DC mode was successful!')

    rc, _, std_err = dash.runcmd('powercfg -change -standby-timeout-ac 0')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not set the standby timeout to 0 in AC mode! Error: {std_err}')
    else:
        runtime.info_msg(f'Setting the standby timeout to 0 in AC mode was successful!')

    rc, _, std_err = dash.runcmd('powercfg -change -monitor-timeout-dc 0')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not set the monitor timeout to 0 in DC mode! Error: {std_err}')
    else:
        runtime.info_msg(f'Setting the monitor timeout to 0 in DC mode was successful!')

    rc, _, std_err = dash.runcmd('powercfg -change -monitor-timeout-ac 0')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not set monitor timeout to 0 in AC mode! Error: {std_err}')
    else:
        runtime.info_msg(f'Setting the monitor timeout to 0 in AC mode was successful!')

    # config memory dump settings in Startup and Recovery 
    rc, _, std_err = dash.runcmd('wmic recoveros set AutoReboot = False')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not set Automatically Restart to be False! Error: {std_err}')
    else:
        runtime.info_msg(f'Setting Automatically Restart to be False was successful!')

    rc, _, std_err = dash.runcmd('wmic recoveros set DebugInfoType = 1')
    if rc == 1 and std_err is not None:
        runtime.warning_msg(f'Can not set the memory dump to be complete! Error: {std_err}')
    else:
        runtime.info_msg(f'Setting the memory dump to be complete was successful!')

    rc, uac_flag = check_uac_flag()
    if rc:
        runtime.error_msgbox(f'Can not retrieve the UAC flag while the program is running with check_uac_flag()')
        return 1

    if uac_flag:
        # define a string variable 
        backup_cmd = ''

        rc, _, std_err= dash.runcmd('reg.exe ADD HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System /v EnableLUA /t REG_DWORD /d 0 /f')
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'UAC can not be disabled! Error: {std_err}')
            return 1

        for curr_args in curr_dict['curr_test_args']:
            if str(curr_args) == '--cleanup':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['cleanup_value']) + ' '
            if str(curr_args) == '--backup_cleanup':
                backup_cmd = backup_cmd + str(curr_args) + ' '
            elif str(curr_args) == '--auto':
                backup_cmd = backup_cmd + str(curr_args) + ' '
            elif str(curr_args) == '--stop':
                # make curr_dict['stop_device'] to be a string and save the data in stop_device
                stop_device = " ".join(f'\"{item}\"' for item in curr_dict['stop_device'])

                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(stop_device) + ' '
            elif str(curr_args) == '--standby':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['standby_num']) + ' ' + str(curr_dict['standby_time']) + ' '
            elif str(curr_args) == '--hibernate':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['hibernate_num']) + ' ' + str(curr_dict['hibernate_time']) + ' '
            elif str(curr_args) == '--wb':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['wb_num']) + ' '
            elif str(curr_args) == '--cb':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['cb_num']) + ' ' + str(curr_dict['cb_time']) + ' '
            elif str(curr_args) == '--greset':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['greset_num']) + ' '
            elif str(curr_args) == '--delay':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['delay_time']) + ' '
            elif str(curr_args) == '--setup':
                backup_cmd = backup_cmd + str(curr_args) + ' '
            else:
                pass

        backup_cmd = f'{os.path.basename(sys.argv[0])} ' + f'{backup_cmd[:-1]}'  # need to remove a redundant blank key

        runtime.info_msg(f'The backup cmd is {backup_cmd}')
        rc = create_batch_file(backup_cmd)
        if rc:
            runtime.error_msgbox(f'Can not create a batch file with create_batch_file()')
            return 1

        print('Restart your system for reseting UAC settings...')
        cmd = "shutdown -r -t 0 -f"

        time.sleep(1)
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'Can not shutdown the system with the cmd of {cmd}')
            return 1
    else:
        runtime.info_msg(f'UAC is {uac_flag}. We do not need to be disabled again')

    return 0

def do_standby(args):
    """
    Places the system in standby mode and performs the specified number of cycles.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Return code (0 if successful, 1 if errors occurred).
    """

    if args.standby[0] > 0 and args.standby[1] > 0:
        for index in range(0, args.standby[0]):
            if power_check_prompt():
                runtime.error_msgbox(f'Error getting system power status in standby mode')
                return 1

            # If the user inputs '--stop', there wouldn't be a delay time set
            if args.stop is None or index == 0:
                for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
                    print(f'Wait {i}s to do standby...', end='\r')
                    time.sleep(1)

            # reflash dict data from current_state.json
            curr_dict = dash.read_json_file(current_state_path)
            if curr_dict == 1 or curr_dict is None:
                raise Exception(f'The current dict is empty! Failed in accessing {current_state_path}')

            # Determine whether to perform backup based on the user's input value
            if '--cleanup' in curr_dict['curr_test_args'] and curr_dict['cleanup_value'] == 'yes':
                backup_cleanup()
            else:
                runtime.info_msg(f'Do not need to clean up Event Logs')

            print(f'Start running a standby...')

            cmd = f'"{pwrtest_path}" /cs /s:standby /c:1 /d:90 /p:{args.standby[1]}'
            runtime.info_msg(f'Place your system in standby mode with the cmd of {cmd}')

            time.sleep(1)
            rc, _, std_err = dash.runcmd(cmd)
            if rc == 1 and std_err is not None:
                runtime.error_msgbox(f'Can not place your system in standby mode with the cmd of {cmd}! Error: {std_err}')
                return 1

            pwrtestlog = dash.read_txt_file(pwrtestlog_path)
            if pwrtestlog is not None and pwrtestlog != 1:
                runtime.info_msg(f'{pwrtestlog}')
            else:
                runtime.error_msgbox(f'Can not access {pwrtestlog_path}')
                return 1

            count = curr_dict['stress_cycle'] + 1

            if set_current_test_mode(args, count, parse_argument(args)):
                runtime.error_msgbox(f'Return error! Failed in set_current_test_mode()')
                return 1

            if args.stop is not None and args.stop:
                # set the delay time for waitting DeviceCompare is ready
                for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
                    print(f'Wait {i}s to make DeviceCompare ready...', end='\r')
                    time.sleep(1)

                rc, stop_flag = failstop(curr_dict['stop_device'], count)
                if rc:
                    runtime.error_msgbox(f'Test Failed in failstop()')
                    return 1
                elif stop_flag:
                    runtime.info_msgbox(f'Find out the failed devices and stop running the auto script')
                    return 1
                else:
                    runtime.info_msg(f'All devices are working well')

    return 0

def do_hibernate(args):
    """
    Places the system in hibernate mode and performs the specified number of cycles.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Return code (0 if successful, 1 if errors occurred).
    """

    if args.hibernate[0] > 0 and args.hibernate[1] > 0:
        for index in range(0, args.hibernate[0]):
            if power_check_prompt():
                runtime.error_msgbox(f'Error getting system power status in hibernate mode')
                return 1

            # If the user inputs '--stop', there wouldn't be a delay time set
            if args.stop is None or index == 0:
                for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
                    print(f'Wait {i}s to do hibernate...', end='\r')
                    time.sleep(1)

            # reflash dict data from current_state.json
            curr_dict = dash.read_json_file(current_state_path)
            if curr_dict == 1 or curr_dict is None:
                raise Exception(f'The current dict is empty! Failed in accessing {current_state_path}')

            # Determine whether to perform backup based on the user's input value
            if '--cleanup' in curr_dict['curr_test_args'] and curr_dict['cleanup_value'] == 'yes':
                backup_cleanup()
            else:
                runtime.info_msg(f'Do not need to clean up Event Logs')

            print(f'Start running a hibernate...')

            _, _, is_s4_supported = get_sleep_state()
            if not is_s4_supported:
                _, _, std_err = dash.runcmd('powercfg -H ON')
                _, _, is_s4_supported = get_sleep_state()
                if not is_s4_supported:
                    runtime.info_msg('Sleep State, Hibernate (S4), is not enabled on this platform')
                else:
                    # Place the system into hibernate, wait 60 seconds, then resume. Repeat three times
                    cmd = f'"{pwrtest_path}" /sleep /s:4 /c:1 /d:90 /p:{args.hibernate[1]}'

                    runtime.info_msg(f'Place system in Hibernate (s:4) mode by command line: {cmd}')

                    time.sleep(1)
                    rc, _, std_err = dash.runcmd(cmd)
                    if rc == 1 and std_err is not None:
                        runtime.error_msgbox(f'Can not place your system in hibernate mode with the cmd of {cmd}! Error: {std_err}')
                        return 1
            else:
                runtime.info_msg('Sleep state S4 (Hibernate) is available in this system')
                # Place the system into Hibernate, wait 60 seconds, then resume. Repeat three times
                cmd = f'"{pwrtest_path}" /sleep /s:4 /c:1 /d:90 /p:{args.hibernate[1]}'

                runtime.info_msg(f'Place system in Hibernate (s:4) mode by command line: {cmd}')

                time.sleep(1)
                rc, _, std_err = dash.runcmd(cmd)
                if rc == 1 and std_err is not None:
                    runtime.error_msgbox(f'Can not place your system in hibernate mode with the cmd of {cmd}! Error: {std_err}')
                    return 1

            pwrtestlog = dash.read_txt_file(pwrtestlog_path)
            if pwrtestlog is not None and pwrtestlog != 1:
                runtime.info_msg(f'{pwrtestlog}')
            else:
                runtime.error_msgbox(f'Can not access {pwrtestlog_path}')
                return 1

            count = curr_dict['stress_cycle'] + 1

            if set_current_test_mode(args, count, parse_argument(args)):
                runtime.error_msgbox(f'Return error! failed in set_current_test_mode()')
                return 1

            if args.stop is not None and args.stop:
                # set the delay time for waitting DeviceCompare is ready
                for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
                    print(f'Wait {i}s to make DeviceCompare ready...', end='\r')
                    time.sleep(1)

                rc, stop_flag = failstop(curr_dict['stop_device'], count)
                if rc:
                    runtime.error_msgbox(f'Test Failed in failstop()')
                    return 1
                elif stop_flag:
                    runtime.info_msgbox(f'Find out the failed devices and stop running the auto script')
                    return 1
                else:
                    runtime.info_msg(f'All devices are working well')

    return 0

def do_warm_boot(args):
    """
    Place system in warm boot mode

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        (bool): tuple(int[0, 1])
    """

    if args.wb is not None and args.wb > 0:
        print(f'Start running a warm boot...')
        cmd = "shutdown -r -t 0 -f"

        time.sleep(1)
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'Can not place your system in warm boot mode with the cmd of {cmd}! Error: {std_err}')
            return 1

    return 0

def do_cold_boot(args):
    """
    Place system in cold boot mode

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        (bool): tuple(int[0, 1])
    """

    if args.cb is not None and (args.cb[0] > 0 and args.cb[1] >= 60):
        # Update wake up timer
        cmd = f'"{platcfgw_exe_path}" -w Auto_On:Daily'

        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'The wake up timer Failed in cmd of {cmd}! Error: {std_err}')
            return 1
        # Command wakeup after shutdown according to specified number of minutes
        sleep_time_minutes = round(args.cb[1] / 60)  # Minute

        # Set system time to avoid issues with seconds rollover
        if dash.set_system_time():
            runtime.error_msgbox(f'Error setting system time')

        cmd = f'"{platcfgw_exe_path}" -w Auto_On_Time:{(datetime.datetime.now() + datetime.timedelta(minutes=+sleep_time_minutes)).strftime("%H:%M")}'
        runtime.info_msg(f'Set Auto On Time with the cmd of {cmd}')

        # Run CMD wakeup
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'The wake up timer Failed in cmd of {cmd}! Error: {std_err}')
            return 1
        # CMD Shutdown
        print(f'Start running a cold boot...')
        cmd = "shutdown -s -t 0 -f"

        time.sleep(1)
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'Can not place your system in cold boot mode with the cmd of {cmd}! Error: {std_err}')
            return 1

    elif args.cb is not None and (args.cb[0] > 0 and args.cb[1] < 60):
        runtime.error_msgbox(f'For --cb, sleep time shound be more than 60s')
        return 1

    return 0

def do_global_reset(args):
    """
    Place system in global reset mode

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        (bool): tuple(int[0, 1])
    """

    if args.greset is not None and args.greset > 0:
        print(f'Start running a global reset...')
        cmd = f'"{fpt_exe_path}" -greset'

        time.sleep(1)
        rc, _, std_err = dash.runcmd(cmd)
        if rc == 1 and std_err is not None:
            runtime.error_msgbox(f'Can not place your system in global reset mode with the cmd of {cmd}! Error: {std_err}')
            return 1

    return 0

def power_check_prompt():
    """
    Checks the system power status.

    Returns:
        (bool): Return code (0 if successful, 1 if errors occurred).
    """

    rc, ACLineStatus = dash.check_power()
    if rc:
        runtime.error_msgbox(f'Error getting system power status')
        return 1
    elif ACLineStatus:
        pass
    else:
        runtime.warning_msg(f'Your system is DC only! Please check whether you need to insert AC or not')
        return 0

    return 0

def test_teardown():
    """
    Performs the necessary steps to reset the system state after the test.

    Returns:
        (bool): Return code (0 if successful, 1 if errors occurred).
    """

    print(f'Start to teardown AutoStress.exe...')

    # remove old batch files
    try:
        if os.path.exists(batch_file_path):
            runtime.info_msg(f'remove the old batch file of {batch_file_path}')
            os.remove(batch_file_path)

    except Exception as err:
        runtime.error_msgbox(f'Can not clean files in {startup_path}! Error: {err}')
        return 1

    try:
        rc, pid_devicecompare = get_process_id_by_name("DeviceCompare.exe")

        if rc == 0 and pid_devicecompare is not None:
            app = Application(backend="uia").connect(title_re="Device Compare")
            main_window = app.window(title_re="Device Compare")
            # wait to be ready
            main_window.wait('visible', timeout=30)
            # initialize x, y coordinate
            pyautogui.moveTo(0, 0, duration=0.25)
            time.sleep(1)
            # stop
            main_window.child_window(title="Stop", auto_id="b_start", control_type="Button").click()
            runtime.info_msg(f'Closing DeviceCompare is done')
        else:
            runtime.info_msg(f'DeviceCompare is not working! Do not need to stop it')

    except Exception as err:
        runtime.error_msgbox(f'Can not stop DeviceCompare! Error: {err}')
        return 1

    print(f'Teardown is done, press any key to exit the program')
    os.system("pause")

    return 0

def run_device_compare():
    """
    Automatically run DeveiveCompare.exe

    Returns:
        (bool): tuple(int[0, 1])
    """

    print(f'Start running DeviceCompare..., please do not operate your system!')

    try:
        # Run DeviceCompare app
        app = Application(backend="uia").start(device_compare_path)
        main_window = app.window(title_re="Device Compare")
        # wait to be ready
        main_window.wait('visible', timeout=30)
        # dump UI handles of DeviceCompare.
        #main_window.print_control_identifiers(filename=device_compare_ui_handle_path)
        # initialize x, y coordinate
        pyautogui.moveTo(0, 0, duration=0.25)
        # delay 1s every action
        time.sleep(1)
        # reset
        main_window.child_window(title="Reset", auto_id="b_reset", control_type="Button").click()
        time.sleep(1)
        # sync
        main_window.child_window(title="Sync", auto_id="b_sync", control_type="Button").click()
        time.sleep(1)
        # start
        main_window.child_window(title="Start", auto_id="b_start", control_type="Button").click()

    except Exception as err:
        runtime.error_msgbox(f'Can not run DeviceCompare! Please check it whether is ready for use. Error: {err}')
        return 1

    print(f'Running DeviceCompare is done')

    return 0 

def test_main(args):
    """
    This function contains the main logic for executing the test.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
    
    Returns:
        bool: True if the test passes, False otherwise.
    """

    runtime.debug_msg(f'argparse: {args}, argparse type: {type(args)} in test_main()')

    if power_check_prompt():
        runtime.error_msgbox(f'Error getting system power status in test_main()')
        return 1

    # reflash dict data from current_state.json
    curr_dict = dash.read_json_file(current_state_path)
    if curr_dict == 1 or curr_dict is None:
        raise Exception(f'The current dict is empty! Failed in accessing {current_state_path}')

    # get stress cycles
    count = curr_dict['stress_cycle']

    # set a delay time to wait for DeviceCompare to be ready
    if args.wb is not None and args.wb > 0:
        for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
            print(f'Wait {i}s to do a warm boot...', end='\r')
            time.sleep(1)
    elif args.cb is not None and args.cb[0] > 0:
        for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
            print(f'Wait {i}s to do a cold boot...', end='\r')
            time.sleep(1)
    elif args.greset is not None and args.greset > 0:
        for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
            print(f'Wait {i}s to do a global reset...', end='\r')
            time.sleep(1)
    elif args.standby is not None or args.hibernate is not None:
        pass  # bypass the delay time when the last cycle is in standby or hibernate mode
    else:
        for i in range(args.delay if args.delay is not None else delay_time, 0, -1):
            print(f'Wait {i}s to make DeviceCompare ready...', end='\r')
            time.sleep(1)

    if args.stop is not None and args.stop:
        runtime.debug_msg(f'The current dict of stop_device: {curr_dict["stop_device"]}')
        rc, stop_flag = failstop(curr_dict['stop_device'], count)
        if rc:
            runtime.error_msgbox(f'The test Failed in failstop()')
            return 1
        elif stop_flag:
            runtime.info_msgbox(f'Find out the failed devices and stop running the auto script')
            return 1
        else:
            runtime.info_msg(f'All devices are working well')

    backup_cmd = ''

    if args.wb is not None and args.wb > 0:
        runtime.debug_msg(f'The current dict of wb_num: {curr_dict["wb_num"]}')
        backup_num = [0, 0, curr_dict['wb_num'] - 1, args.cb[0], args.greset]  # reflash curr_dict['wb_num']

        for curr_args in curr_dict['curr_test_args']:
            if str(curr_args) == '--cleanup' and str(curr_dict['cleanup_value']) == 'yes':
                backup_cmd = backup_cmd + '--backup_cleanup' + ' '
            if str(curr_args) == '--backup_cleanup':
                backup_cmd = backup_cmd + str(curr_args) + ' '
            elif str(curr_args) == '--stop':
                # make curr_dict['stop_device'] to be a string and save the data in stop_device
                stop_device = " ".join(f'\"{item}\"' for item in curr_dict['stop_device'])

                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(stop_device) + ' '
            elif str(curr_args) == '--wb' and backup_num[2] > 0:
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(backup_num[2]) + ' '
            elif str(curr_args) == '--cb':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['cb_num']) + ' ' + str(curr_dict['cb_time']) + ' '
            elif str(curr_args) == '--greset':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['greset_num']) + ' '
            elif str(curr_args) == '--delay':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['delay_time']) + ' '
            else:
                pass

        backup_cmd = f'{os.path.basename(sys.argv[0])} ' + f'{backup_cmd[:-1]}'  # need to remove a redundant blank key

        if create_batch_file(backup_cmd):
            runtime.error_msgbox(f'Return error! Failed in create_batch_file() with the cmd of {backup_cmd}')
            return 1

    elif args.cb is not None and args.cb[0] > 0:
        runtime.debug_msg(f'The current dict of cb_num: {curr_dict["cb_num"]}')
        backup_num = [0, 0, 0, curr_dict['cb_num'] - 1, args.greset]  # reflash curr_dict['cb_num']

        for curr_args in curr_dict['curr_test_args']:
            if str(curr_args) == '--cleanup' and str(curr_dict['cleanup_value']) == 'yes':
                backup_cmd = backup_cmd + '--backup_cleanup' + ' '
            if str(curr_args) == '--backup_cleanup':
                backup_cmd = backup_cmd + str(curr_args) + ' '
            elif str(curr_args) == '--stop':
                # make curr_dict['stop_device'] to be a string and save the data in stop_device
                stop_device = " ".join(f'\"{item}\"' for item in curr_dict['stop_device'])

                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(stop_device) + ' '
            elif str(curr_args) == '--cb' and backup_num[3] > 0:
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(backup_num[3]) + ' ' + str(curr_dict['cb_time']) + ' '
            elif str(curr_args) == '--greset':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['greset_num']) + ' '
            elif str(curr_args) == '--delay':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['delay_time']) + ' '
            else:
                pass

        backup_cmd = f'{os.path.basename(sys.argv[0])} ' + f'{backup_cmd[:-1]}'  # need to remove a redundant blank key

        if create_batch_file(backup_cmd):
            runtime.error_msgbox(f'Return error! Failed in create_batch_file() with the cmd of {backup_cmd}')
            return 1

    elif args.greset is not None and args.greset > 0:
        runtime.debug_msg(f'The current dict of greset_num: {curr_dict["greset_num"]}')
        backup_num = [0, 0, 0, 0, curr_dict['greset_num'] - 1]  # reflash curr_dict['cb_num']

        for curr_args in curr_dict['curr_test_args']:
            if str(curr_args) == '--cleanup' and str(curr_dict['cleanup_value']) == 'yes':
                backup_cmd = backup_cmd + '--backup_cleanup' + ' '
            if str(curr_args) == '--backup_cleanup':
                backup_cmd = backup_cmd + str(curr_args) + ' '
            elif str(curr_args) == '--stop':
                # make curr_dict['stop_device'] to be a string and save the data in stop_device
                stop_device = " ".join(f'\"{item}\"' for item in curr_dict['stop_device'])

                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(stop_device) + ' '
            elif str(curr_args) == '--greset' and backup_num[4] > 0:
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(backup_num[4]) + ' '
            elif str(curr_args) == '--delay':
                backup_cmd = backup_cmd + str(curr_args) + ' ' + str(curr_dict['delay_time']) + ' '
            else:
                pass

        backup_cmd = f'{os.path.basename(sys.argv[0])} ' + f'{backup_cmd[:-1]}'  # need to remove a redundant blank key

        if create_batch_file(backup_cmd):
            runtime.error_msgbox(f'Return error! Failed in create_batch_file() with the cmd of {backup_cmd}')
            return 1
    else:
        backup_num = [0, 0, 0, 0, 0]  # for local variable to use
        if set_current_test_mode(args, count, backup_num):
            runtime.error_msgbox(f'Return error! Failed in set_current_test_mode()')
            return 1
        # handle for finish test
        runtime.info_msg(f'Finished {sys.argv[0]} rc=0')
        return test_teardown()

    # curr_dict['stress_cycle'] + 1 when the power cycle is done
    if set_current_test_mode(args, count + 1, backup_num):
        runtime.error_msgbox(f'Return error! Failed in set_current_test_mode()')
        return 1

    # run backup_cleanup
    if args.backup_cleanup is not None and backup_cleanup():
        runtime.error_msgbox(f'Return error! Failed in backup_cleanup()')
        return 1
    # run warm boot
    if args.wb is not None and do_warm_boot(args):
        runtime.error_msgbox(f'Return error! Failed in do_warm_boot()')
        return 1
    # run cold boot
    if args.cb is not None and do_cold_boot(args):
        runtime.error_msgbox(f'Return error! Failed in do_cold_boot()')
        return 1
    # run global reset
    if args.greset is not None and do_global_reset(args):
        runtime.error_msgbox(f'Return error! Failed in do_global_reset()')
        return 1

    return 0

# Test Entry point
if __name__ == '__main__':
    # Parse arguments, and calls to test_main(), test_teardown() done here.
    # Script should exit back to shell from here using sys.exit(rc)
    try:
        # show the basic information
        print("===========================================================================")
        print(f'Tool version {tool_version}, Python package {python_version}')
        print("This is README.txt, the class material's top-level user guide")
        print("Author: Kanan Fan, https://www.youtube.com/channel/UCoSrY_IQQVpmIRZ9Xf-y93g")
        print("===========================================================================")

        # parse arguments
        args = parse_cmdline()
        
        if args.cleanup is not None and cleanup():
            raise Exception(f'Return error! Failed in running --cleanup')

        # for counting stress cycle
        if os.path.exists(current_state_path):
            curr_dict = dash.read_json_file(current_state_path)
            if curr_dict == 1 or curr_dict is None:
                raise Exception(f'The current dict is empty! Failed in accessing {current_state_path}')

            count = curr_dict['stress_cycle']
        else:
            count = 0

        # back up current agrs, num and time
        if set_current_test_mode(args, count, parse_argument(args)):
            raise Exception(f'Return error! Failed in setting the test arguments')

        curr_dict = dash.read_json_file(current_state_path)
        if curr_dict == 1 or curr_dict is None:
            raise Exception(f'The current dict is empty! Failed in accessing {current_state_path}')

        # set environment
        if args.setup is not None and setup(curr_dict):
            raise Exception(f'The test Failed in running --setup')

        # run DeviceCompare
        if args.auto is not None and run_device_compare():
            raise Exception(f'The test Failed in running --auto')

        # run standby
        if args.standby is not None and do_standby(args):
            raise Exception(f'The test Failed in running --standby')

        # run hibernate
        if args.hibernate is not None and do_hibernate(args):
            raise Exception(f'The test Failed in running --hibernate')

        # Test main
        if test_main(args):
            raise Exception(f'The test Failed in running --wb, --cb and --greset')

    except Exception as err:
        runtime.handle_exception(f'Error: {err}. Please check runtime.log in logs folder for more details')
        runtime.handle_exception(f'Finished {sys.argv[0]} rc=1')
        test_teardown()