# handlers/user_handlers.py
import json
from datetime import date
from io import BytesIO
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import DEVELOPER_USERNAME, SUPPORT_USERNAME, BOT_NAME, BOT_VERSION, DEVELOPER_LINK, SUPPORT_GROUP_LINK
from utils.helpers import get_user, settings, can_search, use_coin, update_user_stats, save_search_result, get_bot_uptime, get_system_info, is_maintenance_mode, user_last_result
from utils.keyboards import get_main_keyboard, get_cancel_keyboard, get_download_keyboard, get_maintenance_keyboard
from utils.api_client import search_indian_number, search_indian_aadhar, search_pak_number, search_pak_cnic, search_pak_police, search_gst_billing, search_pan_gst, search_aadhar_family

async def check_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo) -> bool:
    user_id = update.effective_user.id
    from utils.helpers import is_admin
    if is_admin(user_id):
        return False
    if is_maintenance_mode():
        await update.message.reply_text(
            "🔧 *Bot is Under Maintenance!*\n\nPlease wait...\n\n📞 Contact: @KINGGKAI",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_maintenance_keyboard(DEVELOPER_LINK, SUPPORT_GROUP_LINK)
        )
        return True
    return False

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    user = update.effective_user
    user_data = get_user(mongo, user.id)
    if user.username:
        user_data["username"] = user.username
        mongo.save_user(user_data)
    
    welcome = f"""
👋 *Welcome {user.first_name}!*

🔍 *{BOT_NAME} v{BOT_VERSION}*

✅ *Services:*
• Indian Number & Aadhar
• Pakistan Number, CNIC, Police
• GST Billing & PAN to GST
• Aadhar Family Details

💰 *Free {settings['daily_limit']} searches/day*

💡 *After each search, click DOWNLOAD button*

👑 *Developer:* @{DEVELOPER_USERNAME}
"""
    await update.message.reply_text(welcome, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user.id))

async def my_coins(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    if await check_maintenance(update, context, mongo):
        return
    user = get_user(mongo, update.effective_user.id)
    from utils.helpers import has_unlimited_coins
    if has_unlimited_coins(update.effective_user.id):
        text = "👑 ADMIN\n💰 Coins: UNLIMITED"
    else:
        text = f"💰 *Balance:* {user['coins']} coins"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def my_stats(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    if await check_maintenance(update, context, mongo):
        return
    user = get_user(mongo, update.effective_user.id)
    today = date.today().isoformat()
    daily = 0 if user["last_search_date"] != today else user["daily_searches"]
    remaining = settings["daily_limit"] - daily
    text = f"📊 *Your Stats*\nTotal: {user['total_searches']}\nToday: {daily}/{settings['daily_limit']}\nRemaining: {remaining}\nCoins: {user['coins']}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    if await check_maintenance(update, context, mongo):
        return
    text = f"❓ *Help*\n\nUse buttons below to search\nAfter result, click DOWNLOAD\nSupport: @{SUPPORT_USERNAME}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def system_info_command(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    if await check_maintenance(update, context, mongo):
        return
    sys_info = get_system_info()
    uptime = get_bot_uptime()
    text = f"🖥️ *System*\nUptime: {uptime}\nCPU: {sys_info['cpu_percent']}%\nRAM: {sys_info['memory_percent']}%\nOS: {sys_info['platform']}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

async def send_result(update, result, query, service_name, user_id, mongo):
    user_last_result[user_id] = {"result": result, "query": query, "service": service_name}
    
    output = f"""
╔══════════════════════════════════════╗
║         {service_name} SEARCH RESULT         
╠══════════════════════════════════════╣
📌 *Query:* `{query}`
╠══════════════════════════════════════╣

📦 *RAW API RESPONSE:*

```json
{json.dumps(result, indent=2, ensure_ascii=False)}
