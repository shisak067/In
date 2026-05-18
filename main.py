# main.py
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackQueryHandler
from config import BOT_TOKEN, ASKING_NUMBER, ASKING_AADHAR, ASKING_PAK_NUM, ASKING_PAK_CNIC, ASKING_PAK_POLICE, ASKING_GST_BILLING, ASKING_PAN_GST, ASKING_AADHAR_FAMILY, ASKING_REDEEM_KEY
from database import MongoDBManager, MONGO_URI, MONGO_DB_NAME
from utils.helpers import load_settings
from handlers.user_handlers import start_command, my_coins, my_stats, help_command, system_info_command
from handlers.search_handlers import indian_number_button, handle_indian_number, indian_aadhar_button, handle_indian_aadhar, pak_number_button, handle_pak_number, pak_cnic_button, handle_pak_cnic, pak_police_button, handle_pak_police, gst_billing_button, handle_gst_billing, pan_gst_button, handle_pan_gst, aadhar_family_button, handle_aadhar_family
from handlers.admin_handlers import admin_panel, toggle_maintenance, toggle_bot, bot_status, all_users, exit_admin, cancel_operation
from handlers.callback_handlers import handle_callback

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

mongo = MongoDBManager(MONGO_URI, MONGO_DB_NAME)

def main():
    load_settings(mongo)
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Add conversation handlers
    app.add_handler(ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔍 Indian Number$"), lambda u,c: indian_number_button(u,c,mongo))],
        states={ASKING_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u,c: handle_indian_number(u,c,mongo))]},
        fallbacks=[MessageHandler(filters.Regex("^❌ Cancel$"), cancel_operation)]
    ))
    
    # Add more handlers similarly...
    
    # Command handlers
    app.add_handler(CommandHandler("start", lambda u,c: start_command(u,c,mongo)))
    app.add_handler(CommandHandler("coins", lambda u,c: my_coins(u,c,mongo)))
    app.add_handler(CommandHandler("stats", lambda u,c: my_stats(u,c,mongo)))
    app.add_handler(CommandHandler("help", lambda u,c: help_command(u,c,mongo)))
    app.add_handler(CommandHandler("system", lambda u,c: system_info_command(u,c,mongo)))
    
    # Admin handlers
    app.add_handler(MessageHandler(filters.Regex("^⚙️ Admin Panel$"), admin_panel))
    app.add_handler(MessageHandler(filters.Regex("^🔴 MAINTENANCE OFF$|^🟢 MAINTENANCE ON$"), toggle_maintenance))
    app.add_handler(MessageHandler(filters.Regex("^🔛 Toggle Bot$"), toggle_bot))
    app.add_handler(MessageHandler(filters.Regex("^📊 Bot Status$"), bot_status))
    app.add_handler(MessageHandler(filters.Regex("^👥 All Users$"), all_users))
    app.add_handler(MessageHandler(filters.Regex("^🔙 Exit Admin$"), exit_admin))
    
    # User menu handlers
    app.add_handler(MessageHandler(filters.Regex("^💎 My Coins$"), lambda u,c: my_coins(u,c,mongo)))
    app.add_handler(MessageHandler(filters.Regex("^📊 Stats$"), lambda u,c: my_stats(u,c,mongo)))
    app.add_handler(MessageHandler(filters.Regex("^❓ Help$"), lambda u,c: help_command(u,c,mongo)))
    app.add_handler(MessageHandler(filters.Regex("^🖥️ System Info$"), lambda u,c: system_info_command(u,c,mongo)))
    
    # Callback handler for download button
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    logger.info("Bot Started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
