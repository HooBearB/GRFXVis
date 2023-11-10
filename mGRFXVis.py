from pyray import *
from tkinter import filedialog
import os
import random
import time
import math
import eyed3
eyed3.log.setLevel("ERROR")
import mGRFXLib as mgrfx
version = "0.0.1"

class display:
    x = 1500
    y = 300

    unlit = (153, 255, 255, 255)
    quarter = (51, 153, 204, 64)
    half = (51, 153, 204, 128)
    lit = (51, 153, 204, 255)

    font = None

class layout:
    header = {"text": f"mGRFXVis {version}", "x": 1350, "y": 15, "size": 20, "spacing": 0}
    currentTime = {"x": 10, "y": -10, "size": 120, "spacing": -1}
    divider = {"char": "/", "x": 230, "y": -10, "size": 120, "spacing": 0}
    fileTime = {"x": 270, "y": 40, "size": 60, "spacing": -1}
    mainString = {"x": 10, "y": 40, "size": 250, "spacing": -3}
    volume = {"x": 400, "y": 40, "size": 60, "spacing": -1}
    status = {"x": 400, "y": 10, "size": 40, "spacing": 0}

themes = {
    "default": [(153, 255, 255, 255), (51, 153, 204, 64), (51, 153, 204, 128), (51, 153, 204, 255)],
    "inverted": [(51, 153, 204, 255), (153, 255, 255, 64), (153, 255, 255, 128), (153, 255, 255, 255)],
    "e-ink": [(175, 175, 180, 255), (65, 65, 70, 64), (65, 65, 70, 128), (65, 65, 70, 255)],
    "solar": [(255, 255, 255, 255), (0, 0, 0, 64), (0, 0, 0, 128), (0, 0, 0, 255)],
    "lunar": [(0, 0, 0, 255), (255, 255, 255, 64), (255, 255, 255, 128), (255, 255, 255, 255)],
    "sunset": [(40, 20, 35, 255), (255, 180, 40, 128), (247, 200, 40, 200), (240, 230, 40, 255)],
    "lambda": [(57, 39, 27, 255), (98, 255, 26, 255), (21, 62, 168, 255), (208, 75, 0, 255)],
    "musikcube": [(24, 24, 20, 255), (220, 82, 86, 128), (230, 220, 116, 128), (166, 226, 46, 255)]
}

class user:
    theme = "default"
    volume = 1.0
    loop = True

class current:
    working = False
    gotFile = False
    title = "None"
    artist = "None"
    album = "None"
    time = 0
    length = 0
    order = 0
    iter = 0
    hold = 0
    pause = 0
    id = 0

def determineString():
    displayOrder = ["Title: " + current.title, "Artist: " + current.artist, "Album: " + current.album]
    if current.iter > len(displayOrder[current.order % 3]):
        current.iter = 0
        current.order = current.order + 1

    if current.hold < 20 and current.iter == 0:
        current.hold = current.hold + 1
    else:
        current.hold = 0
        if current.pause % 4 == 0:
            current.iter = current.iter + 0.1
        current.pause = current.pause + 1

    return displayOrder[current.order % 3][int(current.iter):int(current.iter) + 13]

def promptFile(windowTitle, files):
    filepath = filedialog.askopenfilename(title = windowTitle, filetypes = files)
    if filepath == "":
        filepath = None
    print(f"mGRFXVis: promptFile() returned with {filepath}")
    return filepath

def formatTime(time):
    return f"{math.floor(time / 60)}:{math.floor(time % 60):02d}"

def setTheme(theme = None):
    if theme == None:
        display.unlit = themes[user.theme][0]
        display.quarter = themes[user.theme][1]
        display.half = themes[user.theme][2]
        display.lit = themes[user.theme][3]
    else:
        user.theme = theme

def changeTheme(theme = None):
    themeList = list(themes.keys())
    select = themeList.index(user.theme)
    if theme == None:
        while not is_key_down(257):
            begin_drawing()
            clear_background(display.unlit)
            x = 50
            y = 25
            for option in themeList:
                if option == user.theme:
                    draw_text_ex(display.font, f"- {option}", (x, y), 50, 2, display.quarter)
                    draw_text_ex(display.font, f"- {option}", (x + 3, y), 50, 2, display.half)
                    draw_text_ex(display.font, f"- {option}", (x + 6, y), 50, 2, display.lit)
                else:
                    draw_text_ex(display.font, option, (x, y), 50, 2, display.half)
                if y >= 180:
                    x = x + 300
                    y = -25
                y = y + 50
            end_drawing()
            if is_key_down(265) and select - 1 >= 0:
                select = select - 1
            elif is_key_down(264) and select + 1 < len(themeList):
                select = select + 1
            user.theme = themeList[select]
            setTheme()
            time.sleep(0.2)
    else:
        setTheme(theme)

def loadSong(filepath):
    try:
        file = eyed3.load(filepath)
        current.artist = file.tag.artist
        current.title = file.tag.title
        current.album = file.tag.album
        current.length = file.info.time_secs
        current.order = 0
        current.iter = 0
        current.hold = 0
        music = load_music_stream(filepath)
        play_music_stream(music)
        set_window_title(f"mGRFXVis {version}: {current.title} - {current.artist}")
        print(f"mGRFXVis: loadSong() loaded {current.title} by {current.artist} from {current.album} [{current.length}s]")
        return music, True
    except:
        print(f"mGRFXVis: loadSong() was not able to return music object")
        current.title = "None"
        current.artist = "None"
        current.album = "None"
        current.time = 0
        current.length = 0
        current.order = 0
        current.iter = 0
        current.hold = 0
        set_window_title(f"mGRFXVis {version}")
        return None, False

def getRandom():
    return random.choice(os.listdir("C:\\"))

def tryFile():
    music, current.working = loadSong(promptFile("Select a track", [("Audio files (.mp3, .wav, .ogg, .flac)", ["*.mp3", "*.wav", "*.ogg", "*.flac"]), ("All files", "*.*")]))
    current.gotFile = False
    return music

def determineStatus():
    if current.working:
        return "Playing"
    else:
        return "Stopped"

def printLayout():
    begin_drawing()
    clear_background(display.unlit)
    draw_text_ex(display.font, layout.header["text"], (layout.header["x"], layout.header["y"]), layout.header["size"], layout.header["spacing"], display.lit)
    fTime = formatTime(current.time)
    draw_text_ex(display.font, fTime, (layout.currentTime["x"], layout.currentTime["y"]), layout.currentTime["size"], layout.currentTime["spacing"], display.lit)
    draw_text_ex(display.font, "/", (layout.divider["x"], layout.divider["y"]), layout.divider["size"], layout.divider["spacing"], display.lit)
    draw_text_ex(display.font, formatTime(current.length), (layout.fileTime["x"], layout.fileTime["y"]), layout.fileTime["size"], layout.fileTime["spacing"], display.lit)
    draw_text_ex(display.font, determineStatus(), (layout.status["x"], layout.status["y"]), layout.status["size"], layout.status["spacing"], display.half)
    draw_text_ex(display.font, f"Vol {int(user.volume * 100)}", (layout.volume["x"], layout.volume["y"]), layout.volume["size"], layout.volume["spacing"], display.lit)
    draw_text_ex(display.font, determineString(), (layout.mainString["x"], layout.mainString["y"]), layout.mainString["size"], layout.mainString["spacing"], display.lit)
    end_drawing()

def checkPause(music):
    if is_key_down(32):
        if current.working == True:
            current.working = False
            pause_music_stream(music)
        else:
            current.working = True
            resume_music_stream(music)
        time.sleep(0.2)

def checkSeek(music):
    if is_key_down(262):
        if not is_key_down(340):
            if current.time + 5 < current.length:
                seek_music_stream(music, current.time + 5)
            else:
                current.time = 0
                seek_music_stream(music, current.time)
        else:
            seek_music_stream(music, 0)
        time.sleep(0.2)
    if is_key_down(263):
        if current.time - 5 >= 0:
            seek_music_stream(music, current.time - 5)
        else:
            current.time = 0
            seek_music_stream(music, current.time)
        time.sleep(0.2)

def checkVolume(music):
    if is_key_down(265):
        if user.volume + 0.01 <= 1:
            user.volume = user.volume + 0.01
        else:
            user.volume = 1
        set_music_volume(music, user.volume)
        time.sleep(0.02)
    if is_key_down(264):
        if user.volume - 0.01 >= 0:
            user.volume = user.volume - 0.01
        else:
            user.volume = 0
        set_music_volume(music, user.volume)
        time.sleep(0.02)

def checkPosition(music, linedata):
    time = get_music_time_played(music)
    for object in linedata:
        if object["t"] < time - 1:
            linedata.remove(object)
    if len(linedata) > 0:
        if time >= linedata[0]["t"]:
            if current.id == linedata[0]["id"]:
                print(f"mGRFXVis: {round(linedata[0]['t'], 4)} at {round(time, 4)} {linedata[0]['content']}")
                current.id = current.id + 1


        
init_audio_device()
init_window(display.x, display.y, f"mGRFXVis {version}")
display.font = load_font("monogram.fnt")
set_target_fps(120)
setTheme()
printLayout()
music = tryFile()
while not window_should_close():
    printLayout()
    if music != None:
        if is_music_stream_playing(music):
            update_music_stream(music)
            current.time = get_music_time_played(music)
    if is_key_down(341) and is_key_down(79):
        if is_key_down(340):
            filedata = mgrfx.loadFile(promptFile("Select a lyric file", [("mGRFXVis lyric files (.GRV, .txt)", ["*.GRV", "*.txt"]), ("All files", "*.*")]))
            seek_music_stream(music, 0)
            current.gotFile = True
            current.id = 0
        else:
            music = tryFile()
    if is_key_down(84):
        changeTheme()
    checkPause(music)
    checkSeek(music)
    checkVolume(music)
    if current.gotFile:
        checkPosition(music, filedata)
close_window()