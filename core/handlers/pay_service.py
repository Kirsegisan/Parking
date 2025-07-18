import logging
from datetime import datetime, timedelta
import asyncio

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from settings import PAYMENTS
from yookassa import Payment
from keyboards.main_kb import back_to_main_kb, payment_check_kb
from keyboards.pay_service_kb import pay_service_kb
from settings import YOOKASSA_SHOP_ID, YOOKASSA_SECRET_KEY
from yookassa import Configuration
from utils.users_db import get_user_expired_date, set_user_expired_date
from utils.subscriptions_db import record_subscription

Configuration.account_id = YOOKASSA_SHOP_ID
Configuration.secret_key = YOOKASSA_SECRET_KEY

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
async def create_payment(call: CallbackQuery, state: FSMContext):
    amount = call.data.split('_')[1]
    payment = Payment.create({
        "amount": {"value": amount, "currency": "RUB"},
        "capture": True,
        "confirmation": {"type": "redirect", "return_url": "https://t.me/your_bot"},
        "description": f"Подписка на {PAYMENTS[amount]} дней",
        "metadata": {"user_id": call.from_user.id}
    })

    await state.update_data(payment_id=payment.id, amount=amount)
    await call.message.edit_text(
        f"Оплатите {amount} руб: {payment.confirmation.confirmation_url}",
        show_alert=True,
        reply_markup=payment_check_kb()
    )


@pay_service_router.callback_query(F.data == 'check_payment')
async def verify_payment(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    subscription_cost = data['amount']
    payment = Payment.find_one(data['payment_id'])
    print(f"Данные state: {await state.get_data()}")  # Проверьте, есть ли payment_id
    print(f"Платеж: {payment.status}")  # Что возвращает ЮKassa?
    logger.info(f'Пользователь {call.from_user.id} оплатил подписку')
    if payment.status == 'succeeded':
        await record_subscription(
            call.from_user.id,
            datetime.now(),
            subscription_cost,
            PAYMENTS[subscription_cost]
        )
        old_date = await get_user_expired_date(call.from_user.id)
        if old_date:
            new_date = (datetime.strptime(await get_user_expired_date(call.from_user.id), "%Y-%m-%d %H:%M:%S.%f") + timedelta(minutes=PAYMENTS[data['amount']]))
        else:
            new_date = (datetime.now() + timedelta(minutes=PAYMENTS[data['amount']]))
        await set_user_expired_date(call.from_user.id, new_date)
        await call.message.edit_text(
            f"✅ Подписка активна до {new_date}",
            reply_markup=back_to_main_kb()
        )
    else:
        await call.answer("Платеж не найден", show_alert=True)

    await state.update_data(payment_id=payment.id)
