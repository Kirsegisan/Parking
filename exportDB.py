import sqlite3
from openpyxl import Workbook


def export_sqlite_to_xlsx(db_files, output_file):
    # Создаем новую книгу Excel
    wb = Workbook()
    # Удаляем дефолтный лист (он создается автоматически)
    wb.remove(wb.active)

    for db_file in db_files:
        # Подключаемся к SQLite-базе
        conn = sqlite3.connect('core/databases/' + db_file)
        cursor = conn.cursor()

        # Получаем список всех таблиц в базе
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            # Создаем лист с именем в формате "dbname_tablename"
            sheet_name = f"{db_file.replace('.db', '')}_{table_name}"
            # Ограничиваем длину названия листа (Excel допускает max 31 символ)
            sheet_name = sheet_name[:31]
            ws = wb.create_sheet(title=sheet_name)

            # Получаем данные из таблицы
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            # Получаем названия столбцов
            column_names = [description[0] for description in cursor.description]

            # Записываем заголовки
            ws.append(column_names)

            # Записываем данные
            for row in rows:
                ws.append(row)

        # Закрываем соединение с текущей базой
        conn.close()

    # Сохраняем Excel-файл
    wb.save(output_file)
    print(f"Данные успешно экспортированы в {output_file}")


# Список баз данных для экспорта
db_files = ['referrals.db', 'subscriptions.db', 'users.db']
# Название выходного файла
output_file = 'exported_data.xlsx'

# Запускаем экспорт
# export_sqlite_to_xlsx(db_files, output_file)