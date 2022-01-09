import os
import numpy as np  # 调用numpy模块记作np
from speech.stream import *

#最短需要4个buffer才有能成为二进制语音
MIN_BUFFER = 4
#单线程下的参数
#采样时间
SAMP_TIME = 0.5

# 标定
# 要写入的文件名
WAVE_OUTPUT_FILENAME = "speech/audio/calibration.wav"
# 标定录音时间
RECORD_SECONDS = 5

# 调试
DEBUG = False

min_amplitude,tic_stop = 0,0
is_talking,tic,toc = False,False,False

# 是否标定
def is_calibrated():
    return os.path.exists(WAVE_OUTPUT_FILENAME)


# 返回判断为有声音的最小振幅
def calibrate(sensitivity):
    # 获取语音
    if(os.path.isfile(WAVE_OUTPUT_FILENAME)):
        print("找到标定音频")
        print("若发现无法正确判断是否在讲话，请先将标定音频[{}]删除后重新标定".format(WAVE_OUTPUT_FILENAME))
        f = wave.open(WAVE_OUTPUT_FILENAME, "rb")  # 读取语音文件
        nchannels, sampwidth, framerate, nframes = f.getparams()[:4]  # 获取音频参数
        wave_data = f.readframes(nframes)
        global RECORD_SECONDS,RATE
        RATE = framerate
        RECORD_SECONDS = nframes/framerate
    else:
        print("未找到标定音频，请保持周围声音正常且在{}秒内随意说一段话".format(RECORD_SECONDS))
        wave_data = get_recordFrames(RECORD_SECONDS)
    # 转换语音数据格式
    wave_data = np.fromstring(wave_data, dtype=np.float)
    # 记录语音，每次打开只需输入灵敏度
    save_recordFrames(WAVE_OUTPUT_FILENAME, wave_data)
    # 归一化
    wave_data_normal = wave_data * 1.0 / (max(abs(wave_data)))
    #灵敏度判断
    filter = np.where(wave_data_normal >= 1-sensitivity)
    if len(filter[0]) != 0:
        # 找到最小值的索引
        min_index = filter[0][np.argmin(wave_data[filter])]
        # 半秒的采样点数
        half_seconds_frames = RATE*0.5
        # 取灵敏度之中最小值的半秒内
        if(min_index-half_seconds_frames/2<0):
            half = wave_data[0:int(min_index+half_seconds_frames)]
        elif(min_index+half_seconds_frames/2>wave_data.size):
            half = wave_data[int(wave_data.size-half_seconds_frames):wave_data.size]
        else:
            half = wave_data[int(min_index-half_seconds_frames/2):int(min_index+half_seconds_frames/2)]
        # 均值
        global min_amplitude
        min_amplitude = wave_data[min_index]#np.mean(np.abs(half))/2
        return min_amplitude
    else:
        print("灵敏度太低，检测不到你正在说话，退出程序重试")
        return 0

# 获取振幅
def getAmplitude(frames):
    if(len(frames) < MIN_BUFFER*CHUNK):
        return 0
    else:
        amplitude = np.max(np.abs(np.fromstring(frames, dtype=np.short)))
        if DEBUG:print(amplitude)
        return amplitude
