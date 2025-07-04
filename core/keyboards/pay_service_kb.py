from aiogram.utils.keyboard import InlineKeyboardBuilder


def pay_service_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='Оплатить 5 руб', callback_data='pay_5')
    kb.button(text='Оплатить 10 руб', callback_data='pay_10')
    kb.button(text='Оплатить 15 руб', callback_data='pay_15')
    kb.button(text='Оплатить 100 руб', callback_data='pay_100')
    kb.button(text='Оплатить 200 руб', callback_data='pay_200')
    kb.button(text='Оплатить 300 руб', callback_data='pay_300')
    kb.button(text='⬅️ Назад', callback_data='back_to_main')
    kb.adjust(1)
    return kb.as_markup()
