import pandas as pd

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.engine import session_maker
from database.models_worker import FmiNumber


async def load_fmi_numbers_in_db(table_data, session: AsyncSession):
    """Загрузка FMI кодов в базу данных."""

    print('FMI коды найдены')
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


async def load_data():
    """Загрузка данных из exce в базу данных."""

    df = pd.ExcelFile(
        'database/data/engine_error_codes.xlsx',
        )
    session: AsyncSession = session_maker()
    for sheet_name in df.sheet_names:
        table_data = df.parse(sheet_name)
        if str(sheet_name).lower() == 'fmi':
            await load_fmi_numbers_in_db(table_data, session)
            continue

        await load_code_error_in_db(table_data, session)
