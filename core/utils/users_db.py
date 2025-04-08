import logging
import json
from datetime import datetime, timedelta

import aiosqlite

logger = logging.getLogger(__name__)

FREE_PERIOD = 14


async def create_users_db():
    """Создаёт базу данных пользователей.
    user_id - идентификатор пользователя.
    subscription - подписка пользователя.
    expired_date - дата окончания подписки.
    addresses - адреса пользователя.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                subscription TEXT NOT NULL DEFAULT 'free',
                expired_date TEXT,
                addresses TEXT,
                contract BOOLEAN NOT NULL DEFAULT 0
            )
        ''')
        logger.info('База успешно создана.')
        await db.commit()


async def add_user(user_id: int):
    """Проверяет или добавляет пользователя в базу данных.
    user_id - идентификатор пользователя.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        now = datetime.now()
        expired_date = now + timedelta(days=FREE_PERIOD)
        await db.execute('''
            INSERT INTO users (
                user_id,
                expired_date,
                contract
            ) VALUES (?, ?, ?)''', (user_id, expired_date, 1)
                         )
        await db.commit()
        logger.info(f'Пользователь {user_id} добавлен в базу данных.')
        return None


async def check_user(user_id: int) -> bool:
    """Проверяет пользователя в базе данных.
    user_id - идентификатор пользователя.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute("""
            SELECT *
            FROM users
            WHERE user_id = ?
            """, (user_id,)
        )
        user = await cursor.fetchone()
        if user:
            return True
        else:
            return False


async def check_user_contact(user_id: int) -> bool:
    """Проверяет контакт пользователя в базе данных.
    user_id - идентификатор пользователя.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute("""
            SELECT *
            FROM users
            WHERE user_id = ? AND contract = 1
            """, (user_id,)
        )
        user = await cursor.fetchone()
        if user:
            return True
        else:
            return False


async def update_user_contract(user_id: int, db: aiosqlite.Connection = None):
    """Обновляет contract пользователя на 1 и выдаёт бесплатный период."""
    if not db:
        async with aiosqlite.connect('core/databases/users.db') as db:
            await db.execute("""
                UPDATE users
                SET contract = 1
                WHERE user_id = ?
            """, (user_id,))
            await db.commit()
    else:
        await db.execute("""
            UPDATE users
            SET contract = 1
            WHERE user_id = ?
        """, (user_id,))
        await db.commit()


async def get_user_addresses(user_id: int) -> dict:
    """Получает адреса пользователя.
    user_id - идентификатор пользователя.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT addresses FROM users WHERE user_id = ?', (user_id,)
        )
        result = await cursor.fetchone()
        if result and result[0]:
            addresses = json.loads(result[0])
            return {k: v for k, v in addresses.items()}
        else:
            return {}


async def delete_user_address(user_id: int, address_name: str) -> None:
    """Удаляет адрес пользователя.
    user_id - идентификатор пользователя.
    address_name - название адреса.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT addresses FROM users WHERE user_id = ?', (user_id,)
        )
        result = await cursor.fetchone()
        if result and result[0]:
            addresses = json.loads(result[0])
            del addresses[address_name]
            addresses_json = json.dumps(addresses)
            await db.execute(
                'UPDATE users SET addresses = ? WHERE user_id = ?',
                (addresses_json, user_id)
            )
            await db.commit()


async def save_user_address(
        user_id: int, address_original: str, address_name: str) -> None:
    """Сохраняет адрес пользователя.
    user_id - идентификатор пользователя.
    address_original - оригинальный адрес.
    address_name - название адреса.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT addresses FROM users WHERE user_id = ?', (user_id,)
        )
        result = await cursor.fetchone()
        if result and result[0]:
            addresses = json.loads(result[0])
        else:
            addresses = {}

        addresses[address_original] = address_name
        addresses_json = json.dumps(addresses)

        await db.execute(
            'UPDATE users SET addresses = ? WHERE user_id = ?',
            (addresses_json, user_id)
        )
        await db.commit()


async def get_user_expired_date(user_id: int) -> datetime:
    """Получает дату окончания подписки пользователя.
    user_id - идентификатор пользователя.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        cursor = await db.execute(
            'SELECT expired_date FROM users WHERE user_id = ?', (user_id,)
        )
        result = await cursor.fetchone()
        if result and result[0]:
            return result[0]
        else:
            return None


async def set_user_expired_date(user_id: int, expired_date: datetime) -> None:
    """Устанавливает дату окончания подписки пользователя.
    user_id - идентификатор пользователя.
    expired_date - дата окончания подписки.
    """
    async with aiosqlite.connect('core/databases/users.db') as db:
        await db.execute("""
            UPDATE users
            SET expired_date = ?, subscription = 'paid'
            WHERE user_id = ?""", (expired_date, user_id))
        await db.commit()
        logger.info(
            f'Дата окончания подписки пользователя {user_id} установлена.')


async def check_expired_subscriptions():
    """Проверяет истекшие подписки."""
    async with aiosqlite.connect("core/databases/users.db") as db:
        today = datetime.now().date()

        cursor = await db.execute("""
            SELECT user_id
            FROM users
            WHERE expired_date <= ? AND subscription IS NOT NULL
            """, (today,),
        )

        expired_users = await cursor.fetchall()

        for user_id in expired_users:
            await db.execute("""
                UPDATE users
                SET subscription = NULL,
                expired_date = NULL
                WHERE user_id = ?
                """, (user_id[0],),
            )
        await db.commit()
