# * spowatch v1.4
# ! I donot encourage to use this. It is for educational purposes only.
# ! upgrade to Spotify Premium
# * updates
'''
-> 4/20/2021 no need of any watch files.
-> 4/20/2021 watch files when deleted cause an error.
-> 4/20/2021 added comments to the file for good understanding.
-> 4/20/2021 added threshold.
-> 4/20/2021 now skip ad without lossing focus on spotify restart. focus is set back to the app that you were using before
-> [LATEST] 4/21/2021 performance improved when song is paused spowatch will not run ;)
-> [LATEST] 4/21/2021 Spowatch no longer shows song name on console for better performance.
'''

# from concurrent.futures import thread
import threading
from colorama import Fore
from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
import asyncio
import time
import os
import psutil
import win32process
from win32gui import IsWindowVisible, GetWindowText, EnumWindows, GetForegroundWindow, SetForegroundWindow
import getpass
from pynput.keyboard import Key, Listener

# & change threshold according to your system speed.
# & threshold denotes how fast the spowatch restarts and play after an Advertisement.
THRESHOLD = 2

# & XD if you make your own changes then change version lol
VERSION = 1.4

# no.of ads skiped makes sense uh.
skiped_ads = 0
# this stores spotify threads pid's
spotify_pids = []
# this gets the current user which helps to start Spotify according to the username
user = getpass.getuser()
# this stores the current working window's  handle.
focused_window = 0
# this to used so that when the song stops playing spowatch stops watching.
paused = False
# this ends the spowatch thats it.
end_watch = False
# this is used by the timer when timer go off then timeup is set to True.
timeup = False

# * Spotify can be a windows app downloaded from [Microsoft Store]. or direct .exe download
# * from Spotify website. which have different install locations.

reg_spotify_path = "C:/Users/"+user+"/AppData/Roaming/Spotify/Spotify.exe"
winapp_spotify_path = "C:/Users/"+user + \
    "/AppData/Local/Microsoft/WindowsApps/SpotifyAB.SpotifyMusic_zpdnekdrzrea0/Spotify.exe"

# * correct install location of Spotify, will be updated on runtime.
spotify_install_path = ""


# * This gets the media that is playing in this case we are interseted in Spotify
# * so we set the target to Spotify


async def get_media_info():
    found = True
    while found:
        try:
            sessions = await MediaManager.request_async()
            TARGET_ID = "Spotify.exe"
            current_session = sessions.get_current_session()
            if current_session:
                if current_session.source_app_user_model_id == TARGET_ID:
                    info = await current_session.try_get_media_properties_async()

                    info_dict = {song_attr: info.__getattribute__(
                        song_attr) for song_attr in dir(info) if song_attr[0] != '_'}

                    info_dict['genres'] = list(info_dict['genres'])

                    found = False
                    return info_dict

#! some computers might be slow to open Spotify so the get_media_info will not
#! find Spotify and throws an exception.
        except Exception:
            print("make sure Spotify is open")
            found = True

# * This pauses the song [not required/not used]


# async def pause():
#     sessions = await MediaManager.request_async()
#     current_session = sessions.get_current_session()
#     await current_session.try_pause_async()

# * This plays the song used at the app start.


async def play():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    await current_session.try_play_async()

# * This plays the song next song. when the Spotify restarts it points the last
# * played track.


async def next():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    await current_session.try_skip_next_async()

# * gets the spotify pids and stores it in spotify_pids variable.


def get_spotify_pid():
    global spotify_pids
    process_name = "Spotify"
    pid = []
    for proc in psutil.process_iter():
        if process_name in proc.name():
            pid.append(proc.pid)
    spotify_pids = pid

# * These listen to the song pause.


def paused_listener():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


def on_press(key):
    global spotify_pids
    global paused
    if key == Key.space:
        focused_window = GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(focused_window)
        if pid in spotify_pids:
            paused = not paused


def on_release(_):
    global end_watch
    if end_watch:
        return False


# * starts Spotify with init variable which is True if Spotify is started for the first time.
# * else it is set to False.


def start_spotify(init, path):
    global spotify_pids
    os.startfile(path)
    if not init:
        global timeup
        import threading
        # change focus tries to keep the current working window to view. without changing to Spotify on restart.
        # and stop when the timer rings.
        h = threading.Thread(target=change_focus)
        h.start()
        import concurrent.futures
        # starts a timer of 2 seconds.
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(timer)
            timeup = future.result()
    time.sleep(THRESHOLD)
    get_spotify_pid()
    try:
        if init:
            asyncio.run(play())
        else:
            asyncio.run(next())
    except AttributeError:
        pass
    timeup = False

# * This is the timer bruh


def timer():
    for _ in range(1, 3):
        time.sleep(1)
    return True

# * This part of code tries to change focus until timer hits.


def change_focus():
    global timeup
    focused_window = GetForegroundWindow()
    print("[info]: switching focus to -> "+GetWindowText(focused_window))
    while not timeup:
        try:
            SetForegroundWindow(focused_window)
        except:
            pass


# * This checks if Spotify is running or not which


def spotify_running():
    process_name = "Spotify"
    pid = []
    for proc in psutil.process_iter():
        if process_name in proc.name():
            pid.append(proc.pid)
    if pid == []:
        return False
    else:
        return True

# * This kills the Spotify thread.


def kill_spotify():
    print("[info]: terminating Spotify...")
    process_name = "Spotify"
    for proc in psutil.process_iter():
        if process_name in proc.name():
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass


def winEnumHandler(hwnd, _):
    global focused_window
    global skiped_ads
    global spotify_install_path
    global paused
    global spotify_pids
    if IsWindowVisible(hwnd):
        wintext = GetWindowText(hwnd)
        if wintext != None and wintext != "" and wintext != " ":
            if wintext == "Spotify Free" or wintext == "Advertisement":
                current_media_info = asyncio.run(get_media_info())
                if current_media_info["title"] == "Advertisement":
                    print(Fore.RED + "[info]: Ad dectected")
                    print(Fore.RESET, end="")
                    skiped_ads = skiped_ads + 1
                    kill_spotify()
                    print("[info]: starting Spotify")
                    start_spotify(False, spotify_install_path)

# * Some fancy stuff


def details():
    print(Fore.GREEN + '\nspowatch v' + str(VERSION) +
          '\nLicense & Copyright © vanhsirki')
    print(Fore.RESET, end="")
    print(Fore.RED + "donot use, educational purposes only.")
    print("Support by Upgrading to Spotify Premium :)")
    print()
    print(Fore.RESET, end="")


def main():
    global spotify_install_path
    global reg_spotify_path
    global winapp_spotify_path
    global skiped_ads
    global paused
    global end_watch
    global spotify_pids
    details()
    print("[info]: trying to start Spotify...")
    threading.Thread(target=paused_listener).start()
    # if spotify is not running do the below code.
    if not spotify_running():
        try:
            # tries to start spotify from regular path.
            start_spotify(True, reg_spotify_path)
        except FileNotFoundError:
            try:
                # tries to start spotify from windowsapp path.
                start_spotify(True, winapp_spotify_path)
            except FileNotFoundError:
                # if it doesnot find Spotify at these locations oh no you need spotify
                # Or feel free to change [reg_spotify_path] to the location where spotify is located
                print(
                    Fore.RED + "[error]: Spotify not found in default locations.")
                print(Fore.RESET, end="")
            else:
                # sets the spotify_install_path if spotify is found at winapp
                spotify_install_path = winapp_spotify_path
        else:
            # sets the spotify_install_path if spotify is found at regular path.
            spotify_install_path = reg_spotify_path
    else:
        # if spotify is already running... get pids and set spotify_install_path
        print("[info]: Spotify already running...")
        get_spotify_pid()
        if os.path.exists(reg_spotify_path):
            spotify_install_path = reg_spotify_path
        else:
            spotify_install_path = winapp_spotify_path
    # ________________ done with starting Spotify.________________________
    try:
        # now start the spowatch.
        # spowatch does not watch spotify... it looks at available windows titles...
        # if it finds any window with title Advertisment it checks if the window is spotify or not...
        # if it is spotify it restarts the app and continues playing.
        print("[info]: running spowatch...")
        while True:
            if not paused:
                EnumWindows(winEnumHandler, None)
                time.sleep(0.5)
            else:
                time.sleep(1)
    # some other fancy stuff on keyboard interrupt never mind.
    except KeyboardInterrupt:
        print("[info]: keyboard interrupt, ending watch")
        end_watch = True
        if("y" == input("close Spotify? (y/n): ")):
            kill_spotify()
        print(Fore.GREEN + "[info]: ads skipped: "+str(skiped_ads))
        print(Fore.RESET, end="")
        try:
            input("press Enter key to exit...")
        except [KeyboardInterrupt, EOFError]:
            pass

    except psutil.NoSuchProcess:
        print("[info]: process no longer exist, ending watch")
        end_watch = True
        if("y" == input("close Spotify? (y/n): ")):
            kill_spotify()
        print(Fore.GREEN + "[info]: ads skipped: "+str(skiped_ads))
        print(Fore.RESET, end="")
        try:
            input("press Enter key to exit...")
        except [KeyboardInterrupt, EOFError]:
            pass


if __name__ == "__main__":
    main()
