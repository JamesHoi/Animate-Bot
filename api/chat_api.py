import requests
import json
from api.debug import print_runtime

CHAT_API_URL = "https://api.qingyunke.com/api.php?key=free&appid=0&msg="
CHARACTER_NAME = "小黑"


@print_runtime
def get_chat_ans(msg):
    msg = msg.replace(CHARACTER_NAME, "菲菲")
    result = json.loads(requests.get(CHAT_API_URL+msg).content)["content"]
    return result.replace("菲菲",CHARACTER_NAME)