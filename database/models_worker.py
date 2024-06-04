from sqlalchemy import ForeignKey, Integer, String, Text, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class BaseWorker(DeclarativeBase):
    """Базовая модель базы данных, сотрудники."""

    __abstract__ = True


class Gost(BaseWorker):
    """Модель базы данных, ГОСТ."""

    __tablename__ = 'gost'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    gost: Mapped[str] = mapped_column(String(50), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        return self.gost


class TupeEquipment(BaseWorker):
    """Модель базы данных, тип оборудования."""

    __tablename__ = 'tupe_equipment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_equipment: Mapped[str] = mapped_column(String(50), nullable=False)

    model_equipments = relationship(
        "ModelEquipment",
        back_populates="tupe_equipment"
    )

    def __repr__(self) -> str:
        return self.type_equipment


class ProducerEquipment(BaseWorker):
    """Модель базы данных, производитель оборудования."""

    __tablename__ = 'producer_equipment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_equipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('tupe_equipment.id'), nullable=False
    )
    producer_equipment: Mapped[str] = mapped_column(String(50), nullable=False)

    tupe_equipment = relationship(
        "TupeEquipment",
        back_populates="producer_equipments"
    )

    def __repr__(self) -> str:
        return self.producer_equipment


# Таблица для связи "многие ко многим" между ModelEquipment и CodeError
model_equipment_code_error_association = Table(
    'model_equipment_code_error',
    BaseWorker.metadata,
    Column(
        'model_equipment_id', Integer,
        ForeignKey('model_equipment.id'), primary_key=True
        ),
    Column(
        'code_error_id', Integer,
        ForeignKey('code_error.id'), primary_key=True
        )
)


class ModelEquipment(BaseWorker):
    """Модель базы данных, модель оборудования."""

    __tablename__ = 'model_equipment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producer_equipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('producer_equipment.id'), nullable=False
    )
    model_equipment: Mapped[str] = mapped_column(String(50), nullable=False)

    producer_equipment = relationship(
        "ProducerEquipment",
        back_populates="model_equipments"
    )

    code_errors = relationship(
        "CodeError",
        back_populates="model_equipment"
    )

    def __repr__(self) -> str:
        return self.model_equipment


# Таблица для связи "многие ко многим" между CodeError и FmiNumber
code_error_fmi_association = Table(
    'code_error_fmi',
    BaseWorker.metadata,
    Column(
        'code_error_id', Integer,
        ForeignKey('code_error.id'), primary_key=True
        ),
    Column(
        'fmi_number_id', Integer,
        ForeignKey('fmi_number.id'), primary_key=True
        )
)


class CodeError(BaseWorker):
    """Модель базы данных, код ошибки."""

    __tablename__ = 'code_error'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_equipment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('model_equipment.id'), nullable=False
    )
    code_error: Mapped[str] = mapped_column(String(50), nullable=False)
    text_error: Mapped[str] = mapped_column(Text, nullable=False)
    translation_text_error: Mapped[str] = mapped_column(Text, nullable=True)
    fmi_numbers: Mapped[int] = mapped_column()

    model_equipment = relationship(
        "ModelEquipment",
        back_populates="code_errors"
    )
    fmi_numbers = relationship(
        "FmiNumber",
        secondary=code_error_fmi_association,
        back_populates="code_errors"
    )

    def __repr__(self) -> str:
        return self.code_error


class FmiNumber(BaseWorker):
    """Модель базы данных, FMI номер."""

    __tablename__ = 'fmi_number'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    fmi_number: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(String(250), nullable=False)

    code_errors = relationship(
        "CodeError",
        secondary=code_error_fmi_association,
        back_populates="fmi_numbers"
    )

    def __repr__(self) -> str:
        return self.fmi_number
