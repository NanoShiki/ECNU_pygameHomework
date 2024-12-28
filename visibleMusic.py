import librosa
import numpy as np
import matplotlib.pyplot as plt

# 加载音频文件
audio_file = "C:/Users/ruheng47/Desktop/一等情事.wav"  # 替换为你的音频文件路径
y_audio, sr = librosa.load(audio_file)

# 提取节拍
tempo, beats = librosa.beat.beat_track(y=y_audio, sr=sr)

# 输出节奏信息
print(f"Tempo: {tempo} BPM")
print(f"Beats: {beats}")

# 生成二维坐标
# X坐标为节拍位置（时间）
x = librosa.frames_to_time(beats, sr=sr)

# 提取相应节拍的音量作为Y坐标
volume = []
for i in range(len(beats) - 1):
    start_sample = librosa.frames_to_samples(beats[i])
    end_sample = librosa.frames_to_samples(beats[i + 1])
    segment = y_audio[start_sample:end_sample]
    rms = np.sqrt(np.mean(segment**2))  # 计算均方根值作为音量
    volume.append(rms)

y = volume  # 使用RMS值作为Y坐标

# 只保留与x相匹配的y
if len(y) < len(x):
    x = x[:len(y)]

for i in range(len(x)):
    print(x[i], y[i])