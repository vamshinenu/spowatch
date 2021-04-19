import win32gui
import win32process
import psutil
import os
import time
import watch
from pynput.keyboard import Key, Controller, Listener
import getpass

paused = False
user = getpass.getuser()
spotify_path = "C:/Users/"+user+"/AppData/Roaming/Spotify/Spotify.exe"
winapp_spotify_path = "C:/Users/"+user + \
    "/AppData/Local/Microsoft/WindowsApps/SpotifyAB.SpotifyMusic_zpdnekdrzrea0/Spotify.exe"
correct_spotify_path = ""


def on_press(key):
    global paused
    w = win32gui
    forwin = w.GetWindowText(w.GetForegroundWindow())
    if forwin == "Spotify Free":
        if key == Key.space:
            paused = not paused


def on_release(_):
    pass


def keyListener():
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()


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


def play(init):
    keyboard = Controller()
    if init:
        keyboard.press(Key.space)
    else:
        keyboard.press(Key.ctrl)
        keyboard.press(Key.right)
        keyboard.release(Key.right)
        keyboard.release(Key.ctrl)


def startApp(init):
    print("starting spotify...")
    # path = "C:/Users/va/AppData/Roaming/Spotify/Spotify.exe"
    os.startfile(correct_spotify_path)
    watch.write_watch()
    getPid()
    play(init)


# def block_spowatch():
#     w = win32gui
#     forwin = w.GetWindowText(w.GetForegroundWindow())
#     file = open("pausewatch.txt", "r")
#     p = file.read()
#     if p != 0:
#         if forwin == "Spotify Free" and paused:
#             file.close()
#             watch.pause_watch(1)
#             return False


def winEnumHandler(hwnd, _):
    global paused
    if win32gui.IsWindowVisible(hwnd):
        wintext = win32gui.GetWindowText(hwnd)
        _, pid = win32process.GetWindowThreadProcessId(hwnd)

        li = watch.pid_watch("none", "r")
        if not paused:
            if wintext != None and wintext != "" and wintext != " ":
                if wintext == "Spotify Free" or wintext == "Advertisement":
                    if watch.read_watch() < 1:
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
        else:
            print("song paused,spowatch is blocked")


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
    import threading
    threading.Thread(target=keyListener)
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
