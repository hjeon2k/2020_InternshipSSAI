from moviepy.video.tools.subtitles import SubtitlesClip
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
import numpy as np

'''
def encodesub(a, b, c):
    # a, b, c : video, subtitle, video with subtitles
    myvideo = VideoFileClip(a)
    w = myvideo.w
    h = myvideo.h
    generator = lambda txt: TextClip(txt,size=(0.8*w, None), font='Xolonium-Bold', fontsize=int(w/40), color='white', stroke_color='black', stroke_width=(w/1400), method = 'caption')
    print(w/60)
    sub = SubtitlesClip(b, generator)
    sub.pos=lambda t:(w*0.1,h*0.82)
    final = CompositeVideoClip([myvideo, sub])
    final.write_videofile(c, fps=myvideo.fps)
'''

def encodesub(a, b, c):
    # a, b, c : video, subtitle, video with subtitles
    ratio = 0.3 # ratio = (subtitle part width) / original video width
    sub_background_color = 127

    myvideo = VideoFileClip(a)
    w = myvideo.w
    h = myvideo.h
    w_subtitle = int(ratio*w)
    big_image = np.zeros((h, w + w_subtitle, 3))
    image = np.ones((h, w_subtitle, 3)) * sub_background_color
    imageclip = ImageClip(image,  duration = myvideo.duration)
    big_imageclip = ImageClip(big_image, duration = myvideo.duration)
    imageclip.pos = lambda t:(w, 0)
    #imageclip = imageclip.set_opacity(0.5)
    generator = lambda txt: TextClip(txt,size=(w_subtitle - 2*int(w/150), None), font='Xolonium-Bold', fontsize=int(w/50), color='white',  method = 'caption')
    #generator = lambda txt: TextClip(txt,size=(0.8*w, None), font='Xolonium-Bold', fontsize=int(w/40), color='white', stroke_color='black', stroke_width=(w/1400), method = 'caption')
    sub = SubtitlesClip(b, generator)
    sub.pos=lambda t:(w+int(w/150),int(w/100))
    final = CompositeVideoClip([big_imageclip, myvideo, imageclip, sub])
    final.write_videofile(c, fps=myvideo.fps)
