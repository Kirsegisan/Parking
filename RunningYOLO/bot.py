import cv2
from telegram import Update, ReplyKeyboardMarkup, replykeyboardremove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, ConversationHandler
import app
import time
import threading
import requests
from key import TOKEN
import source as sr
import conectToUserDataBase as usersDB
import conetcToCamerasDataBase as camerasDB

URL = 'https://api.telegram.org/bot'
papaChatID = 1974355978

WAIT_Address, WAIT_Name = 1, 2

def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )

    dispatcher = updater.dispatcher
    # Объявление хендлеров
    papa_hendler = MessageHandler(Filters.text("Ку"), meat_papa)
    meatHendler = MessageHandler(Filters.text("/start"), meat)
    addHendler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text("add"), addStart)],
        states={
            WAIT_Address: [MessageHandler(Filters.text, addName)],
            WAIT_Name: [MessageHandler(Filters.text, addEnd)],
        },
        fallbacks=[]
    )

    keyboardHandler = MessageHandler(Filters.text("keyboard"), keyboard)
    delHandler = MessageHandler(Filters.text("delete data"), call_delete_data)
    call_detectHandler = MessageHandler(Filters.text(camerasDB.getAddressesString()), call_detect)
    echoHandler = MessageHandler(Filters.all, echo)

    # порядок выполнения хендлеров
    #dispatcher.add_handler(papa_hendler)
    dispatcher.add_handler(meatHendler)
    dispatcher.add_handler(addHendler)
    dispatcher.add_handler(keyboardHandler)
    dispatcher.add_handler(delHandler)
    dispatcher.add_handler(call_detectHandler)
    dispatcher.add_handler(echoHandler)

    updater.start_polling()
    print('successful launch')
    updater.idle()


def call_delete_data(update: Update, context: CallbackContext):
    sr.delete_data()
    update.message.reply_text("Я обнулил базу данных")


def meat_papa(update: Update, context: CallbackContext):
    if update.message.from_user.name == "@Kirsegisan":
        update.message.reply_text(f"Привет папа")
        global papaChatID
        papaChatID = update.message.chat_id
        print(papaChatID)

    else:
        update.message.reply_text(f"Ты не мой папа")


def call_detect(update: Update, context: CallbackContext):
    update.message.reply_text(f"Сейчас посмотрим...")
    update.message.chat.send_chat_action("typing")
    detect_result = camerasDB.detAnalysisAddresses(update.message.text)
    update.message.reply_text(f"Я нашел {len(detect_result[1])} мест")
    cv2.imwrite('./image_test_free.png', detect_result[0])
    files = {'photo': open('./image_test_free.png', 'rb')}
    requests.post(f'{URL}{TOKEN}/sendPhoto?chat_id={update.message.chat_id}', files=files)
    update.message.chat.send_chat_action("CANCEL")


def keyboard(update: Update, context: CallbackContext):
    buttons = [
        ['delete data'],
        ['detect train'],
        ['detect test']
    ]
    update.message.reply_text(
        text='Now, you have kayboard',
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )

    )


def echo(update: Update, context: CallbackContext):
    if usersDB.userInDB(update.message.chat_id):
        text = update.message.text
        chatID = update.message.chat_id
        name = update.message.from_user.name
        update.message.reply_text(
            text="Я не понял команду, вот доступные адреса",
            reply_markup=ReplyKeyboardMarkup(
                camerasDB.getAddresses(),
                resize_keyboard=True
            )
        )
    else:
        meat(update, context)
    return


def messageForPapa(update: Update, context: CallbackContext, text):
    update.message.reply_text(f"Сейчас посмотрим...", chat_id=1974355978)
    requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={1974355978}&text={text}').json()


def meat(update: Update, context: CallbackContext):
    update.message.reply_text(
        text=f"Приветствую, {update.message.from_user.name}, я ваши виртуальные глаза, которые помогут найти свободное место для парковки\n"
             "Я работаю по этим адресам\n"
             "(Предлагает клавиатуру со всеми доступными адресами)\nВы можете добавить камеру в лист часто используемых"
             "\nдля этого напишите (add)",
        reply_markup=ReplyKeyboardMarkup(
            camerasDB.getAddresses(),
            resize_keyboard=True
        )
    )
    if not usersDB.userInDB(update.message.chat_id):
        usersDB.User(update.message.chat_id)
    else:
        print("Уже в базе данных")


def addAddress(update: Update, context: CallbackContext):
    if usersDB.userInDB(update.message.chat_id):
        user = usersDB.User(update.message.chat_id)
        user.addACameraIDToTheUser(update.message.text)

    return WAIT_Address


def addError(update: Update, context: CallbackContext):
    update.message.reply_text(f"Я такого адресса не знаю")
    return ConversationHandler.END


def addName(update: Update, context: CallbackContext):
    user = usersDB.User(update.message.chat_id)
    user.addACameraIDToTheUser(update.message.text)
    return WAIT_Name


def addEnd(update: Update, context: CallbackContext):
    user = usersDB.User(update.message.chat_id)
    user.addCameraNameToTheUser(update.message.text)
    update.message.reply_text(f"Адресс добавлен")
    return ConversationHandler.END


def addStart(update: Update, context: CallbackContext):
    update.message.reply_text(f"Что добавить")
    return addAddress(update, context)


def wait(update: Update, context: CallbackContext):
    while True:
        messageForPapa(update, context, "Я не сплю")
        print("Я не сплю")
        time.sleep(20*60)



if __name__ == '__main__':
    main()
