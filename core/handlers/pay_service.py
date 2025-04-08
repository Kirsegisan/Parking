import logging
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import PAYMENTS
from keyboards.main_kb import back_to_main_kb
from keyboards.pay_service_kb import pay_service_kb
from utils.users_db import get_user_expired_date, set_user_expired_date
from utils.subscriptions_db import record_subscription


logger = logging.getLogger(__name__)

pay_service_router = Router()


@pay_service_router.callback_query(F.data == 'pay_service')
async def pay_service(call: CallbackQuery, state: FSMContext):
    expired_date = await get_user_expired_date(call.from_user.id)
    await state.update_data(expired_date=expired_date)
    message_date = datetime.fromisoformat(expired_date)
    if expired_date:
        message = (
            'У вас активная подписка до '
            f'{message_date.strftime("%d/%m/%Y %H:%M")}'
        )
    else:
        message = 'У вас нет активной подписки'
    await call.message.edit_text(message, reply_markup=pay_service_kb())


@pay_service_router.callback_query(F.data.startswith('pay_'))
async def pay(call: CallbackQuery, state: FSMContext):
    subscription_cost = call.data.split('_')[1]
    expired_date = await get_user_expired_date(call.from_user.id)
    expired_date_obj = datetime.strptime(expired_date, '%Y-%m-%d %H:%M:%S.%f')
    new_expired_date = expired_date_obj + timedelta(
        days=PAYMENTS[subscription_cost])
    await set_user_expired_date(call.from_user.id, new_expired_date)
    await record_subscription(
        call.from_user.id,
        datetime.now(),
        subscription_cost,
        PAYMENTS[subscription_cost]
    )
    logger.info(f'Пользователь {call.from_user.id} оплатил подписку')
    await call.answer(
        'Тут должна быть интеграция платежного сервиса',
        show_alert=True)
    await call.message.edit_text(
        '<b>Оплата прошла успешно.</b>\n'
        f'Новая дата окончания подписки {new_expired_date}',
        reply_markup=back_to_main_kb()
    )
    await state.clear()
