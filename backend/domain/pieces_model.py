from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


pieces = Table('pieces', metadata,
    Column('code', String(64), primary_key=True),
    Column('description', String(160), nullable=False),
    Column('mass_g', Float, nullable=False),
    Column('stone_count', Integer, nullable=False),
    Column('seal', String(64), nullable=False, unique=True),
    Column('arrived', String(160), nullable=False),
    CheckConstraint('mass_g between 0.1 and 40'),
    CheckConstraint('stone_count between 0 and 8'),
)
