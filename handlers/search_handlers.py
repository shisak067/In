# handlers/search_handlers.py
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
from config import ASKING_NUMBER, ASKING_AADHAR, ASKING_PAK_NUM, ASKING_PAK_CNIC, ASKING_PAK_POLICE, ASKING_GST_BILLING, ASKING_PAN_GST, ASKING_AADHAR_FAMILY
from utils.helpers import can_search, use_coin, update_user_stats, save_search_result
from utils.keyboards import get_main_keyboard, get_cancel_keyboard
from utils.api_client import search_indian_number, search_indian_aadhar, search_pak_number, search_pak_cnic, search_pak_police, search_gst_billing, search_pan_gst, search_aadhar_family
from handlers.user_handlers import check_maintenance, send_result

async def check_and_start_search(update, context, mongo, search_type):
    user_id = update.effective_user.id
    if await check_maintenance(update, context, mongo):
        return False
    can, remaining, use_coin_flag = can_search(mongo, user_id)
    if not can:
        user = get_user(mongo, user_id)
        await update.message.reply_text(f"❌ Daily limit reached!\n💰 Coins: {user['coins']}", parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_keyboard(user_id))
        return False
    if use_coin_flag:
        await update.message.reply_text("⚠️ Using 1 coin...", parse_mode=ParseMode.MARKDOWN)
        context.user_data["use_coin"] = True
    else:
        context.user_data["use_coin"] = False
    context.user_data["search_type"] = search_type
    return True

async def indian_number_button(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    if not await check_and_start_search(update, context, mongo, "num"):
        return ConversationHandler.END
    await update.message.reply_text("🔍 *Enter Indian Number:*\nExample: `9876543210`", parse_mode=ParseMode.MARKDOWN, reply_markup=get_cancel_keyboard())
    return ASKING_NUMBER

async def handle_indian_number(update: Update, context: ContextTypes.DEFAULT_TYPE, mongo):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    if text == "❌ Cancel":
        await update.message.reply_text("❌ Cancelled", reply_markup=get_main_keyboard(user_id))
        return ConversationHandler.END
    
    number = ''.join(filter(str.isdigit, text))
    if len(number) < 10:
        await update.message.reply_text("❌ Invalid number!", reply_markup=get_cancel_keyboard())
        return ASKING_NUMBER
    
    if context.user_data.get("use_coin", False):
        if not use_coin(mongo, user_id):
            await update.message.reply_text("❌ Not enough coins!", reply_markup=get_main_keyboard(user_id))
            return ConversationHandler.END
    
    await update.message.chat.send_action(action="typing")
    status_msg = await update.message.reply_text("⏳ Searching...")
    result = await search_indian_number(number, mongo)
    await status_msg.delete()
    
    if "error" not in result:
        update_user_stats(mongo, user_id)
        save_search_result(mongo, user_id, "indian_number", number, result)
    
    await send_result(update, result, number, "INDIAN NUMBER", user_id, mongo)
    return ConversationHandler.END

# Similar handlers for aadhar, pak_number, pak_cnic, pak_police, gst_billing, pan_gst, aadhar_family
# (Add them similarly - same pattern as above)
