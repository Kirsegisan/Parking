import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from handlers.main import main_router
from handlers.find_object import find_object_router
from handlers.edit_addresses import edit_addresses_router
from handlers.pay_service import pay_service_router
from handlers.invite_friends import invite_friends_router
from handlers.feedback import feedback_router
from middlewares.subscription import (
    SubscriptionMiddleware, check_subscription_users)
from utils.users_db import create_users_db
from utils.subscriptions_db import create_subscriptions_db
from utils.refer_db import create_refer_db
from settings import ADMIN_ID, BOT_TOKEN


async def on_startup(bot: Bot):
    await bot.send_message(ADMIN_ID, text='Бот запущен.')


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()
    await bot.send_message(ADMIN_ID, text='Бот остановлен.')
    for task in asyncio.all_tasks():
        if task is not asyncio.current_task():
            task.cancel()


async def start():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
    dp = Dispatcher()
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.callback_query.middleware(SubscriptionMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.include_router(main_router)
    dp.include_router(find_object_router)
    dp.include_router(edit_addresses_router)
    dp.include_router(pay_service_router)
    dp.include_router(invite_friends_router)
    dp.include_router(feedback_router)
    await create_users_db()
    await create_subscriptions_db()
    await create_refer_db()
    asyncio.create_task(check_subscription_users())
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    logger = logging.getLogger(__name__)
    asyncio.run(start())
