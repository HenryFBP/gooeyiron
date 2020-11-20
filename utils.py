from typing import Union
from pprint import pprint
import distutils.spawn
import re
from typing import List
try:
    from scripts.pyautogui.config import *
except Exception:
    pass  # lol thanks IDE, you know what local paths are
from config import *
import psutil
import subprocess
import shutil
import os
import time
from pygetwindow import BaseWindow
import pygetwindow as gw
import pyautogui as pag
from psutil import Process
from os import remove
import platform
import timeit


def is_windows():
    return platform.system() == 'Windows'


def is_vm():
    if is_windows():
        wmic_output = subprocess.check_output(
            ['wmic', 'bios', 'get', 'serialnumber'], shell=True)
        wmic_output = wmic_output.decode()
        wmic_output = wmic_output.replace('SerialNumber', '')
        wmic_output = wmic_output.strip()

        return wmic_output == '0'
    else:
        raise Exception(
            "Checking if I'm in a VM is not implemented for Linux.")


def has_gpu():
    # TODO This is flawed. Actually check OpenGL version.
    if is_windows():
        if is_vm():
            return False
        else:  # not a vm but windows
            return True
    else:  # linux, vm? maybe
        return True


def write_time_file(i: float):
    if os.path.exists(LOADING_TIME_FILE):
        os.remove(LOADING_TIME_FILE)
    with open(LOADING_TIME_FILE, 'w') as f:
        f.write(str(i))


def cycle_windows_backwards():
    """Alt shift tab."""
    pag.hotkey("alt", "shift", "tab")


def altf4():
    """Alt-F4."""
    pag.hotkey('alt', 'f4')


def ensure_path_exists(p, err_msg=None) -> Exception:

    msg = "Path {} does not exist! Halting! ".format(p)

    if err_msg:
        msg += err_msg

    if not os.path.exists(p):
        raise Exception(msg)


def is_multimc(p: Process) -> bool:

    name, cmdline = "", ""

    try:
        name = p.name()
        cmdline = p.cmdline()
    except (PermissionError, psutil.AccessDenied, ProcessLookupError, psutil.NoSuchProcess) as e:  # Windows can do this
        if isinstance(e, PermissionError) or isinstance(e, psutil.AccessDenied):
            print("Not allowed to view process {}".format(p.pid))
        if isinstance(e, ProcessLookupError) or isinstance(e, psutil.NoSuchProcess):
            print("Process {} does not exist. Race condition?".format(p.pid))
        pass

    # print(name, cmdline)
    # if 'MultiMC' in name:
    if 'multimc' in name.lower() or 'multimc' in ' '.join(cmdline).lower():
        print(p)
        return True

    return False


def remove_file(fp):
    if os.path.exists(fp):
        os.remove(fp)


def get_multimc_binary_path():
    """Ex. C:/tools/MultiMC/MultiMC.exe"""
    for path in MMC_BINARY_PATHS:
        if os.path.exists(path):
            return path
    return None


def get_multimc_instances_path():
    """Ex. C:/tools/MultiMC/instances/"""
    multimc_instances_folder = os.path.join(
        os.path.dirname(get_multimc_binary_path()), 'instances')

    ensure_path_exists(multimc_instances_folder, "MMC Instances folder")

    return multimc_instances_folder


def get_multimc_instance_path():
    """Ex. C:/tools/MultiMC/instances/.TMP.PYAUTOGUI-TEST-MODPACK-EXPORT.tmp/"""
    p = os.path.join(get_multimc_instances_path(), MODPACK_NAME)

    ensure_path_exists(p)

    return p


def get_multimc_instance_logfile_path():
    """Ex. C:/tools/MultiMC/instances/.TMP.PYAUTOGUI-TEST-MODPACK-EXPORT.tmp/minecraft/logs/latest.log"""
    p = os.path.join(get_multimc_instance_path(), 'minecraft/logs/latest.log')

    ensure_path_exists(p)

    return p


def ensure_packwiz_installed():
    if not distutils.spawn.find_executable("packwiz"):
        raise Exception(
            "`packwiz` not found on PATH. Download from https://github.com/comp500/packwiz")


def ensure_multimc_installed():
    if not get_multimc_binary_path():
        print("Could not find MultiMC binary. Searched these paths:")
        pprint(MMC_BINARY_PATHS)
        raise Exception("Could not find MMC instance.")


def ensure_multimc_closed():
    # multimc must be closed
    multimc_open = False
    for p in psutil.process_iter():
        multimc_open = is_multimc(p)

    if multimc_open:
        raise Exception("MultiMC must be CLOSED for this to work.")


def open_multimc() -> subprocess.Popen:
    path = get_multimc_binary_path()
    print("Exec {} in background".format(path))
    # os.system(path) # NOTE: this blocks.
    return subprocess.Popen([path])


def get_multimc_window_title() -> str:
    windowTitles = gw.getAllTitles()

    for title in windowTitles:
        if 'multimc' in title.lower():
            print(title)
            return title

    pprint(windowTitles)
    raise Exception("Could not find window title containing 'MultiMC'!")


def get_multimc_window() -> BaseWindow:
    w: BaseWindow = gw.getWindowsWithTitle(get_multimc_window_title())[0]
    pprint(w)
    return w

def get_active_window_title()->str:
    return gw.getActiveWindow().title

def generate_modpack_zip():

    print("Generating modpack zip at "+ZIP_NAME)
    if not os.path.exists("./pack.toml"):
        raise Exception(
            "Could not find pack.toml in current working directory '{}'!".format(os.getcwd()))

    remove_file(ZIP_NAME)
    remove_file(DEFAULT_ZIP_NAME)

    # For some odd reason, packwiz refresh fails if this file doesn't exist.
    if not os.path.exists("./index.toml"):
        with open('./index.toml', 'w') as _:
            pass

    print(subprocess.check_output(['packwiz', 'refresh'])) # Make index.toml
    print(subprocess.check_output(['packwiz', 'cf', 'export']))
    print("Done!")

    os.rename(DEFAULT_ZIP_NAME, ZIP_NAME)

    # exit(1)


def line_in_data_matches_rexp(data: List[str], rexps: Union[List[str], str]) -> bool:
    """Does a line in a list of data match one or more regular expressions?"""
    if isinstance(rexps, str):
        rexps = [rexps]

    for line in data:
        for rexp in rexps:
            results = re.findall(rexp, line)

            if len(results) > 0:
                return True

    return False


def get_file_data(path:str)->List[str]:
    with open(path, 'r') as f:
        data = f.readlines()
    
    return data

def dump_list_str_to_stdout(l:List[str],endl=''):
    for line in l:
        print(line,end=endl)

def line_in_file_matches_rexp(path: str, rexps: Union[List[str], str]) -> bool:
    """Does a line in a file match one or more regular expressions?"""

    if isinstance(rexps, str):
        rexps = [rexps]

    with open(path, 'r') as f:
        data = f.readlines()

    return line_in_data_matches_rexp(data, rexps)

def logfile_says_ran_out_of_VRAM_while_stitching(data:List[str]):
    """Does the logfile indicate Minecraft has crashed due to running out of VRAM while stitching textures?"""
    return line_in_data_matches_rexp(data, MINECRAFT_TEXTURE_STITCHER_OUT_OF_VRAM)

def logdata_says_done_loading_mods(data:List[str]):
    """Does the logfile indicate forge is done loading mods?"""

    return line_in_data_matches_rexp(data, FORGE_LOADED_REXP)

def logdata_says_minecraft_crash_report(data:List[str]):
    """Does the logfile indicate Minecraft has crashed?"""
    return line_in_data_matches_rexp(data, MINECRAFT_CRASHED_REXP)
