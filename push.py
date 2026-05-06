#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import os
import random
from datetime import datetime

# 宝宝出生日期（年,月,日）—— 请修改为你家宝宝的实际生日
BIRTH_DATE = datetime(2025, 12, 10)   # 示例：2025年12月10日

# 倒计时配置：列表内每个元素为 (目标日期, 事件描述)
COUNTDOWNS = [
    (datetime(2026, 6, 10), "带果果打疫苗"),
    (datetime(2026, 8, 29), "注册会计师考试"),
    (datetime(2026, 9, 15), "法律职业资格考试"),
    # 可以继续添加
]

# ======================== 1. 家人车辆配置（限行判断）========================
family_cars = [
    {"name": "果果姥爷", "last_digit": "6"},
    {"name": "果果爸爸", "last_digit": "8"},
    {"name": "果果妈妈", "last_digit": "7"},
    {"name": "果果奶奶", "last_digit": "0"},
]

# ======================== 2. 天气（和风天气，简化版）========================

def get_daily_forecast(location, key, host):
    """获取未来3天天气预报，提取当天最高和最低温度"""
    url = f"https://{host}/v7/weather/3d?location={location}&key={key}"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        if data.get('code') == '200':
            forecasts = data.get('daily', [])
            if forecasts:
                today = forecasts[0]
                temp_max = today.get('tempMax', 'N/A')
                temp_min = today.get('tempMin', 'N/A')
                text_day = today.get('textDay', '')
                return text_day, temp_min, temp_max
    except Exception as e:
        print(f"天气预报API异常: {e}")
    return None, None, None

def get_clothing_advice(temp_min, temp_max):
    """根据温度推荐穿着"""
    try:
        avg_temp = (float(temp_min) + float(temp_max)) / 2
    except:
        return "注意天气变化"
    if avg_temp < 5:
        return "羽绒服、厚棉衣"
    elif avg_temp < 10:
        return "大衣、薄羽绒服"
    elif avg_temp < 15:
        return "风衣、毛衣"
    elif avg_temp < 20:
        return "夹克、薄外套"
    elif avg_temp < 25:
        return "长袖T恤、薄开衫"
    elif avg_temp < 30:
        return "短袖、连衣裙"
    else:
        return "短袖、防晒衣"

def get_weather():
    WEATHER_KEY = os.environ.get('WEATHER_API_KEY')
    API_HOST = os.environ.get('QWEATHER_API_HOST')
    if not WEATHER_KEY or not API_HOST:
        return "天气数据获取失败（密钥或Host缺失）"

    location = "101030100"  # 天津

    # 1. 获取当天天气预报（最高最低温、天气现象）
    text_day, temp_min, temp_max = get_daily_forecast(location, WEATHER_KEY, API_HOST)
    if text_day is None:
        # 降级：只获取实时天气
        url = f"https://{API_HOST}/v7/weather/now?location={location}&key={WEATHER_KEY}"
        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()
            if data.get('code') == '200':
                now = data.get('now', {})
                temp = now.get('temp', '?')
                text = now.get('text', '晴')
                weather_base = f"{text}，{temp}℃"
                temp_min = temp_max = temp
            else:
                weather_base = "天气数据暂不可用"
                temp_min = temp_max = 'N/A'
        except:
            weather_base = "天气数据获取失败"
            temp_min = temp_max = 'N/A'
    else:
        weather_base = f"{text_day}，{temp_min}-{temp_max}℃"

    # 2. 穿衣推荐
    if temp_min != 'N/A' and temp_max != 'N/A':
        clothing = get_clothing_advice(temp_min, temp_max)
        clothing_text = f"，推荐穿着{clothing}"
    else:
        clothing_text = ""

    # 组装最终消息（不包含空气质量、紫外线）
    return weather_base + clothing_text

# ======================== 3. 限行（自动轮换 + 节假日/调休）========================
holidays_2026 = [
    "2026-01-01",  # 元旦
    "2026-02-15", "2026-02-16", "2026-02-17", "2026-02-18", "2026-02-19",  # 春节
    "2026-04-05", "2026-04-06",  # 清明节
    "2026-05-01", "2026-05-04", "2026-05-05",  # 劳动节
    "2026-06-19", "2026-06-22",  # 端午节
    "2026-09-25", "2026-09-28",  # 中秋节
    "2026-10-01", "2026-10-02", "2026-10-05", "2026-10-06", "2026-10-07",  # 国庆节
]
workdays_2026 = [
    "2026-02-14",  # 周六，春节调休
    "2026-04-04",  # 周六，清明调休
    "2026-05-03",  # 周日，劳动节调休
    "2026-09-24",  # 周六，中秋调休
    "2026-10-10",  # 周六，国庆调休
]

holidays_by_year = {2026: holidays_2026}
workdays_by_year = {2026: workdays_2026}

def is_holiday(date_obj):
    y = date_obj.year
    if y not in holidays_by_year:
        return False
    return date_obj.strftime("%Y-%m-%d") in holidays_by_year[y]

def is_special_workday(date_obj):
    y = date_obj.year
    if y not in workdays_by_year:
        return False
    return date_obj.strftime("%Y-%m-%d") in workdays_by_year[y]

def get_traffic():
    from datetime import datetime, timedelta

    today = datetime.now().date()

    if is_holiday(today):
        return "今日不限行（法定节假日），祝您节日愉快！"

    if today.weekday() >= 5:
        if is_special_workday(today):
            pass
        else:
            return "今日不限行，周末愉快！"

    base_date = datetime(2026, 3, 30).date()
    delta_days = (today - base_date).days
    if delta_days < 0:
        return "今日限行：5和0（规则暂未制定）"

    cycle_index = delta_days // 91
    shift = cycle_index % 5

    combinations = [
        ("2和7", "3和8", "4和9", "5和0", "1和6"),
        ("1和6", "2和7", "3和8", "4和9", "5和0"),
        ("5和0", "1和6", "2和7", "3和8", "4和9"),
        ("4和9", "5和0", "1和6", "2和7", "3和8"),
        ("3和8", "4和9", "5和0", "1和6", "2和7"),
    ]

    weekday_idx = today.weekday()
    limit_num = combinations[shift][weekday_idx]

    limited_digits = limit_num.split('和')
    restricted = [car['name'] for car in family_cars if car['last_digit'] in limited_digits]
    if restricted:
        names = '、'.join(restricted)
        suffix = f"，{names}今天限号"
    else:
        suffix = "，大家都不限号"
    return f"今日限行：{limit_num}{suffix}"

# ---------- 4. 宝宝年龄 ----------
def get_baby_age_display():
    today = datetime.now().date()
    birth = BIRTH_DATE.date()
    delta = (today - birth).days
    if delta < 0:
        return "果果还未出生🎈"
    months = delta // 30
    days = delta % 30
    if days == 0:
        return f"果果今天{months}个月啦🎉"
    else:
        return f"果果今天{months}个月零{days}天"

# ---------- 5. 倒计时 ----------
def get_countdown():
    today = datetime.now().date()
    lines = []
    for target_date, event in COUNTDOWNS:
        target = target_date.date()
        delta = (target - today).days
        if delta > 0:
            lines.append(f"📌距离{event}还有{delta}天")
        elif delta == 0:
            lines.append(f"今天是{event}！🎉")
        else:
            lines.append(f"✅{event}已过去{-delta}天")
    return "\n".join(lines)   # 返回多行文本

# ======================== 6. 果果辅食推荐 ========================
infant_food_pool1 = [
    "高铁米粉","高铁米粉","高铁米粉 + 苹果泥","高铁米粉 + 蛋黄泥(1/4)","高铁米粉 + 梨泥","高铁米粉 + 香蕉泥","高铁米粉 + 牛油果泥",
]
infant_food_pool2 = [
    "胡萝卜泥", "南瓜泥", "土豆泥", "西蓝花泥", "胡萝卜泥",
    "南瓜泥", "土豆泥",
]
def get_baby_food():
    food1 = random.choice(infant_food_pool1)
    food2 = random.choice(infant_food_pool2)
    return f"辅食一：{food1}\n辅食二：{food2}"

# ======================== 7. 成人饮食推荐 ========================
staple_opts = ["纯牛奶", "无糖酸奶", "无糖豆浆", "红枣豆浆", "燕麦奶", "黑芝麻糊"]
protein_opts = ["煮鸡蛋", "蒸蛋羹", "荷包蛋", "水煮蛋", "茶叶蛋", "豆腐脑（少卤）","鸡蛋饼"]
carb_opts = ["蒸红薯", "玉米", "燕麦粥", "小米粥", "全麦面包", "紫米糕", "荞麦馒头", "红豆包(少糖)","全麦卷饼", "山药粥", "南瓜发糕","煎饼果子(不包油条、果篦儿)"]
veg_opts = ["凉拌黄瓜", "小番茄", "生菜沙拉", "白灼西兰花", "水煮胡萝卜片", "凉拌木耳"]
def get_breakfast():
    return f"{random.choice(staple_opts)} + {random.choice(protein_opts)} + {random.choice(carb_opts)} + {random.choice(veg_opts)}"

lunch_staple = [ "杂粮饭", "糙米饭", "荞麦面", "藜麦饭", "玉米碴饭", "紫米饭", "二米饭",
    "燕麦饭", "小米饭", "黑米饭", "红豆饭", "薏米饭", "全麦意面", "土豆泥(无黄油)",
    "南瓜饭", "红薯饭", "山药饭", "高粱米饭", "大麦饭", "青稞饭", "荞麦饭",
    "全麦馒头", "玉米饼", "杂粮窝头", "蒸红薯", "蒸玉米", "蒸山药"]
lunch_protein = ["清蒸鲈鱼", "鸡胸肉炒时蔬", "瘦肉炖豆腐", "番茄炒蛋", "白灼虾",
    "香煎鸡腿肉(去皮)", "卤牛肉(去脂)", "清蒸龙利鱼", "蒜蓉扇贝", "素炒豆干",
    "豆腐酿肉", "虾仁滑蛋", "清蒸鳕鱼", "小炒黄牛肉", "彩椒炒鸡丁",
    "蒜蓉蒸虾", "香菇蒸鸡", "鲫鱼豆腐汤(少油)", "蛤蜊蒸蛋", "清蒸多宝鱼",
    "洋葱炒牛肉", "芦笋炒虾仁", "彩椒炒鱿鱼", "豆腐蒸蛋", "香煎三文鱼",
    "鸡肉丸子", "蒸肉饼(瘦肉)", "清炖狮子头(瘦肉)", "番茄炖牛肉", "蒜香排骨(少油)",
    "葱姜炒蛤蜊", "清蒸黄花鱼", "盐水虾", "香干炒肉丝", "鸡蛋炒苦瓜"]
lunch_veg = ["蒜蓉空心菜", "清炒西兰花", "蘑菇炒青菜", "凉拌菠菜", "蚝油生菜",
    "蒜蓉娃娃菜", "醋溜白菜", "炝炒圆白菜", "西芹百合", "清炒苦瓜",
    "上汤娃娃菜", "白灼芥兰", "蒜蓉秋葵", "清炒红苋菜", "干煸四季豆(少油)",
    "清炒丝瓜", "番茄菜花", "荷塘小炒(藕片、木耳、荷兰豆)", "蒜蓉西葫芦", "清炒豌豆苗",
    "蒜蓉蒿子秆", "蚝油杏鲍菇", "白灼菜心", "清炒莴笋", "蒜蓉油麦菜",
    "凉拌黄瓜", "家常豆腐", "西红柿炒圆白菜", "蒜蓉茼蒿", "清炒萝卜丝",
    "香菇油菜", "清炒豆芽", "蒜蓉空心菜", "蒜蓉木耳菜", "白灼秋葵",
    "凉拌海带丝", "蒜蓉蒸茄子", "清炒苋菜"]
def get_lunch():
    return f"{random.choice(lunch_staple)} + {random.choice(lunch_protein)} + {random.choice(lunch_veg)}"

dinner_staple = ["小米南瓜粥", "山药粥", "燕麦牛奶", "紫薯粥", "红豆薏米粥", "银耳莲子羹",
    "玉米糊", "荞麦粥", "黑米粥", "绿豆粥(夏季)", "红薯粥", "南瓜小米羹",
    "百合粥", "莲子粥", "杂粮粥", "小米红薯粥", "玉米碴粥", "燕麦片粥",
    "蔬菜粥", "皮蛋瘦肉粥(少盐)", "鱼片粥", "鸡丝粥", "豆腐脑(少卤)"]
dinner_protein = [ "豆腐炒木耳", "清蒸龙利鱼", "虾仁蒸蛋", "香菇鸡肉", "芹菜炒香干",
    "番茄煮鱼片", "蛋饺汤", "清炒豆皮", "冬瓜丸子汤", "鲫鱼豆腐汤(少油)",
    "蛏子蒸蛋", "鸡胸肉丸汤", "清蒸桂花鱼", "虾滑紫菜汤", "豆腐虾仁煲",
    "蒜蓉蒸虾", "鸡肉豆腐丸子", "番茄豆腐汤", "清蒸带鱼", "瘦肉冬瓜汤",
    "蛤蜊豆腐汤", "水煮鱼片(少油)", "鸡丝豆腐脑", "蒸鸡腿", "白灼虾(少量)",
    "清汤牛肉丸", "紫菜蛋花汤", "青菜豆腐汤", "丝瓜鸡蛋汤", "蘑菇蛋花汤"]
dinner_veg = ["白灼生菜", "蒜蓉西兰花", "清炒娃娃菜", "上汤苋菜", "清炒油麦菜",
    "蒜蓉空心菜", "凉拌黄瓜", "清炒苦瓜", "蒜蓉丝瓜", "清炒茼蒿",
    "蚝油杏鲍菇", "白灼芥兰", "清炒荷兰豆", "蒜蓉生菜", "清炒莴笋",
    "蒜蓉木耳菜", "清炒苋菜", "凉拌海带丝", "蒜蓉蒸茄子", "蒜蓉油菜",
    "清炒豆苗", "番茄炒圆白菜", "清炒胡萝卜丝", "香菇青菜", "白灼菜心",
    "清炒萝卜苗", "蒜蓉芦笋", "清炒西葫芦", "蒜蓉豇豆", "清炒佛手瓜",
    "时令蔬菜"]
def get_dinner():
    return f"{random.choice(dinner_staple)} + {random.choice(dinner_protein)} + {random.choice(dinner_veg)}"

# ======================== 8. 待办事项 ========================
def get_today_todos():
    todo_file = 'todo.json'
    if not os.path.exists(todo_file):
        return []
    with open(todo_file, 'r', encoding='utf-8') as f:
        todos = json.load(f)

    today = datetime.now()
    today_str = today.strftime('%Y-%m-%d')
    today_day = today.day
    today_weekday = today.weekday()

    today_todos = []
    for t in todos:
        if t.get('done', False):
            continue
        t_date = t.get('date', '')
        if t_date == today_str:
            today_todos.append(t)
        elif t_date == "everyday":
            today_todos.append(t)
        elif t_date.startswith("monthly:"):
            try:
                target_day = int(t_date.split(':')[1])
                if target_day == today_day:
                    today_todos.append(t)
            except:
                pass
        elif t_date.startswith("weekly:"):
            try:
                target_weekday = int(t_date.split(':')[1])
                if target_weekday == today_weekday:
                    today_todos.append(t)
            except:
                pass

    today_todos.sort(key=lambda x: x.get('time', '00:00'))
    return today_todos

# ======================== 9. 发送企业微信 ========================
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

# ======================== 10. 主函数 ========================
def main():
    weather = get_weather()
    traffic = get_traffic()
    baby_age = get_baby_age_display()
    countdown_msg = get_countdown()
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
👶🏻 {baby_age}
📅 {countdown_msg}

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