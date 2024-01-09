import os
import json
import runtime
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

def read_txt_file(src):
    """
    To read a txt file

    Args:
        src(str): file name including path

    Returns:
        (bool, str): return code, the content of a txt file
    """

    if not os.path.exists(src):
        runtime.error_msg(f'Can not find the txt file of {src}')
        return 1

    try:
        # Reads a txt file and creates string data
        with open(src, 'r', encoding='utf-8') as fin:
            data = fin.read()

    except Exception as err:
        runtime.handle_exception(f'Can not read the file of {src}! Error: {err}')
        return 1

    return data

def read_json_file(src):
    """
    To read a json file

    Args:
        src(str): file name including path

    Returns:
        (bool, str): return code, the content of a json file
    """

    if not os.path.exists(src):
        runtime.error_msg(f'Can not find the json file of {src}')
        return 1

    try:
        # Reads a json file and creates dicts
        with open(src, 'r', encoding='utf-8') as fin:
            json_dict = json.load(fin)

    except Exception as err:
        runtime.handle_exception(f'Can not read the file of {src}! Error: {err}')
        return 1

    return json_dict

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