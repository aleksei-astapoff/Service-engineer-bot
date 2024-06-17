import pandas as pd

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import session_maker
from database.models_worker import (FmiNumber, TupeEquipment,
                                    ProducerEquipment, Gost,
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


async def load_gost_in_db(table_data, session: AsyncSession):
    """Загрузка GOST кодов в базу данных."""

    table_data.columns = ['gost_number', 'gost_shot_name', 'text']
    for row in table_data.itertuples():
        gost = (await session.execute(
            select(Gost).filter_by(
                gost_number=row.gost_number,
                gost_shot_name=row.gost_shot_name
                )
        )).scalars().first()

        if not gost:
            gost = Gost(
                gost_number=row.gost_number,
                gost_shot_name=row.gost_shot_name,
                text=row.text
            )
            session.add(gost)
            await session.commit()

        if gost.text != row.text or gost.gost_shot_name != row.gost_shot_name:
            gost.gost_shot_name = row.gost_shot_name
            gost.text = row.text
            session.add(gost)


async def load_code_error_in_db(table_data, session: AsyncSession):
    """Загрузка кодов ошибок в базу данных."""

    table_data.columns = [
        'type_equipment', 'producer_equipment',
        'model_equipment', 'code_error', 'fmi_number',
        'text_error', 'translation_text_error'
        ]

    for row in table_data.itertuples(index=False):
        dict_value = {}
        for column in row._fields:
            if column in DICT_WORKER.keys():
                dict_value = await get_or_create_object_in_db(
                    dict_value, row, column, session)
            else:
                code_error = (await session.execute(
                    select(CodeError).filter_by(
                        code_error=row.code_error,
                        text_error=row.text_error,
                        translation_text_error=row.translation_text_error,
                    )
                )).scalars().first()

                if not code_error or code_error.text_error != row.text_error:
                    code_error = CodeError(
                        code_error=row.code_error,
                        text_error=row.text_error,
                        translation_text_error=row.translation_text_error,
                    )
                    session.add(code_error)
                    await session.commit()

                await session.refresh(
                    code_error, attribute_names=[
                        'model_equipments', 'fmi_numbers'
                        ]
                    )

                for key, _ in dict_value.items():
                    model_equipment = (await session.execute(
                            select(ModelEquipment).filter_by(id=key)
                            )).scalars().first()
                    if model_equipment not in code_error.model_equipments:
                        code_error.model_equipments.append(model_equipment)
                        await session.commit()

                fmi_numbers = [
                    int(fmi) for fmi in str(row.fmi_number).split(', ')
                    if row.fmi_number and fmi.isdigit()
                    ]
                for fmi in fmi_numbers:
                    fmi_number = (await session.execute(
                        select(FmiNumber).filter_by(fmi_number=fmi)
                    )).scalars().first()
                    if fmi_number not in code_error.fmi_numbers:
                        code_error.fmi_numbers.append(fmi_number)
                        await session.commit()
                break


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

            elif str(sheet_name).lower() == 'гост':
                await load_gost_in_db(table_data, session)
            else:
                await load_code_error_in_db(table_data, session)
