'''
Test the modpack by launching MultiMC, importing and running the pack.

Exits with different error codes depending on what went wrong.
'''
from pprint import pprint
from config import *
from utils import *
import shutil
import os
import time
import pygetwindow as gw
import pyautogui as pag
from enum import Enum
import argparse

print("--- Gooey Iron, the MultiMC Gui packwiz testing tool ---")


# Type of test to run.
class TestType(Enum):
    multimcgui = 'multimcgui'


argp = argparse.ArgumentParser()

argp.add_argument("--packFolder", '-f', required=True, type=str,
                  help="Folder that the `packwiz` pack resides in. Must contain 'pack.toml' file.")

argp.add_argument("--testType", '-t', required=True, type=TestType, choices=list(TestType),
                  help="Type of test to run. Currently only choice is 'multimcgui'.`")

args = argp.parse_args()

PACK_FOLDER = args.packFolder

if __name__ == '__main__':

    if is_vm():
        print("We are running in a VM!")
    else:
        print("We are not running in a VM!")

    if not os.path.exists(get_packDOTtoml_path(PACK_FOLDER)):
        raise Exception(
            "Did not find pack.toml inside of {}!".format(get_packDOTtoml_path(PACK_FOLDER)))

    ensure_packwiz_installed()
    ensure_multimc_installed()

    ensure_multimc_closed()
    zip_path = generate_modpack_zip(PACK_FOLDER)

    mmc_proc = open_multimc()
    print(mmc_proc)
    pprint(mmc_proc)
    time.sleep(10)  # wait for mmc to open

    im2 = pag.screenshot('before_mmc_window.png')
    mmc_window = get_multimc_window()
    # mmc_window.activate() # Also doesn't focus... Crashes.

    # Our focused window is NOT 'MultiMC'...SHIFT-ALT-TAB.
    if 'multimc' not in get_active_window_title().lower():
        print("Not seeing MultiMC. Alt-Shift-Tab in 1 second.")
        time.sleep(1)
        cycle_windows_backwards()

    # Our focused window is STILL NOT 'MultiMC'...Abort.
    if 'multimc' not in get_active_window_title().lower():
        raise Exception("NOT FOCUSED ON MultiMC! Aborting. Currently focused window: {}".format(
            get_active_window_title().lower()))

    pag.press('esc')  # close any initial dialogues

    # This very critical code ensures the kitty is always activated.
    location = pag.locateOnScreen(png_path('kitty-disabled.png'))
    if location:
        print("Enabling kitty.")
        pag.click(location)
    else:
        print("Kitty already enabled.")

    # Delete old instances if they exist.
    multimc_instances_folder = get_multimc_instances_path()

    old_pack_folder = os.path.join(multimc_instances_folder, MODPACK_NAME)
    if os.path.exists(old_pack_folder):
        print("Deleting old pack folder {}.".format(old_pack_folder))
        shutil.rmtree(old_pack_folder)
    else:
        print("No old pack folder detected.")

    location = pag.locateOnScreen(png_path('add-instance.png'))
    if not location:
        raise Exception("Could not add instance!")
    pag.click(location)

    # get to import from zip screen
    pag.press(['tab', 'tab', 'tab', 'down'], interval=0.5)

    pag.press(['tab', 'tab'], interval=0.5)  # to focus text box

    pag.typewrite(os.path.realpath(zip_path))  # enter path to zip

    pag.press('enter')
    time.sleep(20)

    # Window says "Please wait..."
    n = 5
    time.sleep(n)
    print("Waiting for modpack install.")
    while True:
        if 'please wait' in get_active_window_title().lower():
            print("Window is telling me to wait, I think I will...")
        else:
            print("We're done waiting! Modpack installed.")
            break
        time.sleep(n)
    time.sleep(n)

    # launch
    location = pag.locateOnScreen(png_path('launch.png'))
    if not location:
        raise Exception("Could not launch pack!")
    pag.click(location)

    # detect minecraft window name and start counting
    print("Waiting for modpack to load...")
    n = 5
    time.sleep(n)
    while True:

        # cycle backwards through windows as sometimes MultiMC steals focus
        cycle_windows_backwards()

        if 'minecraft' in get_active_window_title().lower():
            print("Minecraft window has been opened!")

            print("Timer started!")
            START_TIME = time.time()

            break
        elif 'console window for' in get_active_window_title().lower():
            print("Console window open! Minecraft must have crashed!")

            logfile_data = get_file_data(get_multimc_instance_logfile_path())
            dump_list_str_to_stdout(logfile_data)

            exit(1)
        else:
            print("Waiting {} seconds for minecraft window...".format(n))
        time.sleep(n)

    # detect mojang logo on loading screen
    print("Waiting for loading screen to show up...")
    n = 5
    time.sleep(n)
    while True:
        if pag.locateOnScreen(png_path('mojang-logo.png')):
            print("Mojang logo visible!")
            break
        else:
            print("Waiting {} seconds for mojang logo...".format(n))
        time.sleep(n)

    if has_gpu():
        # detect java logo in title
        print("Waiting for 'Java' logo in title...")
        n = 5
        time.sleep(n)
        while True:
            if pag.locateOnScreen(png_path('java.png')):
                print("Java logo visible! We're on the main menu!")

                break
            else:
                print("Waiting {} seconds for Java logo...".format(n))
            time.sleep(n)

    def printfn(): print("Waiting for '{}' in\nlog file {}...".format(
        FORGE_LOADED_REXP, get_multimc_instance_logfile_path()))

    printfn()
    n = 10
    time.sleep(n)
    while True:

        logfile_data = get_file_data(get_multimc_instance_logfile_path())

        if logdata_says_done_loading_mods(logfile_data):
            break
        elif logfile_says_ran_out_of_VRAM_while_stitching(logfile_data):

            if is_vm():
                print("I'm a VM, I have like, no VRAM...so...Just going to exit with status 0...Don't mind me... TODO Actually buy a machine for this!")
                # TODO Actually invest in a bare metal machine to test lol.
                exit(0)
            else:
                dump_list_str_to_stdout(logfile_data)
                raise Exception(
                    "Logfile says MC ran out of VRAM while stictching textures.")

        elif logdata_says_minecraft_crash_report(logfile_data):
            dump_list_str_to_stdout(logfile_data)
            raise Exception("Logfile says minecraft crashed!")
        else:
            printfn()
        time.sleep(n)

    print("Logfile says we're done loading mods!")

    END_TIME = time.time()
    print("Timer ended.")

    TIME_TO_LOAD_INTO_MAIN_MENU = (END_TIME - START_TIME)
    print("Pack took {:.2f} sec or {:.2f} min to load.".format(
        TIME_TO_LOAD_INTO_MAIN_MENU, TIME_TO_LOAD_INTO_MAIN_MENU/60))

    write_time_file(END_TIME - START_TIME)

    # unnecessary, MMC process gets killed when this (parent) dies
    # print("killing mmc in 5s...")
    # time.sleep(5)
    # mmc_proc.kill()  # kill MMC after 10s for testing
    # print("killed mmc.")

    print("killing minecraft in 5s...")
    time.sleep(5)
    active_window = gw.getActiveWindow()
    if 'minecraft 1.' in active_window.title.lower():
        print("ALT-F4 on MC Window...")
        altf4()
    else:
        raise Exception(
            "Minecraft 1.* window is not focused! Cannot close it.")
