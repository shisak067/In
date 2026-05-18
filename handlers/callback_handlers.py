# handlers/callback_handlers.py
import json
from io import BytesIO
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from utils.helpers import user_last_result

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if query.data == "download_result":
        result_data = user_last_result.get(user_id)
        if not result_data:
            await query.edit_message_text("❌ No result found! Please search again.")
            return
        
        filename = f"{result_data['service']}_{result_data['query']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_content = json.dumps(result_data['result'], indent=2, ensure_ascii=False)
        
        try:
            bio = BytesIO(file_content.encode('utf-8'))
            bio.name = filename
            await query.message.reply_document(
                document=bio,
                filename=filename,
                caption=f"📄 *{result_data['service']} Search Result*\n🔍 `{result_data['query']}`",
                parse_mode="Markdown"
            )
            bio.close()
        except Exception as e:
            await query.message.reply_text(f"❌ Error: {str(e)}")
    
    elif query.data == "close":
        await query.delete_message()
