from pyray import *
import os
import json
import math
import threading
import time
from tkinter import filedialog
import eyed3
from mGRFXLib import *
version = "0.0.2"

class display:
    # Width of display
    x = 1500
    # Height of display
    y = 300

    # Background colour
    unlit = (153, 255, 255, 255)
    # Quarter accent colour
    quarter = (51, 153, 204, 64)
    # Half accent colour
    half = (51, 153, 204, 128)
    # Content colour
    lit = (51, 153, 204, 255)

    # Font file initially is none in case loading the font errors
    # Doing this allows raylib to return to default fonts
    fontPath = "monogram.fnt"
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
    "sunset": [(40, 20, 35, 255), (255, 180, 40, 128), (247, 200, 40, 200), (240, 230, 40, 255)],
    "musikcube": [(24, 24, 20, 255), (220, 82, 86, 128), (230, 220, 116, 128), (166, 226, 46, 255)],
    "bento": [(39, 44, 47, 255), (85, 101, 106, 64), (196, 196, 196, 128), (147, 175, 185, 255)],
    "solar": [(255, 255, 255, 255), (0, 0, 0, 64), (0, 0, 0, 128), (0, 0, 0, 255)],
    "lunar": [(0, 0, 0, 255), (255, 255, 255, 64), (255, 255, 255, 128), (255, 255, 255, 255)],
    "greenscreen": [(0, 255, 0, 255), (0, 0, 0, 64), (0, 0, 0, 128), (0, 0, 0, 255)]
}

class user:
    theme = "default"
    volume = 1.0
    loop = True

class current:
    path = None
    stream = None
    title = "None"
    artist = "None"
    album = "None"
    time = 0
    length = 0
    status = "Stopped"

def loadSettings():
    if os.path.exists("settings.json"):
        settings = json.load(open("settings.json", "r"))
        print("mGRFXVis: Opening settings.json for reading...")
        display.x = settings.get("screenX", 1500)
        display.y = settings.get("screenY", 300)
        display.fontPath = settings.get("font", "monogram.fnt")
        user.theme = settings.get("theme", "default")
        user.volume = settings.get("volume", 1.0)
        user.loop = settings.get("loop", True)
        current.path = settings.get("lastFile", None)
        print("mGRFXVis: settings.json read!")
    else:
        settings = open("settings.json", "w")
        print("mGRFXVis: Opening settings.json for writing...")
        settings.write("{\n}")
        print("mGRFXVis: Null file written!")
        settings.close()

def dumpSettings():
    file = open("settings.json", "w")
    print("mGRFXVis: Opening settings.json for writing...")
    settings = { 
        "screenX": display.x,
        "screenY": display.y,
        "font": display.fontPath,
        "theme": user.theme,
        "volume": user.volume,
        "loop": user.loop,
        "lastFile": current.path
    }
    print("mGRFXVis: Settings formatted!")
    json.dump(file, settings)
    print("mGRFXVis: Settings dumped!")

def setTheme(theme : str = "default"):
    if theme in themes:
        display.unlit = themes[theme][0]
        display.quarter = themes[theme][1]
        display.half = themes[theme][2]
        display.lit = themes[theme][3]

formatTime = lambda time : f"{math.floor(time / 60)}:{math.floor(time % 60):02d}"
roundFloat = lambda value, base : base * round(value / base)

def promptFile(windowTitle : str = f"mGRFXVis {version}", files : list = ("All files", "*.*")):
    filepath = filedialog.askopenfilename(title = windowTitle, filetypes = files)
    if filepath == "":
        filepath = None
    print(f"mGRFXVis: promptFile() returned with {filepath}")
    return filepath

def loadSong(filepath : str = None):
    if filepath == None:
        filepath = promptFile("mGRFXVis - Select Music", [("Audio files (.mp3, .wav, .ogg, .flac)", ["*.mp3", "*.wav", "*.ogg", "*.flac"]), ("mGRFXVis lyric files (.GRV, .txt)", ["*.GRV", "*.txt"]), ("All files", "*.*")])
    if filepath != None:
        try:
            file = eyed3.load(filepath)
            current.artist = file.tag.artist
            current.title = file.tag.title
            current.album = file.tag.album
            current.length = file.info.time_secs
            current.stream = load_music_stream(filepath)
            set_window_title(f"mGRFXVis {version}: {current.title} - {current.artist}")
            print(f"mGRFXVis: Track {current.title} by {current.artist} off of {current.album} loaded!")
            print(f"mGRFXVis: Track length is {current.length} seconds")
            play_music_stream(current.stream)
            current.status = "Playing"
        except:
            current.title = "None"
            current.artist = "None"
            current.album = "None"
            current.time = 0
            current.length = 0
            current.stream = None
            set_window_title(f"mGRFXVis {version}")
            current.status = "Stopped"

def printLayout(mainLine : str = ""):
    begin_drawing()
    clear_background(display.unlit)
    draw_text_ex(display.font, layout.header["text"], (layout.header["x"], layout.header["y"]), layout.header["size"], layout.header["spacing"], display.lit)
    draw_text_ex(display.font, formatTime(current.time), (layout.currentTime["x"], layout.currentTime["y"]), layout.currentTime["size"], layout.currentTime["spacing"], display.lit)
    draw_text_ex(display.font, "/", (layout.divider["x"], layout.divider["y"]), layout.divider["size"], layout.divider["spacing"], display.lit)
    draw_text_ex(display.font, formatTime(current.length), (layout.fileTime["x"], layout.fileTime["y"]), layout.fileTime["size"], layout.fileTime["spacing"], display.lit)
    draw_text_ex(display.font, current.status, (layout.status["x"], layout.status["y"]), layout.status["size"], layout.status["spacing"], display.half)
    draw_text_ex(display.font, f"Vol {roundFloat(int(user.volume * 100), 5)}", (layout.volume["x"], layout.volume["y"]), layout.volume["size"], layout.volume["spacing"], display.lit)
    draw_text_ex(display.font, mainLine, (layout.mainString["x"], layout.mainString["y"]), layout.mainString["size"], layout.mainString["spacing"], display.lit)
    end_drawing()

def displayScreen():
    print("mGRFXVis: Display thread started!")
    while not window_should_close():
        display = [f"Title: {current.title}", f"Artist: {current.artist}", f"Album: {current.album}"]
        printLayout()
    print("mGRFXVis: Display thread closed!")

def senseInput():
    print("mGRFXVis: Input thread started!")
    while not window_should_close():
        if is_key_down(341) and is_key_down(79):
            current.status = "Loading"
            print("mGRFXVis: Loading track file...")
            loadSong()
        if current.stream != None:
            if is_key_down(32):
                if is_music_stream_playing(current.stream):
                    pause_music_stream(current.stream)
                    current.status = "Stopped"
                    time.sleep(0.5)
                else:
                    resume_music_stream(current.stream)
                    current.status = "Playing"
                    time.sleep(0.5)
            elif is_key_down(262):
                if not is_key_down(340):
                    if current.time + 5 < current.length:
                        seek_music_stream(current.stream, current.time + 5)
                        current.status = "Fast-forwarding"
                    else:
                        current.time = 0
                        seek_music_stream(current.stream, current.time)
                else:
                    seek_music_stream(current.stream, 0)
                time.sleep(0.5)
            elif is_key_down(263):
                if current.time - 5 >= 0:
                    seek_music_stream(current.stream, current.time - 5)
                    current.status = "Rewinding"
                else:
                    current.time = 0
                    seek_music_stream(current.stream, current.time)
                time.sleep(0.5)
            elif is_key_down(265):
                if user.volume + 0.05 <= 1:
                    user.volume = user.volume + 0.05
                else:
                    user.volume = 1
                set_music_volume(current.stream, user.volume)
                time.sleep(0.1)
            elif is_key_down(264):
                if user.volume - 0.05 >= 0:
                    user.volume = user.volume - 0.05
                else:
                    user.volume = 0
                set_music_volume(current.stream, user.volume)
                time.sleep(0.1)
            elif user.volume <= 0:
                current.status = "Muted"
            elif is_music_stream_playing(current.stream):
                current.status = "Playing"
            
    print("mGRFXVis: Input thread closed!")
    close_window()

def playStream():
    print("mGRFXVis: Player thread started!")
    while not window_should_close():
        if current.stream != None:
            if is_music_stream_playing(current.stream):
                current.time = get_music_time_played(current.stream)
                update_music_stream(current.stream)
    print("mGRFXVis: Player thread closed!")
    close_window()



init_audio_device()
loadSettings()
init_window(display.x, display.y, f"mGRFXVis {version}")
display.font = load_font(display.fontPath)
printLayout()
musicHandler = threading.Thread(target = playStream)
inputHandler = threading.Thread(target = senseInput)
musicHandler.start()
time.sleep(0.2)
inputHandler.start()
while not window_should_close():
    printLayout()
    if window_should_close():
        dumpSettings()
close_window()