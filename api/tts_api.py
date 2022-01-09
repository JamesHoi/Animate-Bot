from pyDes import des, ECB
import requests
import time
import json
import os
import urllib.parse
import psutil
from io import BytesIO
from PIL import Image
from api.debug import print_runtime

API_CONFIG_PATH = "api/api.config"
TTS_MP3_PATH = "api/tmp.mp3"

def request_tts(text,access_token,userId):
    POST_URL = "https://yuedu.data-baker.com/yuedu/v1/tts/content/synthesis/trial2"
    headers = {
        "authorization": "Basic Ymlhb2JlaTpiaWFvYmVpMTIz",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "content-type": "application/json;charset=UTF-8",
        "accept": "application/json, text/plain, */*",
        "userid": userId,
        "nounce": str(int(time.time()))[:6]
    }
    data = {
        "access_token": access_token,
        "bgmId": "0",
        "bgmVolume": "1",
        "captcha": "tr03r",
        "randomStr": "",
        "speed": 6,
        "ticket": "",
        "ttsContentList": [{
            "text": urllib.parse.quote(text),
            "voiceName": "二次元_未眠"
        }]
    }
    p = requests.post(POST_URL,json.dumps(data),headers=headers)
    return json.loads(p.content)["data"]["audioUrl"]

def decrypt_url(hex_s):
    DES_SECRET_KEY = 'bbkjbbyd'
    des_obj = des(DES_SECRET_KEY, ECB, DES_SECRET_KEY)
    secret_bytes = bytes.fromhex(hex_s)
    s = des_obj.decrypt(secret_bytes)   # 用对象的decrypt方法解密
    return s.decode()

def login():
    get_url = "https://yuedu.data-baker.com/yuedu/v1/wechat/code/get"
    ticket = json.loads(requests.get(get_url).content)["data"]["ticket"]
    code_url = "https://mp.weixin.qq.com/cgi-bin/showqrcode?ticket="
    result_url = "https://yuedu.data-baker.com/yuedu/v1/wechat/code/result?ticket="
    token_url = "https://yuedu.data-baker.com/yuedu/v1/authentication/openid?"

    # 通过openId和userId获取token
    def get_token(openId,userId):
        auth_url = token_url+"openId="+openId+"&userId="+userId
        content = requests.post(auth_url,headers={"authorization":"Basic Ymlhb2JlaTpiaWFvYmVpMTIz"}).content
        access_token = json.loads(content)["data"]["access_token"]
        return access_token

    # 若有保存登录信息，则直接登录，无须扫码
    if os.path.exists(API_CONFIG_PATH):
        with open(API_CONFIG_PATH,"rb") as f:
            data = json.loads(f.read())
            userId = data["userId"]; openId = data["openId"]
        return (get_token(openId,userId),userId)

    # 显示二维码登录
    print("请微信扫描二维码登录 (语音合成标贝悦读https://yuedu.data-baker.com/)")
    img=Image.open(BytesIO(requests.get(code_url+ticket).content))
    img.show()
    time.sleep(0.5)

    # 循环检测登录
    while True:
        result = json.loads(requests.get(result_url+ticket).content)
        if result["code"] == 0:
            for proc in psutil.process_iter():
                if proc.name() == "Microsoft.Photos.exe":
                    proc.kill()
            break
        time.sleep(0.5)
    
    # 获取token
    userId = result["data"]["userId"]
    openId = result["data"]["openId"]
    access_token = get_token(openId,userId)

    # 保存openId和userId用于第二次登录
    with open(API_CONFIG_PATH,"wb+") as f:
        f.write(json.dumps({"userId":userId,"openId":openId}).encode())

    return (access_token,userId)


@print_runtime
def get_tts_audio(text):
    access_token,userId = login()
    audio_url = decrypt_url(request_tts(text,access_token,userId))
    audio_url = audio_url[:audio_url.find("%3D")+3] # 删除解码时多余的字符串
    with open(TTS_MP3_PATH,"wb+") as f:
        f.write(requests.get(audio_url).content)
    return TTS_MP3_PATH