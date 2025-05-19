from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from keyboards.main_kb import (
    start_button, short_menu_buttons, main_menu_buttons)
from utils.users_db import (
    add_user, check_user, check_user_contact, update_user_contract)
from utils.refer_db import check_referral

main_router = Router()


@main_router.message(Command(commands=['start']))
async def start(message: Message, bot: Bot):
    user = await check_user(message.from_user.id)
    if len(message.text) > len('/start'):
        await check_referral(message, bot)
    if user is True:
        user = await check_user_contact(message.from_user.id)
        if user is True:
            await message.answer(
                '<b>Вы уже зарегистрированы</b>',
                reply_markup=short_menu_buttons()
            )
        else:
            await message.answer(
                'Перед использованием бота подписать договор оферты.',
                reply_markup=start_button()
            )
    else:
        await message.answer(
            '<b>Информационное сообщение</b>\nКратное описание сервиса.',
            reply_markup=start_button()
        )


@main_router.callback_query(F.data == 'start_bot')
async def start_bot(call: CallbackQuery):
    await add_user(call.from_user.id, call.from_user.username)
    await update_user_contract(call.from_user.id)
    await call.message.edit_text(
        '<b>Вы зарегистрировались. Доступен бесплатный период на 15 мин.</b>',
        reply_markup=short_menu_buttons()
        )


@main_router.callback_query(F.data == 'back_to_main')
async def get_short_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        'Короткое меню.',
        reply_markup=short_menu_buttons()
    )


@main_router.callback_query(F.data == 'main_menu')
async def get_full_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        'Полное меню.',
        reply_markup=main_menu_buttons()
    )
