from telegram.ext import ContextTypes, ConversationHandler
from telegram import Update
from ..utils import save_user_to_db
from ..models import TelegramUser
from ..decorators import mandatory_channel_required

@mandatory_channel_required
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Botni ishga tushirish uchun komanda.
    """
    data = update.effective_user
    is_save = await save_user_to_db(data)
    admin_id = await TelegramUser.get_admin_ids()
    if is_save:
        await update.message.reply_text("Assalomu alaykum")
    else:
        for i in admin_id:
            await context.bot.send_message(chat_id=i, text=f"<a href='tg://user?id={data.id}'>{data.first_name}</a> foydalanuvchini bazaga saqlashda xatolik.\n\nUser ma'lumoti:\n\tID: {data.id}\n\tFirst name: {data.first_name}\n\tUsername: {data.username}", parse_mode="HTML")
        await update.message.reply_text("Assalomu alaykum")
    return ConversationHandler.END