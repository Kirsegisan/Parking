import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import cv2
from telegram import Update, ReplyKeyboardMarkup, replykeyboardremove
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext, ConversationHandler
import app
import threading
import requests
from key import TOKEN
import source as sr
import conectToUserDataBase as usersDB
import conetcToCamerasDataBase as camerasDB
import traceback
from exportDB import export_sqlite_to_xlsx

# -*- coding: utf-8 -*-

# Список баз данных для экспорта
db_files = ['referrals.db', 'subscriptions.db', 'users.db']
# Название выходного файла
output_file = 'exported_data.xlsx'

URL = 'https://api.telegram.org/bot'
papaChatID = 1974355978

WAIT_Address, WAIT_Name = 1, 2

def main():
    updater = Updater(
        token=TOKEN,
        use_context=True
    )

    dispatcher = updater.dispatcher
    exportDB = MessageHandler(Filters.text("exportDB"), exportDataBase)
    papa_hendler = MessageHandler(Filters.text("Hi"), meat_papa)
    meatHendler = MessageHandler(Filters.text("/start"), meat)
    addHendler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text("add"), addStart)],
        states={
            WAIT_Address: [MessageHandler(Filters.text, addName)],
            WAIT_Name: [MessageHandler(Filters.text, addEnd)]
        },
        fallbacks=[]
    )

    keyboardHandler = MessageHandler(Filters.text("keyboard"), keyboard)
    delHandler = MessageHandler(Filters.text("delete data"), call_delete_data)
    call_detectHandler = MessageHandler(Filters.text(camerasDB.getAddressesString()), call_detect)
    echoHandler = MessageHandler(Filters.all, echo)

    #dispatcher.add_handler(papa_hendler)
    dispatcher.add_handler(exportDB)
    dispatcher.add_handler(meatHendler)
    dispatcher.add_handler(addHendler)
    dispatcher.add_handler(keyboardHandler)
    dispatcher.add_handler(delHandler)
    dispatcher.add_handler(call_detectHandler)
    dispatcher.add_handler(echoHandler)

    updater.start_polling()
    print('successful launch')
    updater.idle()


def call_delete_data(update, context):
    if update.message.from_user.name == "@Kirsegisan":
        sr.delete_data()
        update.message.reply_text("Я обнулил базу данных")
    else:
        update.message.reply_text(f"Ты не мой папа")


def meat_papa(update, context):
    if update.message.from_user.name == "@Kirsegisan":
        update.message.reply_text(f"Привет папа")
        global papaChatID
        papaChatID = update.message.chat_id
        print(papaChatID)

    else:
        update.message.reply_text(f"Ты не мой папа")


def call_detect(update, context):
    update.message.reply_text(f"Сейчас посмотрим...")
    update.message.chat.send_chat_action("typing")
    try:
        detect_result = camerasDB.detAnalysisAddresses(update.message.text)
        update.message.reply_text(f"Я нашел {len(detect_result[1])} свободных мест, {len(detect_result[2])} занятых и в {len(detect_result[3])} в сомневаюсь, не часто там ставят машины")
        cv2.imwrite('./image_test_free.png', detect_result[0])
        files = {'photo': open('./image_test_free.png', 'rb')}
        requests.post(f'{URL}{TOKEN}/sendPhoto?chat_id={update.message.chat_id}', files=files)
    except Exception as e:
        # Печатаем ошибку в консоль
        print(f"Произошла ошибка: {e}")
        traceback.print_exc()  # Это напечатает полный traceback ошибки
        update.message.reply_text("Что-то пошло не так, и все сломалось")
    update.message.chat.send_chat_action("CANCEL")


def keyboard(update, context):
    buttons = [
        ['delete data'],
        ['detect train'],
        ['detect test'],
        ["exportDB"]
    ]
    update.message.reply_text(
        text='Now, you have kayboard',
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )

    )


def echo(update, context):
    if usersDB.userInDB(update.message.chat_id):
        text = update.message.text
        chatID = update.message.chat_id
        name = update.message.from_user.name
        user = usersDB.User(update.message.chat_id)
        if text in user.getUserCameras():
            update.message.text = user.getUserCameraID(text)
            return call_detect(update, context)
        else:
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


def messageForPapa(update, context, text):
    update.message.reply_text(f"Сейчас посмотрим...", chat_id=1974355978)
    requests.get(f'{URL}{TOKEN}/sendMessage?chat_id={1974355978}&text={text}').json()


def meat(update, context):
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


def addAddress(update, context):
    if usersDB.userInDB(update.message.chat_id):
        user = usersDB.User(update.message.chat_id)
        update.message.reply_text(
            text="Какой адрес вы хотите добавить в список избранных?",
            reply_markup=ReplyKeyboardMarkup(
                camerasDB.getAddresses(),
                resize_keyboard=True
            )
        )
        # message = update.message.text
        # if message in camerasDB.getAddresses():
        #     user.addACameraIDToTheUser(message)
        # else:
        #     return addError(update, context)

    return WAIT_Address


def addError(update, context):
    update.message.reply_text(f"Я такого адреса не знаю")
    return ConversationHandler.END


def addName(update, context):
    user = usersDB.User(update.message.chat_id)
    message = update.message.text
    if message in camerasDB.getAddressesList():
        user.addACameraIDToTheUser(message)
    else:
        return addError(update, context)
    return WAIT_Name


def addEnd(update, context):
    user = usersDB.User(update.message.chat_id)
    user.addCameraNameToTheUser(update.message.text)
    update.message.reply_text(
        text="Адресс добавлен",
        reply_markup=ReplyKeyboardMarkup(
            user.getUserAddresses(),
            resize_keyboard=True
        )
    )
    return ConversationHandler.END


def addStart(update, context):
    update.message.reply_text(f"(Правила добавления)")
    return addAddress(update, context)


# def wait(update: Update, context: CallbackContext):
#     while True:
#         messageForPapa(update, context, "")
#         print("")
#         time.sleep(20*60)


def exportDataBase(update, context):
    export_and_send_xlsx(TOKEN, update.message.chat_id, db_files)


def export_and_send_xlsx(
        bot_token: str,
        chat_id: str,
        db_files: list,
        temp_xlsx: str = "exported_data.xlsx"
) -> bool:
    """
    Экспортирует SQLite базы в XLSX и отправляет файл в Telegram чат.

    Параметры:
        bot_token (str): Токен вашего бота (например, "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11")
        chat_id (str): ID чата (можно получить из update.message.chat_id)
        db_files (list): Список путей к файлам БД (например, ["referrals.db", "subscriptions.db"])
        temp_xlsx (str): Временный файл для экспорта (по умолчанию "exported_data.xlsx")

    Возвращает:
        bool: True если отправка успешна, False при ошибке.
    """
    try:
        # 1. Создаем XLSX-файл
        export_sqlite_to_xlsx(db_files, temp_xlsx)
        # 2. Отправка через Telegram API
        url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
        with open(temp_xlsx, "rb") as file:
            files = {"document": file}
            data = {"chat_id": chat_id}
            response = requests.post(url, files=files, data=data)
        os.remove(temp_xlsx)
        # 3. Проверяем успешность
        if response.status_code == 200:
            print("Файл успешно отправлен!")
            return True
        else:
            print(f"Ошибка при отправке: {response.json()}")
            return False

    except Exception as e:
        print(f"⚠️ Ошибка: {str(e)}")
        return False


if __name__ == '__main__':
    main()
