import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards.main_kb import back_to_main_kb

invite_friends_router = Router()
logger = logging.getLogger(__name__)


def invite_friends_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text='Пригласить друзей', callback_data='gen_link')
    return kb.as_markup()


@invite_friends_router.callback_query(F.data == 'invite_friends')
async def invite_friends(call: CallbackQuery):
    await call.message.edit_text(
        'Пригласи 5 друзей, и получи 1 месяц пользования сервисом БЕСПЛАТНО!',
        reply_markup=invite_friends_keyboard()
    )


@invite_friends_router.callback_query(F.data == 'gen_link')
async def gen_link(call: CallbackQuery):
    await call.message.edit_text(
        'Ссылка для приглашения друзей: '
        f'https://t.me/CardayTestBot?start={call.from_user.id}',
        reply_markup=back_to_main_kb()
    )
