from telegram import Update, ReplyKeyboardMarkup, replykeyboardremove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, ConversationHandler
import time
from key import TOKEN


papaChatID = 1974355978


def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )

    dispatcher = updater.dispatcher
    papa_hendle = MessageHandler(Filters.text("Ку"), meat_papa)
    echoHandler = MessageHandler(Filters.text("wait"), wait)

    dispatcher.add_handler(papa_hendle)
    dispatcher.add_handler(echoHandler)

    updater.start_polling()
    print('successful launch')
    updater.idle()


def messageForPapa(update: Update, context: CallbackContext, text):
    update.message.reply_text(f"{text}")


def meat_papa(update: Update, context: CallbackContext):
    if update.message.from_user.name == "@Kirsegisan":
        update.message.reply_text(f"Привет папа")
        global papaChatID
        papaChatID = update.message.chat_id
        print(papaChatID)

    else:
        update.message.reply_text(f"ы не мой папа")


def wait(update: Update, context: CallbackContext):
    while True:
        messageForPapa(update, context, "Я не сплю")
        print("Я не сплю")
        time.sleep(20*60)


main()
