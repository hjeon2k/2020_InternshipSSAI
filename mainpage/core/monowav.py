import moviepy.editor
from scipy.io import wavfile
import numpy as np
import os
import shutil
from django.conf import settings

def convertToWav(path_in, path_out, filename):
    VideoTypes=['mp4', 'MP4', 'mov', 'MOV', 'AVI', 'avi']
    AudioTypes=['wav', 'WAV', 'mp3', 'MP3', 'acc','ACC', 'mod','MOD', 'mpeg','MPEG', 's3m','S3M', 'xma','XMA']
    s= path_in[-3:-1]+path_in[-1]
    if (s in VideoTypes):
        shutil.copy(path_in, settings.MEDIA_ROOT + '/' + 'video_'+filename +'.'+ s)
        video=moviepy.editor.VideoFileClip(path_in)
        video.audio.write_audiofile(path_out)
    elif (s in AudioTypes):
        moviepy.editor.AudioFileClip(path_in).write_audiofile(path_out)
    os.remove(path_in)

def ToMonoWav(path_in, path_out):
    samplerate, data = wavfile.read(path_in)
    if data.ndim!=1:
        data = np.average(data, axis = 1)
    data = np.array(data, dtype='int16')
    wavfile.write(path_out, samplerate, data)
    os.remove(path_in)

def getWav(path, filename):
    p, ext = os.path.splitext(path)
    tmpWav = p + '_tmp.wav'
    convertToWav(path, tmpWav, filename)
    if os.path.isfile(tmpWav):
        ToMonoWav(tmpWav, p + '.wav')
        return True
    else: return False
