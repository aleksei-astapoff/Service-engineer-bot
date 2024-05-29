from sqlalchemy import Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from utils import current_time


class BaseClient(DeclarativeBase):
    """Базовая модель базы данных, заказы клиентов."""

    __abstract__ = True

    creation: Mapped[Date] = mapped_column(DateTime(), default=current_time)


class Order(BaseClient):
    """Модель базы данных, заказы клиентов."""

    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clients.id'), nullable=False
        )

    address_machine: Mapped[str] = mapped_column(String(150), nullable=False)
    type_service: Mapped[str] = mapped_column(String(50), nullable=False)
    type_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    model_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(50), nullable=False)
    image: Mapped[str] = mapped_column(String(250))

    client = relationship(
        "Client",
        back_populates="orders"
    )
    images = relationship('Photo', back_populates='order')


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

    orders = relationship("Order", back_populates="client")

    def __repr__(self) -> str:
        return self.full_name


class Photo(BaseClient):
    """Модель базы данных, фото."""

    __tablename__ = 'photos'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('orders.id'), nullable=False
        )
    file_path = mapped_column(String(250), nullable=False)

    order = relationship(
        "Order",
        back_populates="images"
    )

    def __repr__(self) -> str:
        return self.file_path
