import requests
import json

def get(uid):
    api = f"http://SERVERIP:PORT/api?cmd=1009&uid={uid}"
    try:
        response = requests.get(api)
        data = response.text
        json_data = json.loads(data)
        if json_data["data"] != "null":
            avatar_combat_force = json_data['data']['avatar_combat_force']
            max_key = max(avatar_combat_force, key=avatar_combat_force.get)
            max_value = float(avatar_combat_force[max_key])
            return [int(max_value), max_key, 0]
        else:
            return ["目标玩家不在线或不存在", 0]
    except Exception as e:
        return [f"失败 错误码{e}", "",1]