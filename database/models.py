from ast import List

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    date_creation = mapped_column(Date, nullable=False)
    client_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('clients.id'), nullable=False
        ),

    address: Mapped[str] = mapped_column(String(150), nullable=False)
    type_service: Mapped[str] = mapped_column(String(50), nullable=False)
    type_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    model_machine: Mapped[str] = mapped_column(String(50), nullable=False)
    serial_number: Mapped[str] = mapped_column(String(50), nullable=False)
    image: Mapped[str] = mapped_column(List(), nullable=True)

    client = relationship(
        "Client",
        back_populates="orders"
    )


class Client(Base):
    __tablename__ = 'clients'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_profile_id: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=True)
    user_name: Mapped[str] = mapped_column(String(150), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(11), nullable=True)

    orders = relationship("Order", back_populates="client")
