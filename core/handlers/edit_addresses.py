import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from settings import ADDRESSES
from keyboards.main_kb import (
    add_address_button, short_menu_buttons, edit_address_button)
from utils.users_db import (
    get_user_addresses, save_user_address, delete_user_address)


edit_addresses_router = Router()
logger = logging.getLogger(__name__)


class AddAddressState(StatesGroup):
    waiting_for_address_name = State()
    waiting_approve_address = State()


@edit_addresses_router.callback_query(
    F.data.in_(['edit_addresses', 'back_to_addresses', 'cancel_address']))
async def edit_addresses(call: CallbackQuery, state: FSMContext):
    await state.clear()
    added_addresses = await get_user_addresses(call.from_user.id)
    add_mark = ''
    kb = InlineKeyboardBuilder()
    for address in ADDRESSES.keys():
        if address in added_addresses.keys():
            add_mark = '✅'
        else:
            add_mark = ''
        kb.button(text='{} {}'.format(add_mark, address),
                  callback_data=f'{address}')
    kb.button(text='⬅️ В главное меню', callback_data='back_to_main')
    kb.adjust(1)
    await call.message.edit_text(
        'Список доступных адресов:',
        reply_markup=kb.as_markup())


@edit_addresses_router.callback_query(F.data.in_(ADDRESSES.keys()))
async def add_address(call: CallbackQuery, state: FSMContext):
    added_addresses = await get_user_addresses(call.from_user.id)
    address = call.data
    await state.update_data(choosed_address=address)
    if address in added_addresses.keys():
        await call.message.edit_text(
            f'<b>Адрес {address} уже добавлен</b>\n',
            reply_markup=edit_address_button()
        )
        return
    await call.message.edit_text(
        f'<b>Вы выбрали адрес {address}</b>\n'
        'Введите ниже псевдоним выбранного адреса, он будет использоваться в '
        'поиске объектов',
    )
    await state.set_state(AddAddressState.waiting_for_address_name)


@edit_addresses_router.message(AddAddressState.waiting_for_address_name)
async def add_address_name(message: Message, state: FSMContext):
    data = await state.get_data()
    address = data['choosed_address']
    address_name = message.text
    await state.update_data(address_name=address_name)
    await message.answer(
        f'<b>Для адреса:</b> {address}\n'
        f'<b>Вы установили псевдоним:</b> {message.text}',
        reply_markup=add_address_button()
    )
    await state.set_state(AddAddressState.waiting_approve_address)


@edit_addresses_router.callback_query(F.data == 'confirm_address')
async def confirm_address(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    address = data['choosed_address']
    address_name = data['address_name']
    await save_user_address(call.from_user.id, address, address_name)
    await call.message.edit_text(
        f'<b>Адрес: {address} с названием {address_name} добавлен в '
        'список.</b>',
        reply_markup=short_menu_buttons()
    )
    await state.clear()


@edit_addresses_router.callback_query(F.data == 'delete_address')
async def delete_address(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    address = data['choosed_address']
    await delete_user_address(call.from_user.id, address)
    await call.message.edit_text(
        f'<b>Адрес: {address} удален из списка.</b>',
        reply_markup=short_menu_buttons()
    )
    await state.clear()
