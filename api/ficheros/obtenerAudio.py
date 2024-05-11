from moviepy.editor import VideoFileClip
import librosa
from scipy.io import wavfile
import os

def extract_audio(input_file):
    
    # Carga el video
    video_clip = VideoFileClip(input_file)

    # Extrae el audio del video
    audio = video_clip.audio

    output = input_file.split('.')[0] + '.wav'    

    # Escribe el archivo
    audio.write_audiofile(output, codec='pcm_s16le', fps=audio.fps)

    return output

def get_mel_spect(wav_path, feat_sec, n_mels, eps):

    samplerate, data = wavfile.read(wav_path)
    data, samplerate = librosa.load(wav_path, sr = samplerate)

    os.remove(wav_path)

    mel_spect = librosa.feature.melspectrogram(y=data, sr=samplerate, hop_length= samplerate // feat_sec, window='hann', n_mels=n_mels)
    if (mel_spect == 0).mean() == 1:
        mel_spect += eps

    return mel_spect

def vid2mel(video_path, feat_sec = 100, n_mels = 128, eps=1e-05):

    print(f"Extrayendo audio de {video_path}")
    wav_path = extract_audio(video_path)

    print(f"Extrayendo features de audio de {video_path}")
    mel_spect = get_mel_spect(wav_path, feat_sec, n_mels, eps)
    print(f"Features de audio de {video_path} extraídos")
    return mel_spect

def wav2mel(wav_path, feat_sec = 100, n_mels = 128, eps=1e-05):
    mel_spect = get_mel_spect(wav_path, feat_sec, n_mels, eps)
    return mel_spect