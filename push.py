#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import random
from datetime import datetime

# ======================== 1. 家人车辆配置（限行判断）========================
family_cars = [
    {"name": "果果姥爷", "last_digit": "6"},
    {"name": "果果爸爸", "last_digit": "8"},
    {"name": "果果妈妈", "last_digit": "7"},
    {"name": "果果奶奶", "last_digit": "0"},
]

# ======================== 2. 天气（和风天气）========================
def get_weather():
    WEATHER_KEY = os.environ.get('WEATHER_API_KEY')
    API_HOST = os.environ.get('QWEATHER_API_HOST')   # 新增：读取专属 API Host

    if not WEATHER_KEY:
        print("⚠️ [Debug] WEATHER_API_KEY was not found.")
        return "晴，20℃ 🌞（天气密钥缺失）"
    if not API_HOST:
        print("⚠️ [Debug] QWEATHER_API_HOST was not found.")
        return "晴，20℃ 🌞（API Host缺失）"

    # 注意：API_HOST 本身不要包含 https:// 前缀，代码会自动加上
    url = f"https://{API_HOST}/v7/weather/now?location=101030100&key={WEATHER_KEY}"
    try:
        resp = requests.get(url, timeout=10)
        print(f"🔍 [Debug] Weather API Raw Response: {resp.text}")
        data = resp.json()
        code = data.get('code')
        if code == '200':
            now = data.get('now', {})
            temp = now.get('temp', '?')
            text = now.get('text', '晴')
            print(f"✅ [Debug] Weather succeeded. Temp: {temp}, Text: {text}")
            return f"{text}，{temp}℃ 🌞"
        else:
            print(f"⚠️ [Debug] Weather API Error. Code: {code}, Msg: {data.get('message', '')}")
    except Exception as e:
        print(f"❌ [Debug] Weather API Exception: {e}")

    return "晴，20℃ 🌞（天气服务暂不可用）"

# ======================== 3. 限行（极速数据）========================
def get_traffic():
    API_KEY = os.environ.get('TRAFFIC_API_KEY')
    if not API_KEY:
        print("⚠️ [Debug] TRAFFIC_API_KEY not found.")
        return "今日限行：5和0，果果姥爷限号（API密钥缺失）"

    url = 'https://jisuapivehiclelimit.api.bdymkt.com/vehiclelimit/query'
    headers = {'X-APISpace-Token': API_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'city': 'tianjin', 'date': datetime.now().strftime('%Y-%m-%d')}
    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        print(f"🔍 [Debug] Traffic API HTTP Status: {resp.status_code}")
        print(f"🔍 [Debug] Traffic API Response Body: {resp.text}")
        if resp.status_code != 200:
            if resp.status_code == 403:
                print("⚠️ [Debug] Traffic API returned 403. Likely usage limit exceeded.")
            return f"今日限行：5和0，果果姥爷限号（HTTP {resp.status_code}）"
        result = resp.json().get('result', {})
        if result:
            limit_num = result.get('limitNumbers', '')
            if limit_num:
                print(f"✅ [Debug] Traffic API succeeded. Limit: {limit_num}")
                return f"今日限行：{limit_num}，果果姥爷限号"
            else:
                print("✅ [Debug] Traffic API succeeded, no limit today.")
                return "今日不限行，果果姥爷畅行"
        else:
            print(f"⚠️ [Debug] Traffic API no 'result' field: {resp.text}")
    except Exception as e:
        print(f"❌ [Debug] Traffic API Exception: {e}")
    return "今日限行：5和0，果果姥爷限号（API暂不可用）"

# ======================== 4. 果果辅食推荐 ========================
infant_food_pool1 = [
    "高铁米粉+胡萝卜泥", "高铁米粉+菠菜泥", "高铁米粉+南瓜泥", "高铁米粉+山药泥",
    "蛋黄泥", "土豆泥", "南瓜泥", "山药泥", "紫薯泥",
    "牛肉泥", "猪肝泥", "鸡肉泥", "鳕鱼泥", "三文鱼泥",
    "豆腐泥", "燕麦米粉+苹果泥", "小米糊", "大米糊"
]
infant_food_pool2 = [
    "西兰花泥", "花菜泥", "菠菜泥", "生菜泥", "油菜泥",
    "苹果泥", "香蕉泥", "牛油果泥", "梨泥", "桃子泥",
    "红枣泥", "豌豆泥", "玉米泥", "胡萝卜泥", "西葫芦泥",
    "蓝莓泥", "草莓泥", "火龙果泥", "猕猴桃泥"
]
def get_baby_food():
    food1 = random.choice(infant_food_pool1)
    food2 = random.choice(infant_food_pool2)
    return f"辅食一：{food1}\n辅食二：{food2}"

# ======================== 5. 成人饮食推荐 ========================
staple_opts = ["纯牛奶", "无糖酸奶", "豆浆", "杏仁奶", "燕麦奶", "黑芝麻糊"]
protein_opts = ["煮鸡蛋", "蒸蛋羹", "荷包蛋", "水煮蛋", "茶叶蛋", "蛋白粉奶昔"]
carb_opts = ["蒸红薯", "玉米", "燕麦粥", "小米粥", "全麦面包", "紫米糕", "荞麦馒头", "南瓜发糕"]
veg_opts = ["凉拌黄瓜", "小番茄", "生菜沙拉", "白灼西兰花", "水煮胡萝卜片", "凉拌木耳"]
def get_breakfast():
    return f"{random.choice(staple_opts)} + {random.choice(protein_opts)} + {random.choice(carb_opts)} + {random.choice(veg_opts)}"

lunch_staple = ["杂粮饭", "糙米饭", "荞麦面", "全麦意面", "藜麦饭", "玉米碴饭", "紫米饭"]
lunch_protein = ["清蒸鲈鱼", "鸡胸肉炒时蔬", "瘦肉炖豆腐", "番茄炒蛋", "白灼虾",
                 "香煎鸡腿肉", "卤牛肉", "清蒸龙利鱼", "蒜蓉扇贝", "素炒豆干"]
lunch_veg = ["蒜蓉空心菜", "清炒西兰花", "蘑菇炒青菜", "凉拌菠菜", "蚝油生菜",
             "蒜蓉娃娃菜", "醋溜白菜", "炝炒圆白菜", "西芹百合"]
def get_lunch():
    return f"{random.choice(lunch_staple)} + {random.choice(lunch_protein)} + {random.choice(lunch_veg)}"

dinner_staple = ["小米南瓜粥", "山药粥", "燕麦牛奶", "紫薯粥", "红豆薏米粥", "银耳莲子羹"]
dinner_protein = ["豆腐炒木耳", "清蒸龙利鱼", "虾仁蒸蛋", "香菇鸡肉", "芹菜炒香干",
                  "番茄煮鱼片", "蛋饺汤", "清炒豆皮"]
dinner_veg = ["白灼生菜", "蒜蓉西兰花", "清炒娃娃菜", "上汤苋菜", "清炒油麦菜", "蒜蓉空心菜"]
def get_dinner():
    return f"{random.choice(dinner_staple)} + {random.choice(dinner_protein)} + {random.choice(dinner_veg)}"

# ======================== 6. 待办事项 ========================
def get_today_todos():
    todo_file = 'todo.json'
    if not os.path.exists(todo_file):
        return []
    with open(todo_file, 'r', encoding='utf-8') as f:
        todos = json.load(f)
    today = datetime.now().strftime('%Y-%m-%d')
    today_todos = [t for t in todos if t.get('date') == today and not t.get('done', False)]
    today_todos.sort(key=lambda x: x.get('time', '00:00'))
    return today_todos

# ======================== 7. 发送企业微信 ========================
def send_to_wecom(message):
    webhook = os.environ.get('WECHAT_WEBHOOK')
    if not webhook:
        print("Error: WECHAT_WEBHOOK not set")
        return
    payload = {"msgtype": "text", "text": {"content": message}}
    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        if resp.status_code == 200:
            print("推送成功")
        else:
            print(f"推送失败，状态码：{resp.status_code}")
    except Exception as e:
        print(f"发送异常：{e}")

# ======================== 8. 主函数 ========================
def main():
    weather = get_weather()
    traffic = get_traffic()
    baby_food = get_baby_food()
    breakfast = get_breakfast()
    lunch = get_lunch()
    dinner = get_dinner()
    todos = get_today_todos()

    if todos:
        todo_lines = [f"⏰ {t['time']} - {t['content']}" for t in todos]
        todo_text = "\n".join(todo_lines)
    else:
        todo_text = "今日无待办，放松一下~"

    message = f"""🌞 早安！美好的一天又开始了(*≧ω≦)！
☁️ 今日天气：{weather}
🚗 {traffic}

👶🏻今日果果辅食推荐
{baby_food}

📅 今日成人饮食推荐
🥣 早餐：{breakfast}
🍱 午餐：{lunch}
🥗 晚餐：{dinner}

📅 今日待办提醒
{todo_text}"""
    print(message)
    send_to_wecom(message)

if __name__ == "__main__":
    main()