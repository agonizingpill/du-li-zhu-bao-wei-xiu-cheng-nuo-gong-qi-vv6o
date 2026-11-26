from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


bench_steps = Table('bench_steps', metadata,
    Column('code', String(64), primary_key=True),
    Column('piece', String(64), ForeignKey('pieces.code'), nullable=False),
    Column('operation', String(160), nullable=False),
    Column('minutes', Integer, nullable=False),
    Column('first_witness', String(160), nullable=True),
    Column('second_witness', String(160), nullable=True),
    CheckConstraint('minutes between 10 and 180'),
    CheckConstraint("operation in ('镶石拆装','抛光','整形')"),
    CheckConstraint('first_witness IS NULL OR second_witness IS NULL OR first_witness <> second_witness'),
)
