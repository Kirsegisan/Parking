from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os

from keyboards.main_kb import short_menu_buttons
from settings import ADDRESSES
from utils.users_db import get_user_addresses

import conetcToCamerasDataBase
import cv2
from io import BytesIO
from aiogram import types
import numpy as np

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
    await call.message.edit_text("Сейчас посмотрим")
    try:
        detect_results = conetcToCamerasDataBase.detAnalysisAddresses(select)
        for detect_result in detect_results:
            await send_cv2_image_as_photo(
                call.message,
                detect_result[0],
                caption=f'Вы выбрали объект {detect_result[4]}'
            )

    except Exception as e:
        print(f"Ошибка при поиске объекта: {e}")  # Вывод в терминал
        await call.message.answer(
            'Ошибка поиска объекта',
            reply_markup=short_menu_buttons()
        )
        return
    await call.message.answer(
                'Выберите действие.',
                reply_markup=short_menu_buttons()
            )


async def send_cv2_image_as_photo(
        message: types.Message,
        cv2_image: np.ndarray,  # Изображение в формате OpenCV (numpy array)
        caption: str = ""
):
    # Конвертируем изображение в формат, который понимает Telegram (JPEG или PNG)
    _, buffer = cv2.imencode('.png', cv2_image)  # Можно также использовать '.jpg'

    # Создаем файловый объект в памяти
    image_bytes = BytesIO(buffer.tobytes())
    image_bytes.seek(0)  # Перемещаем указатель в начало

    # Создаем BufferedInputFile (специальный тип для aiogram 3.x)
    input_file = BufferedInputFile(file=image_bytes.read(), filename="image.png")

    # Отправляем фото
    await message.answer_photo(
        photo=input_file,
        caption=caption
    )
