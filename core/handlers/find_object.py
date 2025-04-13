from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.main_kb import short_menu_buttons
from settings import ADDRESSES
from utils.users_db import get_user_addresses

import conetcToCamerasDataBase
import cv2

find_object_router = Router()


@find_object_router.callback_query(F.data == 'find_object')
async def find_object(call: CallbackQuery):
    addresses = await get_user_addresses(call.from_user.id)
    if addresses:
        kb = InlineKeyboardBuilder()
        for address, address_name in addresses.items():
            kb.button(text=address_name, callback_data=f'info_{address}')
        kb.adjust(1)
        await call.message.edit_text(
            'Выберите объект из списка',
            reply_markup=kb.as_markup())
    else:
        await call.answer(
            'Список своих адресов, где вы можете пользоваться услугой, '
            'пока пуст. Чтобы добавить свои адреса перейдите в раздел '
            'Главного Меню "Редактировать свои адреса."',
            show_alert=True
        )


@find_object_router.callback_query(F.data.startswith('info_'))
async def select_object(call: CallbackQuery):
    select = call.data.split('_')[1]
    detect_result = conetcToCamerasDataBase.detAnalysisAddresses(select)
    cv2.imwrite('./image_test_free.png', detect_result[0])
    await call.message.answer_photo(
        FSInputFile('./image_test_free.png'),
        caption=f'Вы выбрали объект {select}'
    )
    await call.message.answer(
        'Выберите действие.',
        reply_markup=short_menu_buttons()
    )