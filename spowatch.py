import win32gui
import win32process
import psutil
import os
import time
import watch
from pynput.keyboard import Key, Controller


def killThread():
    print("terminating spotify...")
    process_name = "Spotify"
    # pid = None
    for proc in psutil.process_iter():
        if process_name in proc.name():
            proc.kill()


def getPid():
    process_name = "Spotify"
    pid = []
    for proc in psutil.process_iter():
        if process_name in proc.name():
            pid.append(proc.pid)
    watch.pid_watch(pid, "w")


def startApp():
    print("starting spotify...")
    path = "C:/Users/va/AppData/Roaming/Spotify/Spotify.exe"
    os.startfile(path)
    watch.write_watch()
    getPid()
    play()


def play():
    keyboard = Controller()
    keyboard.press(Key.ctrl)
    keyboard.press(Key.right)
    keyboard.release(Key.right)
    keyboard.release(Key.ctrl)


# TODO handle keyboard strokes
pass


def winEnumHandler(hwnd, ctx):

    if win32gui.IsWindowVisible(hwnd):
        wintext = win32gui.GetWindowText(hwnd)
        tid, pid = win32process.GetWindowThreadProcessId(hwnd)

        li = watch.pid_watch("none", "r")
        if wintext != None and wintext != "" and wintext != " ":
            if wintext == "Spotify Free" or wintext == "Advertisement":
                if watch.read_watch() < 1:
                    print("Ad dectected or song paused...")
                    killThread()
                    time.sleep(0.5)
                    startApp()

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
    watch.init_watch()
    startApp()
    try:
        print("running spotify watcher...")
        while True:
            win32gui.EnumWindows(winEnumHandler, None)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\nkeyboard interrupt, ending watch...\n")
        watch.end_watch()
    except psutil.NoSuchProcess:
        print("process no longer exist, ending watch...")
        watch.end_watch()


if __name__ == "__main__":
    main()


# todo: need to play after starting the app
