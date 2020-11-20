import os

MODPACK_NAME = '.TMP.PYAUTOGUI-TEST-MODPACK-EXPORT.tmp'
ZIP_NAME = MODPACK_NAME+'.zip'
DEFAULT_ZIP_NAME = 'export.zip'

SCRIPTS_FOLDER = 'scripts/pyautogui'
IMAGES_FOLDER=os.path.join(SCRIPTS_FOLDER, 'images')

FORGE_IDENT_REXP=r'Forge Mod Loader has identified \d+? mods to load'
FORGE_LOADED_REXP=r'Forge Mod Loader has successfully loaded \d+? mods'
MINECRAFT_CRASHED_REXP=r'---- Minecraft Crash Report ----'
MINECRAFT_TEXTURE_STITCHER_OUT_OF_VRAM=r'net.minecraft.client.renderer.StitcherException: Unable to fit:'

LOADING_TIME_FILE='.TMP.LOADING_TIME.TXT'

def png_path(fp):
    return os.path.join(IMAGES_FOLDER, fp)


MMC_BINARY_PATHS = [
    '/opt/multimc/run.sh',

    'C:/tools/MultiMC/MultiMC.exe',
    'C:/Program Files (x86)/MultiMC/MultiMC.exe',
    'C:/Program Files/MultiMC/MultiMC.exe',
]
