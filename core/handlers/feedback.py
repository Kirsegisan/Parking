import logging

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from settings import ADMIN_ID

feedback_router = Router()
logger = logging.getLogger(__name__)


def back_to_main_kb():
    kb = InlineKeyboardBuilder()
    kb.button(text='В главное меню', callback_data='back_to_main')
    return kb.as_markup()


class FeedbackState(StatesGroup):
    feedback = State()


@feedback_router.callback_query(F.data == 'feedback')
async def feedback(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text(
        'Можете связаться с нами по номеру +79999999999\n'
        'Либо оставьте своё сообщение ниже:',
        reply_markup=back_to_main_kb())
    await state.set_state(FeedbackState.feedback)


@feedback_router.message(FeedbackState.feedback)
async def feedback_message(message: Message, bot: Bot, state: FSMContext):
    try:
        await bot.forward_message(
            chat_id=ADMIN_ID,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        await message.answer(
            '✅ Ваше сообщение переслано администратору')
    except Exception as e:
        await message.answer(
            '⚠️ Не удалось отправить сообщение администратору')
        logger.error(f'Ошибка пересылки: {e}')
    await state.clear()
