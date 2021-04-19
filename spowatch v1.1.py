import getpass
import win32gui
import win32process
import psutil
import os
import time
import watch
import asyncio
from winrt.windows.media.control import \
    GlobalSystemMediaTransportControlsSessionManager as MediaManager


async def get_media_info():
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

                return info_dict
    except Exception:
        print("make sure Spotify is open")


async def pause():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    await current_session.try_pause_async()


async def play():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    await current_session.try_play_async()


async def next():
    sessions = await MediaManager.request_async()
    current_session = sessions.get_current_session()
    await current_session.try_skip_next_async()

user = getpass.getuser()
spotify_path = "C:/Users/"+user+"/AppData/Roaming/Spotify/Spotify.exe"
winapp_spotify_path = "C:/Users/"+user + \
    "/AppData/Local/Microsoft/WindowsApps/SpotifyAB.SpotifyMusic_zpdnekdrzrea0/Spotify.exe"
correct_spotify_path = ""


def killThread():
    print("terminating spotify...")
    process_name = "Spotify"
    # pid = None
    for proc in psutil.process_iter():
        if process_name in proc.name():
            try:
                proc.kill()
            except psutil.NoSuchProcess:
                pass


def getPid():
    process_name = "Spotify"
    pid = []
    for proc in psutil.process_iter():
        if process_name in proc.name():
            pid.append(proc.pid)
    watch.pid_watch(pid, "w")


def startApp(init):
    print("starting spotify...")
    os.startfile(correct_spotify_path)
    watch.write_watch()
    getPid()
    time.sleep(1)
    if init:
        asyncio.run(play())
    else:
        asyncio.run(next())


def winEnumHandler(hwnd, _):
    global paused
    if win32gui.IsWindowVisible(hwnd):
        wintext = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        li = watch.pid_watch("none", "r")
        if wintext != None and wintext != "" and wintext != " ":
            if wintext == "Spotify Free" or wintext == "Advertisement":

                current_media_info = asyncio.run(get_media_info())

                if((current_media_info["title"] == "Spotify Free") or (current_media_info["title"] == "Advertisement")):
                    print("Ad dectected...")
                    killThread()
                    time.sleep(0.5)
                    startApp(False)
                    watch.write_watch()
            elif str(pid) in li:
                if "Spotify" in wintext:
                    pass
                else:
                    watch.init_watch()
                    h = wintext.rstrip().lstrip()
                    if watch.song_watch(h):
                        print("playing: ", end=" ")
                        print(h)


def main():
    global correct_spotify_path
    try:
        os.startfile(spotify_path)
    except FileNotFoundError:
        try:
            os.startfile(winapp_spotify_path)
        except FileNotFoundError:
            print("spotify not installed!")
        else:
            correct_spotify_path = winapp_spotify_path
            pass
        pass
    else:
        correct_spotify_path = spotify_path
        pass

    watch.init_watch()
    startApp(True)
    try:
        print("running spotify watcher...")
        while True:
            win32gui.EnumWindows(winEnumHandler, None)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\nkeyboard interrupt, ending watch...\n")
        watch.end_watch()
        killThread()
    except psutil.NoSuchProcess:
        print("process no longer exist, ending watch...")
        killThread()
        watch.end_watch()


if __name__ == "__main__":
    main()
