import logging

from aiogram import Bot, types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import aiosqlite
import asyncio

from keyboards.pay_service_kb import pay_service_kb
from utils.users_db import check_expired_subscriptions

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if not isinstance(event, types.CallbackQuery):
            return await handler(event, data)
        if event.data.startswith("pay_"):
            return await handler(event, data)
        user_id = event.from_user.id
        bot: Bot = data["bot"]

        async with aiosqlite.connect("core/databases/users.db") as db:
            cursor = await db.execute("""
                SELECT subscription, expired_date
                FROM users
                WHERE user_id = ?
                """, (user_id,),
            )
            user_data = await cursor.fetchone()
        if user_data and not user_data[0] in ['free', 'paid']:
            await event.answer(
                "❌ Ваша подписка истекла. Пожалуйста, продлите её.",
                show_alert=True,
            )
            await bot.send_message(
                user_id,
                'Продлите подписку.',
                reply_markup=pay_service_kb()
            )
            return
        return await handler(event, data)


async def check_subscription_users():
    try:
        while True:
            await check_expired_subscriptions()
            await asyncio.sleep(86400)
    except Exception as e:
        logger.error(f"Ошибка в check_inactive_users: {e}")
