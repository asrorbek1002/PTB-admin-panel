from telegram.ext import ContextTypes

from telegram import (
    Update,
    KeyboardButtonRequestChat,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ChatAdministratorRights,
)


lists = ["administrator", "member", "creator"]

async def check_channel(update:Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    print(user_id)
    # mandatory_channel = [-1002243017689, -1002064132087, -1002442002199]
    # for channel_id in mandatory_channel:
    #     try:
    #         is_member = await context.bot.get_chat_member(channel_id, user_id)
    #         if is_member.status in lists:
    #             print("A'zo")
    #             continue
    #         else:
    #             print("A'zo Emas")
    #             break
    #     except Exception as e:
    #         print(e)
    #    # Chat so'rovi tugmasini yaratamiz
    # chat_request_button = KeyboardButton(
    #     text="Guruh tanlash",
    #     request_chat=KeyboardButtonRequestChat(
    #         request_id=1,  
    #         chat_is_channel=False,
    #         bot_administrator_rights=ChatAdministratorRights(
                
    #         )  
    #         chat_is_forum=False, 
    #         ),
    # )

    # # Tugmalarni biriktirish
    # keyboard = [[chat_request_button]]
    # reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # await update.message.reply_text(
    #     "Quyidagi tugma orqali guruh tanlang:", reply_markup=reply_markup
    # )


from functools import wraps
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

def admin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user_id = update.effective_user.id
        # Kanalga a'zoligini tekshirish
        try:
            pass
            # user = await TelegramUser.objects.aget(user_id=user_id)  # Django ORM ning asinxron `aget` metodi
            # if not user.is_admin:
            #     await context.bot.send_message(chat_id=user_id, text="Siz admin emassiz!😠")
            #     return ConversationHandler.END
                
        except Exception as e:
            await context.bot.send_message(chat_id=user_id, text="Sizning ma'lumotlaringiz topilmadi.\n/start")
            return ConversationHandler.END
        
        # Agar admin bo‘lsa, funksiya chaqiriladi
        return await func(update, context, *args, **kwargs)
    return wrapper
