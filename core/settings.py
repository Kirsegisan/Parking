import locale
import conetcToCamerasDataBase

ADMIN_ID = 593336868
BOT_TOKEN = '8161606621:AAEgyqWO5QDWMMnstjnB17cvpSaL7HPsOS4'
BOT_TOKEN = '7877206090:AAGpKyAWoRHCMVTwvixExjbMiR9zOuXtb9w'
# BOT_TOKEN = '8029805048:AAEWVQF42sFqF3Wzf--Bf6u43WS6mXMamgs'


locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')

ADDRESSES = conetcToCamerasDataBase.getAddresses()

# ADDRESSES = dict(sorted(
#     ALL_ADDRESSES.items(), key=lambda item: locale.strxfrm(item[0]))
# )

PAYMENTS = {  # Ключ - сумма. Значение - количество дней
    '5': 5,
    '10': 10,
    '15': 15,
    '100': 30,
    '200': 60,
    '300': 90,
}

YOOKASSA_SHOP_ID = "1075018"  # Например 123456
YOOKASSA_SECRET_KEY = "test_Xq9NQyenjvGZQcJkdVrixWKuush9D3qu7s40KCXqSAk"   # Или test_ключ для тестов
