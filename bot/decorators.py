from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from django.db.models import QuerySet
from asgiref.sync import sync_to_async
from .models import Channel, TelegramUser

lists = ["administrator", "member", "creator"]

def admin_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        # Adminni tekshirish
        try:
            user = await TelegramUser.objects.aget(user_id=user_id)  # Django ORM ning asinxron `aget` metodi
            if not user.is_admin:
                await context.bot.send_message(chat_id=user_id, text="Siz admin emassiz!😠")
                return ConversationHandler.END
                
        except TelegramUser.DoesNotExist:
            await context.bot.send_message(chat_id=user_id, text="Sizning ma'lumotlaringiz topilmadi.\n/start")
            return ConversationHandler.END
        
        # Agar admin bo‘lsa, funksiya chaqiriladi
        return await func(update, context, *args, **kwargs)
    return wrapper


from functools import wraps
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from asgiref.sync import sync_to_async
from .models import Channel, TelegramUser

# Barcha Channel ma'lumotlarini olish uchun asinxron funksiya
@sync_to_async
def get_all_channels():
    return list(Channel.objects.all())  # QuerySet ni ro'yxatga aylantirish

# Foydalanuvchi kanalga a'zo ekanligini tekshirish uchun dekorator
def mandatory_channel_required(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        
        try:
            # Foydalanuvchini bazadan topish
            user = await sync_to_async(TelegramUser.objects.get)(user_id=user_id)
            user_id = user.user_id

            # InlineKeyboard uchun tugmalar yaratish
            keyboards = []

            # Barcha kanallarni olish
            channels = await get_all_channels()

            # Har bir kanal uchun tugma yaratish
            for channel in channels:
                keyboards.append([InlineKeyboardButton(text=f"{channel.name}", url=f"{channel.url}")])

            # Foydalanuvchi kanalga a'zo ekanligini tekshirish
            for channel in channels:
                try:
                    # Foydalanuvchi statusini tekshirish
                    is_member = await context.bot.get_chat_member(chat_id=channel.channel_id, user_id=user_id)
                    if is_member.status in ["member", "administrator", "creator"]:
                        print(f"Foydalanuvchi {channel.name} kanaliga a'zo.")
                        continue
                    else:
                        # Agar foydalanuvchi kanalga a'zo bo'lmasa, xabar yuborish
                        await context.bot.send_message(
                            chat_id=user_id, 
                            text="Iltimos, botdan to'liq foydalanish uchun quyidagi kanallarga a'zo bo'ling:",
                            reply_markup=InlineKeyboardMarkup(keyboards)
                        )
                        return  # Funksiyani to'xtatish
                except Exception as e:
                    print(f"Xatolik: {e}")
                    continue

        except TelegramUser.DoesNotExist:
            # Agar foydalanuvchi topilmasa, xabar yuborish
            await context.bot.send_message(chat_id=user_id, text="Sizning ma'lumotlaringiz topilmadi.\n/start")
            return ConversationHandler.END
    
        # Agar foydalanuvchi barcha kanallarga a'zo bo'lsa, asosiy funksiyani davom ettirish
        return await func(update, context, *args, **kwargs)
    return wrapper

