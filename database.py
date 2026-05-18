# database.py
import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Tuple, Optional, List
from pymongo import MongoClient

logger = logging.getLogger(__name__)
DATA_DIR = "bot_data"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class MongoDBManager:
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.is_connected = False
        self.connect()
    
    def connect(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client[self.db_name]
            self.is_connected = True
            logger.info("✅ MongoDB connected!")
            return True
        except Exception as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None
            self.db = None
            self.is_connected = False
            return False
    
    def is_available(self):
        if not self.is_connected:
            return False
        try:
            self.client.admin.command('ping')
            return True
        except:
            self.is_connected = False
            return False
    
    def get_collection(self, name):
        if self.is_available() and self.db:
            return self.db[name]
        return None
    
    # User methods
    def save_user(self, user_data):
        collection = self.get_collection("users")
        if collection:
            try:
                collection.update_one({"user_id": user_data["user_id"]}, {"$set": user_data}, upsert=True)
                return True
            except:
                pass
        return self._save_user_file(user_data)
    
    def _save_user_file(self, user_data):
        users_file = f"{DATA_DIR}/users.json"
        try:
            users = {}
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
            users[str(user_data["user_id"])] = user_data
            with open(users_file, 'w') as f:
                json.dump(users, f, indent=2)
            return True
        except:
            return False
    
    def get_user(self, user_id):
        collection = self.get_collection("users")
        if collection:
            try:
                user = collection.find_one({"user_id": user_id})
                if user:
                    user.pop("_id", None)
                    return user
            except:
                pass
        return self._get_user_file(user_id)
    
    def _get_user_file(self, user_id):
        users_file = f"{DATA_DIR}/users.json"
        try:
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
                return users.get(str(user_id))
        except:
            return None
        return None
    
    def get_all_users(self):
        collection = self.get_collection("users")
        if collection:
            try:
                users = list(collection.find({}))
                for u in users:
                    u.pop("_id", None)
                return users
            except:
                pass
        return self._get_all_users_file()
    
    def _get_all_users_file(self):
        users_file = f"{DATA_DIR}/users.json"
        try:
            if os.path.exists(users_file):
                with open(users_file, 'r') as f:
                    users = json.load(f)
                return list(users.values())
        except:
            return []
        return []
    
    # Settings methods
    def save_setting(self, key, value):
        collection = self.get_collection("settings")
        if collection:
            try:
                collection.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)
                return True
            except:
                pass
        return self._save_setting_file(key, value)
    
    def _save_setting_file(self, key, value):
        settings_file = f"{DATA_DIR}/settings.json"
        try:
            settings = {}
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            settings[key] = value
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except:
            return False
    
    def get_setting(self, key, default=None):
        collection = self.get_collection("settings")
        if collection:
            try:
                setting = collection.find_one({"key": key})
                if setting:
                    return setting.get("value", default)
            except:
                pass
        return self._get_setting_file(key, default)
    
    def _get_setting_file(self, key, default=None):
        settings_file = f"{DATA_DIR}/settings.json"
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                return settings.get(key, default)
        except:
            return default
        return default
    
    # API Settings
    def save_api_setting(self, service, data):
        collection = self.get_collection("api_settings")
        if collection:
            try:
                collection.update_one({"service": service}, {"$set": data}, upsert=True)
                return True
            except:
                pass
        return self._save_api_setting_file(service, data)
    
    def _save_api_setting_file(self, service, data):
        api_file = f"{DATA_DIR}/api_settings.json"
        try:
            api_settings = {}
            if os.path.exists(api_file):
                with open(api_file, 'r') as f:
                    api_settings = json.load(f)
            api_settings[service] = data
            with open(api_file, 'w') as f:
                json.dump(api_settings, f, indent=2)
            return True
        except:
            return False
    
    def get_api_setting(self, service):
        collection = self.get_collection("api_settings")
        if collection:
            try:
                setting = collection.find_one({"service": service})
                if setting:
                    setting.pop("_id", None)
                    return setting
            except:
                pass
        return self._get_api_setting_file(service)
    
    def _get_api_setting_file(self, service):
        api_file = f"{DATA_DIR}/api_settings.json"
        try:
            if os.path.exists(api_file):
                with open(api_file, 'r') as f:
                    api_settings = json.load(f)
                return api_settings.get(service)
        except:
            return None
        return None
    
    # Key methods
    def save_key(self, key, data):
        collection = self.get_collection("generated_keys")
        if collection:
            try:
                collection.update_one({"key": key}, {"$set": data}, upsert=True)
                return True
            except:
                pass
        return self._save_key_file(key, data)
    
    def _save_key_file(self, key, data):
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            keys = {}
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
            keys[key] = data
            with open(keys_file, 'w') as f:
                json.dump(keys, f, indent=2)
            return True
        except:
            return False
    
    def get_key(self, key):
        collection = self.get_collection("generated_keys")
        if collection:
            try:
                key_data = collection.find_one({"key": key})
                if key_data:
                    key_data.pop("_id", None)
                    return key_data
            except:
                pass
        return self._get_key_file(key)
    
    def _get_key_file(self, key):
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                return keys.get(key)
        except:
            return None
        return None
    
    def get_all_keys(self):
        collection = self.get_collection("generated_keys")
        if collection:
            try:
                keys = list(collection.find({}))
                for k in keys:
                    k.pop("_id", None)
                return keys
            except:
                pass
        return self._get_all_keys_file()
    
    def _get_all_keys_file(self):
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                return list(keys.values())
        except:
            return []
        return []
    
    def delete_key(self, key):
        collection = self.get_collection("generated_keys")
        if collection:
            try:
                result = collection.delete_one({"key": key})
                return result.deleted_count > 0
            except:
                pass
        return self._delete_key_file(key)
    
    def _delete_key_file(self, key):
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                if key in keys:
                    del keys[key]
                    with open(keys_file, 'w') as f:
                        json.dump(keys, f, indent=2)
                    return True
        except:
            return False
        return False
    
    def delete_unused_keys(self, key_type=None):
        collection = self.get_collection("generated_keys")
        if collection:
            try:
                query = {"is_used": False}
                if key_type and key_type != "all":
                    query["key_type"] = key_type
                result = collection.delete_many(query)
                return result.deleted_count
            except:
                pass
        return self._delete_unused_keys_file(key_type)
    
    def _delete_unused_keys_file(self, key_type=None):
        keys_file = f"{DATA_DIR}/generated_keys.json"
        try:
            if os.path.exists(keys_file):
                with open(keys_file, 'r') as f:
                    keys = json.load(f)
                to_delete = []
                for k, data in keys.items():
                    if not data.get("is_used", False):
                        if not key_type or key_type == "all" or data.get("key_type") == key_type:
                            to_delete.append(k)
                for k in to_delete:
                    del keys[k]
                with open(keys_file, 'w') as f:
                    json.dump(keys, f, indent=2)
                return len(to_delete)
        except:
            return 0
        return 0
    
    # Blocked numbers
    def save_blocked_number(self, number, data):
        collection = self.get_collection("blocked_numbers")
        if collection:
            try:
                collection.update_one({"number": number}, {"$set": data}, upsert=True)
                return True
            except:
                pass
        return self._save_blocked_number_file(number, data)
    
    def _save_blocked_number_file(self, number, data):
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            blocked = {}
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
            blocked[number] = data
            with open(blocked_file, 'w') as f:
                json.dump(blocked, f, indent=2)
            return True
        except:
            return False
    
    def get_blocked_number(self, number):
        collection = self.get_collection("blocked_numbers")
        if collection:
            try:
                return collection.find_one({"number": number})
            except:
                pass
        return self._get_blocked_number_file(number)
    
    def _get_blocked_number_file(self, number):
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
                return blocked.get(number)
        except:
            return None
        return None
    
    def get_all_blocked_numbers(self):
        collection = self.get_collection("blocked_numbers")
        if collection:
            try:
                return list(collection.find({}))
            except:
                pass
        return self._get_all_blocked_numbers_file()
    
    def _get_all_blocked_numbers_file(self):
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
                return [{"number": k, **v} for k, v in blocked.items()]
        except:
            return []
        return []
    
    def remove_blocked_number(self, number):
        collection = self.get_collection("blocked_numbers")
        if collection:
            try:
                result = collection.delete_one({"number": number})
                return result.deleted_count > 0
            except:
                pass
        return self._remove_blocked_number_file(number)
    
    def _remove_blocked_number_file(self, number):
        blocked_file = f"{DATA_DIR}/blocked.json"
        try:
            if os.path.exists(blocked_file):
                with open(blocked_file, 'r') as f:
                    blocked = json.load(f)
                if number in blocked:
                    del blocked[number]
                    with open(blocked_file, 'w') as f:
                        json.dump(blocked, f, indent=2)
                    return True
        except:
            return False
        return False
    
    # Search history
    def save_search_result(self, user_id, search_type, query, result):
        collection = self.get_collection("search_history")
        if collection:
            try:
                collection.insert_one({
                    "user_id": user_id,
                    "search_type": search_type,
                    "query": query,
                    "result": result,
                    "timestamp": datetime.now()
                })
                return True
            except:
                pass
        return False
    
    # Logs
    def save_log(self, log_type, data):
        collection = self.get_collection("logs")
        if collection:
            try:
                collection.insert_one({"type": log_type, "data": data, "timestamp": datetime.now()})
                return True
            except:
                pass
        return False
    
    # Stats
    def get_stats(self):
        stats = {"total_users": 0, "total_keys": 0, "used_keys": 0, "total_searches": 0}
        users = self.get_all_users()
        stats["total_users"] = len(users)
        keys = self.get_all_keys()
        stats["total_keys"] = len(keys)
        stats["used_keys"] = sum(1 for k in keys if k.get("is_used", False))
        return stats