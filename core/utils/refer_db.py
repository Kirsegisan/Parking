from datetime import datetime, timedelta

from aiogram import Bot
import aiosqlite
from aiogram.types import Message


async def create_refer_db():
    """Создает базу данных рефералов.
    referrer_id: идентификатор реферера
    referral_id: идентификатор реферала
    referral_date: дата реферала
    activated: активирован ли реферал
    bonus_activated: активирован ли бонус
    """
    async with aiosqlite.connect("core/databases/referrals.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS referrals (
                referrer_id INTEGER NOT NULL,
                referral_id INTEGER PRIMARY KEY,
                referral_date TEXT NOT NULL,
                activated BOOLEAN DEFAULT FALSE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS bonus_status (
                user_id INTEGER PRIMARY KEY,
                completed_referrals INTEGER DEFAULT 0,
                bonus_activated BOOLEAN DEFAULT FALSE
            )
        """)
        await db.commit()


async def check_referral(message: Message, bot: Bot):
    """Проверяет, является ли сообщение реферальным.
    message: сообщение
    bot: бот
    """
    async with aiosqlite.connect("core/databases/referrals.db") as db:
        get_id = message.text.split(' ')[1]
        referrer_id = int(get_id)

        cursor = await db.execute(
            "SELECT 1 FROM referrals WHERE referral_id = ?",
            (message.from_user.id,)
        )
        exists = await cursor.fetchone()

        if not exists:
            await db.execute(
                "INSERT INTO referrals VALUES (?, ?, ?, ?)",
                (referrer_id, message.from_user.id, datetime.now().isoformat(),
                 False)
            )
            await db.commit()

            await update_referral_count(referrer_id, bot)


async def update_referral_count(referrer_id: int, bot: Bot):
    """
    Обновляет количество активированных рефералов.
    referrer_id: идентификатор реферера
    bot: бот
    """
    async with aiosqlite.connect("core/databases/referrals.db") as db:

        cursor = await db.execute("""
            SELECT COUNT(*)
            FROM referrals
            WHERE referrer_id = ? AND activated = FALSE
            """, (referrer_id,)
        )
        active_count = (await cursor.fetchone())[0]

        if active_count >= 1:
            await db.execute("""
                UPDATE referrals
                SET activated = TRUE
                WHERE referrer_id = ? AND activated = FALSE
                """, (referrer_id,)
            )

            cursor = await db.execute(
                "SELECT bonus_activated FROM bonus_status WHERE user_id = ?",
                (referrer_id,)
            )
            status = await cursor.fetchone()

            if not status or not status[0]:
                await apply_subscription_bonus(referrer_id, bot)
                await db.execute(
                    "INSERT OR REPLACE INTO bonus_status VALUES (?, ?, ?)",
                    (referrer_id, active_count, True)
                )

        await db.commit()


async def apply_subscription_bonus(user_id: int, bot: Bot):
    """
    Применяет бонус подписки.
    user_id: идентификатор пользователя
    bot: бот
    """
    async with aiosqlite.connect("core/databases/users.db") as db:

        cursor = await db.execute(
            "SELECT expired_date FROM users WHERE user_id = ?",
            (user_id,)
        )
        current_expiry = await cursor.fetchone()

        new_expiry = (datetime.now() + timedelta(days=30)).date()

        if current_expiry and current_expiry[0]:
            current_date = datetime.strptime(
                current_expiry[0], "%Y-%m-%d %H:%M:%S.%f")
            new_expiry = (current_date + timedelta(days=30))

        await db.execute("""
            UPDATE users
            SET subscription = 'paid',
            expired_date = ? WHERE user_id = ?
            """, (new_expiry, user_id)
        )
        await db.commit()

    await bot.send_message(
        user_id,
        "🎉 Вы получили 1 месяц подписки за приглашение 5 друзей!"
    )
