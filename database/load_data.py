import pandas as pd


def load_fmi_numbers_in_db(table_data):
    """Загрузка FMI кодов в базу данных."""

    print('FMI коды найдены')
    # print(table_data)


def load_code_error_in_db(table_data):
    """Загрузка кодов ошибок в базу данных."""

    print('code_error найдены')
    # print(table_data)


def load_data():
    """Загрузка данных из exce в базу данных."""

    df = pd.ExcelFile(
        'database/data/engine_error_codes.xlsx',
        )
    for sheet_name in df.sheet_names:
        table_data = df.parse(sheet_name)
        if str(sheet_name).lower() == 'fmi':
            load_fmi_numbers_in_db(table_data)
            continue

        load_code_error_in_db(table_data)


if __name__ == '__main__':
    load_data()
