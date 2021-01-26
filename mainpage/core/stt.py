
#-*- coding: utf-8 -*-
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
import srt
import datetime
import wave

n = 1 # number of channels in audio file. 1or2or3
def speech_to_text(config, audio):
    client = speech.SpeechClient()
    operation = client.long_running_recognize(
        request={"config": config, "audio": audio}
    )
    response = operation.result()
    x = subtitle_generation(response)
    srtfile = x[0]
    scriptfile = x[1]
#    with open("subtitle.txt", "w") as file:
#        file.write(srtfile)
#    with open("script.txt", "w") as file:
#        file.write(scriptfile)
    return srtfile, scriptfile
def subtitle_generation(speech_to_text_response, bin_size=3):
    """We define a bin of time period to display the words in sync with audio.
    Here, bin_size = 3 means each bin is of 3 secs.
    All the words in the interval of 3 secs in result will be grouped togather."""
    transcriptions = []
    index = 0
    words = []
    timestamps = []
    scriptword = []
    for result in speech_to_text_response.results:
        try:
            transcript = result.alternatives[0].transcript
            for word in result.alternatives[0].words:
                timestamps.append((word.start_time.seconds, word.start_time.microseconds, word.end_time.seconds, word.end_time.microseconds))
                words.append(word.word)
            scriptword.append(transcript)
        except IndexError:
            pass
    timestamps_real=[]
    timestamp_indexes = []
    words_real = []
    for i in range(len(timestamps)):
        if timestamps[i] not in timestamps_real:
            timestamps_real.append(timestamps[i])
            timestamp_indexes.append(i)

    for i in timestamp_indexes:
        words_real.append(words[i])
    start_index = 0
    final_index = 0
    sen = ""
    for i in range(len(words_real)):
        sen = sen + " " + words[i]
        if(words[i][-1] in ['.', '?', '!', '다', '요','까', '죠']  or i == len(words) -1):
            final_index = i
            index += 1
            transcriptions.append(srt.Subtitle(index, datetime.timedelta(0, timestamps_real[start_index][0], timestamps_real[start_index][1]), datetime.timedelta(0, timestamps_real[final_index][2]+2, timestamps_real[final_index][3]), sen))
            sen = ""
            start_index = i+1
    subtitles = srt.compose(transcriptions)
    script = " ".join(scriptword)
    return subtitles, script            
#audio = speech.types.RecognitionAudio(uri="gs://voice_files_sypark/1min.wav")

"""
config = speech.RecognitionConfig(
    encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=44100,
    language_code="ko-KR",
    enable_automatic_punctuation = True,
    enable_word_time_offsets = True,
    enable_word_confidence=True,
    enable_speaker_diarization=True,
    audio_channel_count=n
)
"""

#speech_to_text(config, audio)

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

'''
def stt(audio, slan='ko-KR'):
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code=slan,
        enable_automatic_punctuation = True,
        enable_word_time_offsets = True,
        enable_word_confidence=True,
        enable_speaker_diarization=True,
        audio_channel_count=n
    )
    return speech_to_text(config, audio)
'''

def stt(samplerate, audio, slan='ko-KR'):
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=samplerate,
        language_code=slan,
        enable_automatic_punctuation = True,
        enable_word_time_offsets = True,
        enable_word_confidence=True,
        enable_speaker_diarization=True,
        audio_channel_count=n
    )
    return speech_to_text(config, audio)
