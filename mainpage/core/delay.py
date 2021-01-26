from moviepy.editor import VideoFileClip, AudioFileClip
import math
from scipy.io import wavfile
import os

def stt_translate_delay(file_path):
    f, ext = os.path.splitext(file_path)
    if ext!='.mp4' and ext!=".mov" and ext!=".avi":
        clip_duration = AudioFileClip(file_path).duration/60
    else:
        clip_duration = VideoFileClip(file_path).duration/60
    delaytime = 0.28 * clip_duration + 0.5
    if delaytime > 1.8:
        return math.ceil(delaytime)
    else:
        return math.ceil(delaytime * 10)/10

def encode_delay(filesize):
    filesize_inMB = filesize/1048576
    if filesize_inMB > 100:
        time = filesize_inMV*0.6
    else:
        time = 0.07*filesize_inMB**1.6
    if time > 1.8:
        return round(time)
    else:
        return round(time, 1)
