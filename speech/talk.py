
from speech.playsound import playsound
from api.chat_api import get_chat_ans
from api.tts_api import get_tts_audio
from speech.rt_stream import get_talkOnce
from api.asr_api import asr
#from render import animate

def talk_loop():
    while True:
        audio = get_talkOnce(30)  # 超时时间30秒
        user_text = asr(audio)["result"][0]
        if user_text == "": continue  # 若未检测到用户说话则重新开始
        print("[INFO]你说的话：", user_text)

        # 获取机器人回答
        text = get_chat_ans(user_text)
        print("[INFO]机器人的回答:", text)
        audio_path = get_tts_audio(text)

        '''
        # 输出音频并令人物摇头
        animate.IS_MOVING = True
        p = playsound()
        p.play(audio_path)
        p.close()
        animate.IS_MOVING = False
        '''
