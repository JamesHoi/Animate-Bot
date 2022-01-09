import _thread
from speech.rt_stream import calibrate
from speech.talk import talk_loop
#from render.animate import render_loop


if __name__ == '__main__':
    calibrate(0.6)  # 灵敏值
 #   _thread.start_new_thread(render_loop, ())
    _thread.start_new_thread(talk_loop, ())
    input()  # 阻塞防止主线程退出
