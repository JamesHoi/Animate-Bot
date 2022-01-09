import pyaudio
import wave

# 录音参数
# 定义数据流块
CHUNK = 2000#1024
FORMAT = pyaudio.paFloat32
CHANNELS = 2
RATE = 32000

def get_recordFrames(seconds,FORMAT=FORMAT):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,channels=CHANNELS,rate=RATE,input=True,frames_per_buffer=CHUNK)
    # 开始录音
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
        data = stream.read(CHUNK)
        frames.append(data)
    # 关闭数据流
    stream.stop_stream()
    stream.close()
    #print("* done recording")
    return b''.join(frames)

# 保存语音为.pcm
def save_recordFrames(filename,frames,FORMAT=FORMAT):
    p = pyaudio.PyAudio()
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(frames)
    wf.close()