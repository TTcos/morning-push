#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import random
from datetime import datetime

# ======================== 1. 家人车辆配置（限行判断）========================
family_cars = [
    {"name": "果果姥爷", "last_digit": "5"},   # 车牌尾号 5
    {"name": "猪猪",     "last_digit": "0"},   # 车牌尾号 0
    # 可继续添加，格式如上
]

# ======================== 2. 天气（和风天气）========================
# 和风天气 API 配置
WEATHER_KEY = os.environ.get('WEATHER_API_KEY')
WEATHER_HOST = os.environ.get('QWEATHER_API_HOST') or 'https://api.qweather.com'   # 如果未设置_HOST就用默认API地址
LOCATION_ID = '101030100'  # 天津的和风天气城市代码

def get_weather():
    # 从环境变量读取 API 密钥（已在 GitHub Secrets 中配置）
    WEATHER_KEY = os.environ.get('WEATHER_API_KEY')
    WEATHER_HOST = os.environ.get('QWEATHER_API_HOST')
    if not WEATHER_KEY:
        return "天气数据获取失败：未配置API密钥"

    # 确保 WEATHER_HOST 以 https:// 开头，拼接实时天气 API 的路径
    if WEATHER_HOST and not WEATHER_HOST.startswith('http'):
        WEATHER_HOST = 'https://' + WEATHER_HOST
    WEATHER_HOST = WEATHER_HOST or "https://devapi.qweather.com"
    url = f"{WEATHER_HOST}/v7/weather/now?location={LOCATION_ID}&key={WEATHER_KEY}"

    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        # 和风天气返回码：'200' 表示成功
        if data.get('code') == '200':
            now = data.get('now', {})
            temp = now.get('temp', '?')
            text = now.get('text', '未知')
            return f"{text}，{temp}℃ 🌞"
        else:
            # 打印错误码，方便排查
            print(f"Weather API error: {data.get('code')} - {data.get('message')}")
    except Exception as e:
        print(f"Weather API request failed: {e}")

    return "晴，20℃ 🌞"   # 兜底数据

# ======================== 3. 限行（极速数据 API + 家人匹配）========================
def get_traffic():
    API_KEY = os.environ.get('TRAFFIC_API_KEY')
    if not API_KEY:
        return "今日限行：5和0，果果姥爷限号（未配置 Traffic Key）"

    url = 'https://jisuapivehiclelimit.api.bdymkt.com/vehiclelimit/query'
    headers = {
        'X-APISpace-Token': API_KEY,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'city': 'tianjin',
        'date': datetime.now().strftime('%Y-%m-%d')
    }

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        result = resp.json().get('result', {})
        if result:
            limit_num = result.get('limitNumbers', '')
            if limit_num:
                # 解析限行尾号，例如 "5和0" → ["5","0"]
                limited_digits = limit_num.split('和')
                # 找出今天限行的家人
                restricted = [car['name'] for car in family_cars if car['last_digit'] in limited_digits]
                if restricted:
                    names = '、'.join(restricted)
                    suffix = f"，{names}今天{'你们' if len(restricted)>1 else '你'}限号"
                else:
                    suffix = "，大家都不限号"
                return f"今日限行：{limit_num}{suffix}"
            else:
                return "今日不限行，果果姥爷畅行"
    except Exception as e:
        print(f"Traffic API error: {e}")

    # 兜底
    return "今日限行：5和0，果果姥爷限号（API暂不可用）"

# ======================== 4. 果果辅食推荐 ========================
infant_foods = [
    "高铁米粉+胡萝卜泥", "西兰花泥", "南瓜泥", "土豆泥", "蛋黄泥",
    "苹果泥", "香蕉泥", "菠菜泥", "山药泥", "牛肉泥", "鳕鱼泥",
    "米粉+菠菜泥", "米粉+南瓜泥", "紫薯泥", "牛油果泥"
]

def get_baby_food():
    selected = random.sample(infant_foods, 2)
    return f"辅食一：{selected[0]}\n辅食二：{selected[1]}"

# ======================== 5. 成人饮食推荐 ========================
breakfast_opts = {
    "staple": ["纯牛奶", "无糖酸奶", "豆浆"],
    "protein": ["煮鸡蛋", "蒸蛋羹"],
    "carb": ["蒸红薯", "玉米", "燕麦粥", "小米粥"],
    "veg": ["凉拌黄瓜", "小番茄", "生菜沙拉"]
}
def get_breakfast():
    return f"{random.choice(breakfast_opts['staple'])} + {random.choice(breakfast_opts['protein'])} + {random.choice(breakfast_opts['carb'])} + {random.choice(breakfast_opts['veg'])}"

lunch_opts = {
    "staple": ["杂粮饭", "糙米饭", "荞麦面"],
    "protein": ["清蒸鲈鱼", "鸡胸肉炒时蔬", "瘦肉炖豆腐", "番茄炒蛋", "白灼虾"],
    "veg": ["蒜蓉空心菜", "清炒西兰花", "蘑菇炒青菜", "凉拌菠菜"]
}
def get_lunch():
    return f"{random.choice(lunch_opts['staple'])} + {random.choice(lunch_opts['protein'])} + {random.choice(lunch_opts['veg'])}"

dinner_opts = {
    "staple": ["小米南瓜粥", "山药粥", "燕麦牛奶"],
    "protein": ["豆腐炒木耳", "清蒸龙利鱼", "虾仁蒸蛋"],
    "veg": ["白灼生菜", "蒜蓉西兰花", "清炒娃娃菜"]
}
def get_dinner():
    return f"{random.choice(dinner_opts['staple'])} + {random.choice(dinner_opts['protein'])} + {random.choice(dinner_opts['veg'])}"

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

    # 待办列表文本
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