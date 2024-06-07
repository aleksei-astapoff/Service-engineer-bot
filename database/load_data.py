import pandas as pd

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import session_maker
from database.models_worker import (FmiNumber, TupeEquipment,
                                    ProducerEquipment,
                                    ModelEquipment, CodeError)

DICT_WORKER = {
    'type_equipment': TupeEquipment,
    'producer_equipment': ProducerEquipment,
    'model_equipment': ModelEquipment,
}


async def get_or_create_object_in_db(
        dict_value, row, column, session: AsyncSession
        ):
    """Получение или создание объекта в базе данных."""

    if len(dict_value) != 0:
        related_data = dict_value.popitem()
        related_data = {related_data[1]: related_data[0]}
    else:
        related_data = None
    model_class = DICT_WORKER[column]
    values = [value for value in str(getattr(row, column)).split(', ')]

    for value_ in values:
        result = (await session.execute(
            select(model_class).filter_by(**{column: value_})
        )).scalars().first()

        if not result:
            if related_data:
                result = model_class(**{column: value_}, **related_data)
            else:
                result = model_class(**{column: value_})
            session.add(result)
            await session.commit()
        dict_value[result.id] = column + '_id'
    return dict_value


async def load_fmi_numbers_in_db(table_data, session: AsyncSession):
    """Загрузка FMI кодов в базу данных."""

    table_data.columns = ['fmi_number', 'text']
    for row in table_data.itertuples():
        fmi_number = (await session.execute(
            select(FmiNumber).filter_by(
                fmi_number=row.fmi_number,
                )
        )).scalars().first()

        if not fmi_number:
            fmi_number = FmiNumber(
                fmi_number=row.fmi_number,
                text=row.text,
            )
            session.add(fmi_number)
            await session.commit()

            print(f'FMI {row.fmi_number} добавлен')

        if fmi_number.text != row.text:
            fmi_number.text = row.text
            session.add(fmi_number)
            await session.commit()
            print(f'FMI {row.fmi_number} обновлен')


async def load_code_error_in_db(table_data, session: AsyncSession):
    """Загрузка кодов ошибок в базу данных."""

    print('code_error найдены')
    table_data.columns = [
        'type_equipment', 'producer_equipment',
        'model_equipment', 'code_error', 'fmi_number',
        'text_error', 'translation_text_error'
        ]

    for row in table_data.itertuples(index=False):
        dict_value = {}
        for column in row._fields:
            if column in DICT_WORKER.keys():
                await get_or_create_object_in_db(
                    dict_value, row, column, session)
                dict_value = dict_value
            print(dict_value)
        print('Дошли до колонки', column)
        

async def load_data():
    """Загрузка данных из exce в базу данных."""

    df = pd.ExcelFile(
        'database/data/engine_error_codes.xlsx',
        )
    async with session_maker() as session:
        for sheet_name in df.sheet_names:
            table_data = df.parse(sheet_name)
            if str(sheet_name).lower() == 'fmi':
                await load_fmi_numbers_in_db(table_data, session)
                continue

            await load_code_error_in_db(table_data, session)
