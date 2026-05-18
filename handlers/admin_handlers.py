# handlers/admin_handlers.py
from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.helpers import is_admin, settings, mongo, toggle_maintenance_mode
from utils.keyboards import get_admin_keyboard, get_main_keyboard

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("⚙️ *Admin Panel*", parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_keyboard())

async def toggle_maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    new_state = toggle_maintenance_mode(mongo)
    status = "ON 🟢" if new_state else "OFF 🔴"
    await update.message.reply_text(f"🛠️ Maintenance Mode: {status}", reply_markup=get_admin_keyboard())

async def toggle_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    settings["bot_active"] = not settings["bot_active"]
    mongo.save_setting("bot_active", settings["bot_active"])
    status = "ACTIVE 🟢" if settings["bot_active"] else "INACTIVE 🔴"
    await update.message.reply_text(f"Bot: {status}", reply_markup=get_admin_keyboard())

async def bot_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    stats = mongo.get_stats()
    from utils.helpers import get_bot_uptime, MAINTENANCE_MODE
    uptime = get_bot_uptime()
    text = f"📊 *Bot Status*\nUsers: {stats['total_users']}\nKeys: {stats['total_keys']}\nUptime: {uptime}\nMaintenance: {'ON' if MAINTENANCE_MODE else 'OFF'}"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_keyboard())

async def all_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    users = mongo.get_all_users()
    text = f"👥 *Total Users:* {len(users)}\n\n"
    for i, u in enumerate(users[:20], 1):
        text += f"{i}. `{u['user_id']}` - {u.get('username', 'No name')}\n"
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_admin_keyboard())

async def exit_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return
    await update.message.reply_text("✅ Exited Admin", reply_markup=get_main_keyboard(update.effective_user.id))

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    user_id = update.effective_user.id
    await update.message.reply_text("❌ Cancelled", reply_markup=get_main_keyboard(user_id))
    return ConversationHandler.END
