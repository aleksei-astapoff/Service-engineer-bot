import os
import aiohttp
import aiofiles

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from database.models_client import Order, Client, Photo, Machine
from constant import MEDIA_ROOT_DIR
from utils import bot_telegram
from dotenv import load_dotenv

load_dotenv()


async def ensure_dir(derictory: str):
    """Проверка существования директории."""
    if not os.path.exists(derictory):
        os.makedirs(derictory)


async def save_photos(photos, machine, client, address_service):
    """Сохранение фотографий в директории."""
    image_paths = {}
    client_dir = os.path.join(MEDIA_ROOT_DIR, str(
        client.full_name if client.full_name else client.user_name
        ))
    machine_dir = os.path.join(client_dir, str(machine.serial_number))

    await ensure_dir(machine_dir)

    async with aiohttp.ClientSession() as session:
        for index, photo_id in enumerate(photos, start=1):
            try:
                file_info = await bot_telegram.get_file(photo_id)
                file_path = (
                        'https://api.telegram.org/file/bot'
                        + os.getenv("BOT_TOKEN") +
                        '/' + file_info.file_path
                    )
                async with session.get(file_path) as response:
                    if response.status == 200:
                        filename = f"{address_service}_photo_{index}.jpg"
                        filepath = os.path.join(machine_dir, filename)
                        async with aiofiles.open(filepath, 'wb') as file:
                            content = await response.read()
                            await file.write(content)
                        image_paths[filepath] = photo_id
                    else:
                        print(
                            'Ошибка загрузки сервера, фото: '
                            + photo_id + 'код статуса HTTP: '
                            + response.status)
            except Exception as exc:
                print(f"Ошибка загрузки фото {photo_id}: {exc}")
    return image_paths, machine_dir


async def session_save(session: AsyncSession, object):
    """Сохранение клиента в базу данных."""

    session.add(object)
    await session.commit()
    await session.refresh(object)


async def get_or_create_client(
        session: AsyncSession, telegram_profile_id: int, **kwargs
        ):
    """Получение или создание клиента в базе данных."""
    try:
        result = await session.execute(
            select(Client).where(
                Client.telegram_profile_id == telegram_profile_id
                )
            )
        client = result.scalar_one()

        updated = False
        for key, value in kwargs.items():
            if getattr(client, key) != value:
                setattr(client, key, value)
                updated = True

        if updated:
            await session_save(session, client)

    except NoResultFound:
        client = Client(telegram_profile_id=telegram_profile_id, **kwargs)
        await session_save(session, client)

    return client


async def get_or_create_machine(
        session: AsyncSession, client_id: int, **kwargs
        ):
    """Получение или создание оборудования в базе данных."""
    try:
        result = await session.execute(
            select(Machine).where(
                Machine.client_id == client_id,
                Machine.serial_number == kwargs['serial_number']
                )
            )
        machine = result.scalar_one()

    except NoResultFound:
        machine = Machine(client_id=client_id, **kwargs)
        await session_save(session, machine)

    return machine


async def orm_add_order(session: AsyncSession, data: dict):
    """Добавление заявки в базу данных."""
    if data.get('client') is None:
        client = await get_or_create_client(
            session,
            telegram_profile_id=int(data['telegram_profile_id']),
            full_name=f'{data["fist_name"]} {data["last_name"]}',
            user_name=data['telegram_profile_username'],
            phone_number=data['phone_number']
        )
    else:
        client = data['client']
    if data.get('machines_by_client') is None:
        machine = await get_or_create_machine(
            session,
            client_id=client.id,
            type_machine=data['type_machine'],
            model_machine=data['model_machine'],
            serial_number=data['serial_number'],
            address_machine=data['address_service'],
            images='Нет изображений',
        )
    else:
        machine = data['machines_by_client']

    order = Order(
        machine_id=machine.id,
        type_service=data['type_service'],
        address_service=machine.address_machine,
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)

    if data.get('image') is not None:
        photos = data['image']
        image_paths, machine_dir = await save_photos(
            photos, machine, client, order.address_service
            )
        machine_dir_str = (
            machine_dir + '/ Загружено фото: ' + str(len(image_paths))
            )

        machine.images = machine_dir_str
        session.add(machine)

        for image_path, photo_id in image_paths.items():
            photo = Photo(
                machine_id=machine.id, file_path=image_path, photo_id=photo_id
                )
            session.add(photo)

    await session.commit()

    return order.id


async def get_client_by_id(session: AsyncSession, telegram_profile_id: int):
    """Получение клиента по ID."""
    result = await session.execute(
        select(Client).where(Client.telegram_profile_id == telegram_profile_id)
    )
    return result.scalar_one_or_none()


async def get_client_machines(session: AsyncSession, client):
    """Получение заявки по клиенту."""
    result = await session.execute(
        select(Machine).where(Machine.client_id == client.id)
    )
    return result.scalars().all()
