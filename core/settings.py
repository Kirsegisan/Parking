import locale
import conetcToCamerasDataBase

ADMIN_ID = 1974355978
BOT_TOKEN = '7962713583:AAEZOrcnhpT1vER-5aAmywxim3qQ7NsrtLY'

locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')

ADDRESSES = conetcToCamerasDataBase.getAddresses()

# ADDRESSES = dict(sorted(
#     ALL_ADDRESSES.items(), key=lambda item: locale.strxfrm(item[0]))
# )

PAYMENTS = {  # Ключ - сумма. Значение - количество дней
    '100': 30,
    '200': 60,
    '300': 90,
}

YOOKASSA_SHOP_ID = "123456"  # Например 123456
YOOKASSA_SECRET_KEY = "test_ваш_тестовый_ключ"   # Или test_ключ для тестов
