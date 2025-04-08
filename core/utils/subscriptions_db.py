import logging

import aiosqlite

logger = logging.getLogger(__name__)


async def create_subscriptions_db():
    """Создает базу данных подписок.
    user_id - идентификатор пользователя.
    payment_date - дата оплаты.
    amount - сумма оплаты.
    days - количество дней подписки.
    """
    async with aiosqlite.connect('core/databases/subscriptions.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscriptions (
                user_id INTEGER,
                payment_date TEXT,
                amount INTEGER,
                days INTEGER
            )
        ''')
        logger.info('База подписок успешно создана.')
        await db.commit()


async def record_subscription(
        user_id: int, payment_date: str, amount: int, days: int):
    """Записывает информацию о подписке пользователя.
    user_id - идентификатор пользователя.
    payment_date - дата оплаты.
    amount - сумма оплаты.
    days - количество дней подписки.
    """
    async with aiosqlite.connect('core/databases/subscriptions.db') as db:
        await db.execute('''
            INSERT INTO subscriptions (user_id, payment_date, amount, days)
            VALUES (?, ?, ?, ?)
        ''', (user_id, payment_date, amount, days))
        logger.info(
            f'Запись о подписке пользователя {user_id} успешно создана.')
        await db.commit()
