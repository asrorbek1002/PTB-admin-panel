from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from telegram import Update
from LotoBot.settings import TELEGRAM_BOT_TOKEN
from .BotCommands.StartCommand import start
from .BotAdmin.AdminMenu import admin_menyu
from .BotHandler.SendMessage import send_msg_handler
from .BotHandler.BotStats import bot_stats
from .BotAdmin.AddAdmin import add_admin_handler
from .BotAdmin.DeleteAdmin import remove_admin_handler
from .BotHandler.checkChannel import check_channel
from .MandatoryChannel.Add_channel import AddChannel_ConvHandler
from .MandatoryChannel.Delete_mandatory import start_delete_mandatory, delete_mandatory


def main():

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('admin', admin_menyu))
    app.add_handler(CommandHandler('test', check_channel))

    # Conversation handlers
    app.add_handler(send_msg_handler)
    app.add_handler(add_admin_handler)
    app.add_handler(remove_admin_handler)
    app.add_handler(AddChannel_ConvHandler)

    # Inline hanlder
    app.add_handler(CallbackQueryHandler(bot_stats, pattern=r"^botstats$"))
    app.add_handler(CallbackQueryHandler(start_delete_mandatory, pattern=r"^Del_mandatory$"))
    app.add_handler(CallbackQueryHandler(delete_mandatory, pattern=r"^xDeleted_"))

    # Bot start
    print("The bot is running!!!")
    app.run_polling()
