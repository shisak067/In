# utils/helpers.py
import random
import string
import time
import psutil
import platform
from datetime import datetime, date
from typing import Dict, Any, Tuple, Optional, List
from config import OWNER_IDS, BOT_NAME, BOT_VERSION, BOT_START_TIME, DEVELOPER_USERNAME

# Global variables
settings = {}
api_settings = {}
MAINTENANCE_MODE = False
user_last_result = {}

def load_settings(mongo):
    global settings, api_settings, MAINTENANCE_MODE
    settings = {
        "bot_active": mongo.get_setting("bot_active", True),
        "referral_coins": mongo.get_setting("referral_coins", 10),
        "daily_limit": mongo.get_setting("daily_limit", 15)
    }
    MAINTENANCE_MODE = mongo.get_setting("maintenance_mode", False)
    api_settings = {"apis": {}}
    from config import DEFAULT_APIS
    for key in DEFAULT_APIS.keys():
        api_data = mongo.get_api_setting(key)
        if api_data:
            api_settings["apis"][key] = api_data
        else:
            api_settings["apis"][key] = {"enabled": True, "url": DEFAULT_APIS[key]}
            mongo.save_api_setting(key, api_settings["apis"][key])

def toggle_maintenance_mode(mongo):
    global MAINTENANCE_MODE
    MAINTENANCE_MODE = not MAINTENANCE_MODE
    mongo.save_setting("maintenance_mode", MAINTENANCE_MODE)
    return MAINTENANCE_MODE

def is_maintenance_mode():
    return MAINTENANCE_MODE

def get_user(mongo, user_id):
    user = mongo.get_user(user_id)
    if not user:
        user = {
            "user_id": user_id,
            "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "username": None,
            "coins": 0,
            "total_searches": 0,
            "daily_searches": 0,
            "last_search_date": date.today().isoformat(),
            "referral_code": f"{user_id}_{''.join(random.choices(string.ascii_uppercase + string.digits, k=6))}",
            "referred_by": None,
            "referrals": [],
            "is_admin": False,
            "redeemed_keys": [],
            "is_blocked": False,
            "blocked_reason": None,
            "blocked_at": None
        }
        mongo.save_user(user)
    return user

def is_admin(user_id):
    if user_id in OWNER_IDS:
        return True
    return False  # We'll implement admin check from DB later

def is_owner(user_id):
    return user_id in OWNER_IDS

def has_unlimited_coins(user_id):
    return is_admin(user_id)

def add_coins(mongo, user_id, amount):
    user = get_user(mongo, user_id)
    user["coins"] += amount
    mongo.save_user(user)

def use_coin(mongo, user_id):
    if has_unlimited_coins(user_id):
        return True
    user = get_user(mongo, user_id)
    if user["coins"] > 0:
        user["coins"] -= 1
        mongo.save_user(user)
        return True
    return False

def can_search(mongo, user_id):
    global settings
    if is_admin(user_id):
        return True, 999999, False
    user = get_user(mongo, user_id)
    today = date.today().isoformat()
    if user["last_search_date"] != today:
        user["daily_searches"] = 0
        user["last_search_date"] = today
        mongo.save_user(user)
    remaining = settings["daily_limit"] - user["daily_searches"]
    if remaining > 0:
        return True, remaining, False
    elif user["coins"] > 0:
        return True, 0, True
    else:
        return False, 0, False

def generate_keys(mongo, key_type, count, credits):
    keys = []
    for _ in range(count):
        key_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
        full_key = f"{key_type}_{key_id}" if key_type != "normal" else key_id
        key_data = {
            "key": full_key,
            "key_type": key_type,
            "credits": credits,
            "used_by": None,
            "used_at": None,
            "created_at": datetime.now().isoformat(),
            "is_used": False
        }
        mongo.save_key(full_key, key_data)
        keys.append(full_key)
    return keys

def redeem_key(mongo, user_id, key):
    key_data = mongo.get_key(key)
    if not key_data:
        return False, "❌ Invalid key!"
    if key_data.get("is_used", False):
        return False, f"❌ Key already used!"
    key_data["is_used"] = True
    key_data["used_by"] = user_id
    key_data["used_at"] = datetime.now().isoformat()
    mongo.save_key(key, key_data)
    credits = key_data.get("credits", 0)
    add_coins(mongo, user_id, credits)
    return True, f"✅ Redeemed! +{credits} coins"

def get_bot_uptime():
    uptime_seconds = int(time.time() - BOT_START_TIME)
    days = uptime_seconds // 86400
    hours = (uptime_seconds % 86400) // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    if seconds > 0 or not parts: parts.append(f"{seconds}s")
    return " ".join(parts)

def get_system_info():
    try:
        return {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_used": psutil.virtual_memory().used // (1024**2),
            "memory_total": psutil.virtual_memory().total // (1024**2),
            "platform": platform.system(),
            "platform_release": platform.release(),
            "python_version": platform.python_version()
        }
    except:
        return {"cpu_percent": 0, "memory_percent": 0, "memory_used": 0, "memory_total": 0, 
                "platform": "Unknown", "platform_release": "Unknown", "python_version": "Unknown"}
