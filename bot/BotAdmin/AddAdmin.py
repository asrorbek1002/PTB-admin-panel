from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler, CommandHandler, MessageHandler, filters, CallbackQueryHandler
from ..models import TelegramUser  # Django modelingizni import qiling
from ..decorators import admin_required

from warnings import filterwarnings
from telegram.warnings import PTBUserWarning

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


# ConversationHandler bosqichlari
ASK_USER_ID, CONFIRM = range(2)

@admin_required
async def start_add_admin(update: Update, context: CallbackContext) -> int:
    """
    Admin qo'shishni boshlaydi.
    """
    await update.callback_query.edit_message_text(
        "Iltimos, admin qilishni istagan foydalanuvchi ID sini kiriting:"
    )
    return ASK_USER_ID

@admin_required
async def ask_user_id(update: Update, context: CallbackContext) -> int:
    """
    Foydalanuvchi ID ni qabul qiladi va tasdiqlashni so'raydi.
    """
    user_id = update.message.text

    if not user_id.isdigit():
        await update.message.reply_text("ID faqat raqamlardan iborat bo'lishi kerak. Qaytadan kiriting.")
        return ASK_USER_ID

    context.user_data['user_id'] = int(user_id)

    await update.message.reply_text(
        f"Foydalanuvchi ID: {user_id}. Ushbu foydalanuvchini admin qilishni tasdiqlaysizmi? (Ha/Yo'q)",
        reply_markup=ReplyKeyboardMarkup([["Ha", "Yo'q"]], one_time_keyboard=True, resize_keyboard=True)
    )
    return CONFIRM

@admin_required
async def confirm(update: Update, context: CallbackContext) -> int:
    """
    Tasdiqlash jarayoni.
    """
    choice = update.message.text.lower()
    user_id = context.user_data.get('user_id')

    if choice == "ha":
        user = await TelegramUser.make_admin(user_id=user_id)
        if user:
            await update.message.reply_text(f"Foydalanuvchi {user} admin qilindi.")
            await context.bot.send_message(chat_id=user_id, text="Tabriklayman siz hozirgina admin bo'ldingiz")
        else:
            await update.message.reply_text("Bunday foydalanuvchi topilmadi.")
    elif choice == "yo'q":
        await update.message.reply_text("Amal bekor qilindi.")
    else:
        await update.message.reply_text("Iltimos, faqat 'Ha' yoki 'Yo'q' deb javob bering.")
        return CONFIRM

    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    """
    Muloqotni bekor qiladi.
    """
    await update.message.reply_text("Admin qo'shish bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# ConversationHandler ni sozlash
add_admin_handler = ConversationHandler(
    entry_points=[CallbackQueryHandler(start_add_admin, pattern='^add_admin$')],
    states={
        ASK_USER_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_user_id)],
        CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
    },
    fallbacks=[CommandHandler('cancel', cancel)],
)