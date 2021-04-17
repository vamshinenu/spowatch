import os


def init_watch():
    with open("adwatch.txt", "w") as f:
        f.write(str(0))
        f.close()


def read_watch():
    with open("adwatch.txt", "r") as f:
        retval = int(float(f.read()))
        f.close()
    return retval


def write_watch(mode=1):
    val = read_watch()
    with open("adwatch.txt", "w") as f:
        f.write(str(val + mode))
        f.close()


def end_watch():
    if os.path.exists("adwatch.txt"):
        os.remove("adwatch.txt")
    if os.path.exists("pid.txt"):
        os.remove("pid.txt")
    if os.path.exists("songwatch.txt"):
        os.remove("songwatch.txt")


def pid_watch(data, mode):
    if not os.path.exists("pid.txt"):
        file = open("pid.txt", "w")
        file.close()

    if mode == "w":
        with open("pid.txt", "w") as file:
            file.write(str(data))
            file.close()
    if mode == "r":
        with open("pid.txt", "r") as file:
            filedat = file.read()
            file.close()
        data = filedat.strip('][').split(', ')
        return data


def song_watch(current_song):
    if not os.path.exists("songwatch.txt"):
        file = open("songwatch.txt", "w")
        file.close()

    previous_song = ""
    with open("songwatch.txt", "r") as file:
        previous_song = file.read()

    if previous_song != current_song:
        with open("songwatch.txt", "w") as file:
            file.write(current_song)
            file.close
        return True
    else:
        False
