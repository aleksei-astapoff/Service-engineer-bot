import os
import aiohttp
import aiofiles

from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from database.models_client import Order, Client, Photo
from constant import MEDIA_ROOT_DIR
from utils import bot_telegram
from dotenv import load_dotenv

load_dotenv()


async def ensure_dir(derictory: str):
    """Проверка существования директории."""
    if not os.path.exists(derictory):
        os.makedirs(derictory)


async def save_photos(photos, client_id, order_id, address_machine):
    """Сохранение фотографий в директории."""
    image_paths = {}
    client_dir = os.path.join(MEDIA_ROOT_DIR, str(client_id))
    order_dir = os.path.join(client_dir, str(order_id))

    await ensure_dir(order_dir)

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
                        filename = f"{address_machine}_photo_{index}.jpg"
                        filepath = os.path.join(order_dir, filename)
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
    return image_paths, order_dir


async def session_save_client(session: AsyncSession, client: Client):
    """Сохранение клиента в базу данных."""

    session.add(client)
    await session.commit()
    await session.refresh(client)


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
            await session_save_client(session, client)

    except NoResultFound:
        client = Client(telegram_profile_id=telegram_profile_id, **kwargs)
        await session_save_client(session, client)

    return client


async def orm_add_order(session: AsyncSession, data: dict):
    """Добавление заявки в базу данных."""

    client = await get_or_create_client(
        session,
        telegram_profile_id=int(data['telegram_profile_id']),
        full_name=f'{data["fist_name"]} {data["last_name"]}',
        user_name=data['telegram_profile_username'],
        phone_number=data['phone_number']
    )

    order = Order(
        client_id=client.id,
        type_service=data['type_service'],
        type_machine=data['type_machine'],
        model_machine=data['model_machine'],
        serial_number=data['serial_number'],
        image='Нет изображений',
        address_machine=data['address_machine'],
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)

    if data.get('image') is not None:
        photos = data['image']
        image_paths, order_dir = await save_photos(
            photos, client.id, order.id, order.address_machine
            )
        order_dir_str = (
            order_dir + '/ Загружено фото: ' + str(len(image_paths))
            )

        order.image = order_dir_str
        session.add(order)

        for image_path, photo_id in image_paths.items():
            photo = Photo(
                order_id=order.id, file_path=image_path, photo_id=photo_id
                )
            session.add(photo)

    await session.commit()
