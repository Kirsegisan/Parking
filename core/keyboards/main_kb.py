from aiogram.utils.keyboard import InlineKeyboardBuilder

ONLY_FIND_OBJECTS_BUTTONS = (
    ('🔍 Найти объект', 'find_object'),
    ('⏬ Остальное меню', 'main_menu')
)


MAIN_CHOOSE_BUTTONS = (
    ('🔍 Найти объект', 'find_object'),
    ('✍️ Редактировать свои адреса', 'edit_addresses'),
    ('💳 Оплатить сервис', 'pay_service'),
    ('🗳 Обратная связь', 'feedback'),
    ('👨‍👧‍👧Пригласить друзей и получить скидку', 'invite_friends')
)


def start_button():
    kb = InlineKeyboardBuilder()
    kb.button(text='🚀 ПРИСОЕДИНИТЬСЯ', callback_data='start_bot')
    return kb.as_markup()


def short_menu_buttons():
    kb = InlineKeyboardBuilder()
    for text, callback_data in ONLY_FIND_OBJECTS_BUTTONS:
        kb.button(text=text, callback_data=callback_data)
    kb.adjust(1)
    return kb.as_markup()


def main_menu_buttons():
    kb = InlineKeyboardBuilder()
    for text, callback_data in MAIN_CHOOSE_BUTTONS:
        kb.button(text=text, callback_data=callback_data)
    kb.button(text='🔗 Как подключить сервис', url='https://ya.ru'),
    kb.button(text='ℹ️ О проекте', url='https://google.com')
    kb.adjust(1)
    return kb.as_markup()


def add_address_button():
    kb = InlineKeyboardBuilder()
    kb.button(text='💾 Сохранить', callback_data='confirm_address')
    kb.button(text='⬅️ Отменить', callback_data='cancel_address')
    kb.adjust(1)
    return kb.as_markup()


def edit_address_button():
    kb = InlineKeyboardBuilder()
    kb.button(text='🗑️ Удалить адрес', callback_data='delete_address')
    kb.button(text='⬅️ Назад', callback_data='cancel_address')
    return kb.as_markup()


def back_to_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='В главное меню', callback_data='back_to_main')
    return kb.as_markup()
