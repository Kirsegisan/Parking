import locale

ADMIN_ID = [123123123, 321321321]
BOT_TOKEN = '5285866637:AAE-EbkvJJd_p4gaX9Z8x2n7R42NXRmCSkA'

locale.setlocale(locale.LC_COLLATE, 'ru_RU.UTF-8')

ALL_ADDRESSES = {  # Ключ - адрес. Значение - путь до фотографии
    'Казань, ул. Пушкина, д. 1': 'core/photos/kazan.jpg',
    'Москва, ул. Ленина, д. 1': 'core/photos/moscow.jpg',
    'Санкт-Петербург, ул. Пушкина, д. 2': 'core/photos/spb.jpg',
    'Астрахань, ул. Гагарина, д. 3': 'core/photos/astra.jpg',
}

ADDRESSES = dict(sorted(
    ALL_ADDRESSES.items(), key=lambda item: locale.strxfrm(item[0]))
)

PAYMENTS = {  # Ключ - сумма. Значение - количество дней
    '100': 30,
    '200': 60,
    '300': 90,
}
