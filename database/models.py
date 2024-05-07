from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseClient(DeclarativeBase):
    """Базовая модель базы данных, заказы клиентов."""

    creation: Mapped[Date] = mapped_column(DateTime(), default=func.now())


class Order(BaseClient):
    """Модель базы данных, заказы клиентов."""

    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clients.id'), nullable=False
        )

    address: Mapped[str] = mapped_column(String(150), nullable=False)
    type_service: Mapped[str] = mapped_column(String(50), nullable=False)
    type_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    model_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(50), nullable=False)
    image: Mapped[str] = mapped_column(String(250))

    client = relationship(
        "Client",
        back_populates="orders"
    )


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
