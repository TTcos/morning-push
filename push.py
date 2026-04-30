#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import random
from datetime import datetime

# ======================== 1. 家人车辆配置（限行判断）========================
family_cars = [
    {"name": "果果姥爷", "last_digit": "6"},   # 车牌尾号 6
    {"name": "果果爸爸",     "last_digit": "8"},   # 车牌尾号 8
    {"name": "果果妈妈",     "last_digit": "7"},   # 车牌尾号 7
    {"name": "果果奶奶",     "last_digit": "0"},   # 车牌尾号 0
    # 可继续添加，格式如上
]

# ======================== 2. 天气（和风天气）========================
# 在 push.py 中找到 get_weather 函数，替换为下面内容，关键调试部分已添加注释
def get_weather():
    WEATHER_KEY = os.environ.get('WEATHER_API_KEY')
    if not WEATHER_KEY:
        # 如果密钥没设置，会在日志中打印警告
        print("⚠️ [Debug] WEATHER_API_KEY was not found in environment variables.")
        return "晴，20℃ 🌞（天气密钥缺失）"

    # 使用和风天气免费开发版推荐的 devapi 域名[reference:1]
    url = f"https://devapi.qweather.com/v7/weather/now?location=101030100&key={WEATHER_KEY}"

    try:
        # 发起 HTTP 请求
        resp = requests.get(url, timeout=10)
        # 在这里新增一行打印，把原始响应的文本打印到日志中
        print(f"🔍 [Debug] Weather API Raw Response: {resp.text}")
        data = resp.json()
        code = data.get('code')

        # 和风天气API返回code为200表示成功，如果是其他值，打印错误详情[reference:2]
        if code == '200':
            now = data.get('now', {})
            temp = now.get('temp', '?')
            text = now.get('text', '晴')
            # 成功时也打印一条日志，方便确认API调用正常
            print(f"✅ [Debug] Weather API succeeded. Temp: {temp}, Text: {text}")
            return f"{text}，{temp}℃ 🌞"
        else:
            # 这是关键：打印出API返回的错误码和原因，我们可以根据这个来判断[reference:3]
            print(f"⚠️ [Debug] Weather API Error. Code: {code}, Message: {data.get('message', 'No message')}")
    except Exception as e:
        # 如果请求过程中出现异常（如网络问题），打印异常信息
        print(f"❌ [Debug] Weather API Request Exception: {e}")

    # 所有失败情况都返回兜底数据
    return "晴，20℃ 🌞（天气服务暂不可用）"

# ======================== 3. 限行（极速数据 API + 家人匹配）========================
# 在 push.py 中找到 get_traffic 函数，替换为下面内容
def get_traffic():
    API_KEY = os.environ.get('TRAFFIC_API_KEY')
    if not API_KEY:
        print("⚠️ [Debug] TRAFFIC_API_KEY was not found in environment variables.")
        return "今日限行：5和0，果果姥爷限号（API密钥缺失）"

    url = 'https://jisuapivehiclelimit.api.bdymkt.com/vehiclelimit/query'
    headers = {'X-APISpace-Token': API_KEY, 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'city': 'tianjin', 'date': datetime.now().strftime('%Y-%m-%d')}

    try:
        resp = requests.post(url, headers=headers, data=data, timeout=10)
        # 关键操作：打印出服务器返回的HTTP状态码和原始响应，这是最有力的排查依据
        print(f"🔍 [Debug] Traffic API HTTP Status: {resp.status_code}")
        print(f"🔍 [Debug] Traffic API Response Body: {resp.text}")

        # 如果HTTP状态码不是200（成功），则直接返回错误，不再解析JSON
        if resp.status_code != 200:
            # 如果状态码是403，很可能是API调用额度已用完[reference:5]
            if resp.status_code == 403:
                print("⚠️ [Debug] Traffic API returned 403. Likely daily usage limit exceeded.")
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
            print(f"⚠️ [Debug] Traffic API returned but no 'result' field: {resp.text}")
    except Exception as e:
        print(f"❌ [Debug] Traffic API Request Exception: {e}")

    return "今日限行：5和0，果果姥爷限号（API暂不可用）"

# ======================== 4. 果果辅食推荐 ========================
# ======================== 果果辅食推荐（两个独立库，扩大规模） ========================
# 辅食一库：高铁米粉、谷物、蛋、肉泥等基础辅食
infant_food_pool1 = [
    "高铁米粉+胡萝卜泥", "高铁米粉+菠菜泥", "高铁米粉+南瓜泥", "高铁米粉+山药泥",
    "蛋黄泥", "土豆泥", "南瓜泥", "山药泥", "紫薯泥",
    "牛肉泥", "猪肝泥", "鸡肉泥", "鳕鱼泥", "三文鱼泥",
    "豆腐泥", "燕麦米粉+苹果泥", "小米糊", "大米糊"
]

# 辅食二库：各种蔬菜泥、水果泥、混合泥
infant_food_pool2 = [
    "西兰花泥", "花菜泥", "菠菜泥", "生菜泥", "油菜泥",
    "苹果泥", "香蕉泥", "牛油果泥", "梨泥", "桃子泥",
    "红枣泥", "豌豆泥", "玉米泥", "胡萝卜泥", "西葫芦泥",
    "蓝莓泥", "草莓泥", "火龙果泥", "猕猴桃泥"
]

def get_baby_food():
    # 从两个库中各随机选一种（不重复保证多样性）
    food1 = random.choice(infant_food_pool1)
    food2 = random.choice(infant_food_pool2)
    return f"辅食一：{food1}\n辅食二：{food2}"

# ======================== 5. 成人饮食推荐 ========================
# 早餐选项（扩大）
staple_opts = ["纯牛奶", "无糖酸奶", "豆浆", "杏仁奶", "燕麦奶", "黑芝麻糊"]
protein_opts = ["煮鸡蛋", "蒸蛋羹", "荷包蛋", "水煮蛋", "茶叶蛋", "蛋白粉奶昔"]
carb_opts = ["蒸红薯", "玉米", "燕麦粥", "小米粥", "全麦面包", "紫米糕", "荞麦馒头", "南瓜发糕"]
veg_opts = ["凉拌黄瓜", "小番茄", "生菜沙拉", "白灼西兰花", "水煮胡萝卜片", "凉拌木耳"]

def get_breakfast():
    return f"{random.choice(staple_opts)} + {random.choice(protein_opts)} + {random.choice(carb_opts)} + {random.choice(veg_opts)}"

# 午餐选项（扩大）
lunch_staple = ["杂粮饭", "糙米饭", "荞麦面", "全麦意面", "藜麦饭", "玉米碴饭", "紫米饭"]
lunch_protein = ["清蒸鲈鱼", "鸡胸肉炒时蔬", "瘦肉炖豆腐", "番茄炒蛋", "白灼虾",
                 "香煎鸡腿肉", "卤牛肉", "清蒸龙利鱼", "蒜蓉扇贝", "素炒豆干"]
lunch_veg = ["蒜蓉空心菜", "清炒西兰花", "蘑菇炒青菜", "凉拌菠菜", "蚝油生菜",
             "蒜蓉娃娃菜", "醋溜白菜", "炝炒圆白菜", "西芹百合"]

def get_lunch():
    return f"{random.choice(lunch_staple)} + {random.choice(lunch_protein)} + {random.choice(lunch_veg)}"

# 晚餐选项（扩大）
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
# 找到 main() 函数，在构建好 message 变量后，推送前，确保有下面这行打印命令
def main():
    # ... 获取天气、限行、辅食等数据的代码 ...

    # 组合最终的消息内容
    message = f"""🌞 早安！美好的一天又开始了(*≧ω≦)！
☁️ 今日天气：{weather}
...

📅 今日待办提醒
{todo_text}"""

    # 在推送前，将完整消息打印到日志中
    print(message)
    send_to_wecom(message)