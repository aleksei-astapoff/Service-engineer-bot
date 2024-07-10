from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils import current_time


class BaseClient(DeclarativeBase):
    """Базовая модель базы данных, заказы клиентов."""

    __abstract__ = True

    creation: Mapped[Date] = mapped_column(DateTime(), default=current_time)
    # creation: Mapped[Date] = mapped_column(
    # DateTime(timezone=True), server_default=func.timezone('Europe/Moscow', func.now()))


class Machine(BaseClient):
    """Модель базы данных, оборудование."""

    __tablename__ = 'machines'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clients.id'), nullable=False
        )
    type_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    model_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(50), nullable=False)
    address_machine: Mapped[str] = mapped_column(String(150), nullable=False)
    images: Mapped[str] = mapped_column(String(250), nullable=True)

    photos = relationship('Photo', back_populates='machine')

    orders = relationship("Order", back_populates='machine')
    client = relationship("Client", back_populates='machines')

    def __repr__(self):
        return self.serial_number


class Order(BaseClient):
    """Модель базы данных, заказы клиентов."""

    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    machine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('machines.id'), nullable=False
        )
    address_service: Mapped[str] = mapped_column(String(150), nullable=False)
    type_service: Mapped[str] = mapped_column(String(50), nullable=False)

    machine = relationship(
        "Machine",
        back_populates="orders"
    )

    def __repr__(self):
        return self.address_service


class Client(BaseClient):
    """Модель базы данных, клиенты."""

    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_profile_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=True)
    user_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(11), nullable=True)

    machines = relationship("Machine", back_populates="client")

    def __repr__(self) -> str:
        return self.full_name


class Photo(BaseClient):
    """Модель базы данных, фото."""

    __tablename__ = 'photos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    machine_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('machines.id'), nullable=False
        )
    file_path: Mapped[str] = mapped_column(String(250), nullable=False)
    photo_id: Mapped[str] = mapped_column(String(250), nullable=False)

    machine = relationship(
        "Machine",
        back_populates="photos"
    )

    def __repr__(self) -> str:
        return self.file_path
