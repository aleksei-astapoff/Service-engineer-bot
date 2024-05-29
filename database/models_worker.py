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


class TupeEquiment(BaseWorker):
    """Модель базы данных, тип оборудования."""

    __tablename__ = 'tupe_equiment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_equiment: Mapped[str] = mapped_column(String(50), nullable=False)

    model_equiments = relationship(
        "ModelEquiment",
        back_populates="tupe_equiment"
    )

    def __repr__(self) -> str:
        return self.type_equiment


class ModelEquiment(BaseWorker):
    """Модель базы данных, модель оборудования."""

    __tablename__ = 'model_equiment'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    type_equiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('tupe_equiment.id'), nullable=False
    )
    model_equiment: Mapped[str] = mapped_column(String(50), nullable=False)

    tupe_equiment = relationship(
        "TupeEquiment",
        back_populates="model_equiments"
    )
    code_errors = relationship(
        "CodeError",
        back_populates="model_equiment"
    )

    def __repr__(self) -> str:
        return self.model_equiment


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
    model_equiment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey('model_equiment.id'), nullable=False
    )
    code_error: Mapped[str] = mapped_column(String(50), nullable=False)

    model_equiment = relationship(
        "ModelEquiment",
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
    fmi_number: Mapped[str] = mapped_column(String(250), nullable=False)

    code_errors = relationship(
        "CodeError",
        secondary=code_error_fmi_association,
        back_populates="fmi_numbers"
    )

    def __repr__(self) -> str:
        return self.fmi_number
