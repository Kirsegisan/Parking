import locale
import conetcToCamerasDataBase

ADMIN_ID = 1974355978
BOT_TOKEN = '8040038186:AAFIDi_MVmZfT6EWHUON37OCQQiphnDqr5o'
# BOT_TOKEN = '8029805048:AAEWVQF42sFqF3Wzf--Bf6u43WS6mXMamgs'


locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')

ADDRESSES = conetcToCamerasDataBase.getAddresses()

# ADDRESSES = dict(sorted(
#     ALL_ADDRESSES.items(), key=lambda item: locale.strxfrm(item[0]))
# )

PAYMENTS = {  # Ключ - сумма. Значение - количество дней
    '5': 0.00347,
    '10': 0.00694444445,
    '15': 0.01041,
    '100': 30,
    '200': 60,
    '300': 90,
}

YOOKASSA_SHOP_ID = "1075018"  # Например 123456
YOOKASSA_SECRET_KEY = "test_Xq9NQyenjvGZQcJkdVrixWKuush9D3qu7s40KCXqSAk"   # Или test_ключ для тестов
