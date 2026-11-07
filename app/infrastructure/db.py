from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import DateTime, Integer, Numeric, String, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.domain.orcamento import Orcamento, OrcamentoStatus
from app.settings import get_settings


class Base(DeclarativeBase):
    pass


class OrcamentoOrm(Base):
    __tablename__ = "orcamentos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    os_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    valor_total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[str] = mapped_column(String(32))
    correlation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    mp_preference_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PagamentoOrm(Base):
    __tablename__ = "pagamentos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    os_id: Mapped[int] = mapped_column(Integer, index=True)
    orcamento_id: Mapped[int] = mapped_column(Integer)
    mp_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


_engine = None
_Session: sessionmaker[Session] | None = None


def get_engine():
    global _engine
    if _engine is None:
        url = get_settings().database_url
        kw = {"connect_args": {"check_same_thread": False}} if url.startswith("sqlite") else {}
        _engine = create_engine(url, pool_pre_ping=True, future=True, **kw)
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _Session
    if _Session is None:
        _Session = sessionmaker(get_engine(), expire_on_commit=False)
    return _Session


def init_db() -> None:
    Base.metadata.create_all(get_engine())


def save_orcamento(session: Session, o: Orcamento) -> Orcamento:
    if o.id is None:
        row = OrcamentoOrm(
            os_id=o.os_id,
            valor_total=o.valor_total,
            status=o.status.value,
            correlation_id=o.correlation_id,
            mp_preference_id=o.mp_preference_id,
            created_at=o.created_at,
        )
        session.add(row)
        session.flush()
        o.id = row.id
    else:
        row = session.get(OrcamentoOrm, o.id)
        assert row
        row.status = o.status.value
        row.mp_preference_id = o.mp_preference_id
    return o


def get_orcamento_by_os(session: Session, os_id: int) -> Orcamento | None:
    row = session.execute(select(OrcamentoOrm).where(OrcamentoOrm.os_id == os_id)).scalar_one_or_none()
    if not row:
        return None
    return Orcamento(
        id=row.id,
        os_id=row.os_id,
        valor_total=row.valor_total,
        status=OrcamentoStatus(row.status),
        correlation_id=row.correlation_id,
        mp_preference_id=row.mp_preference_id,
        created_at=row.created_at,
    )
