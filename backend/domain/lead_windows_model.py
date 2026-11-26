from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


lead_windows = Table('lead_windows', metadata,
    Column('code', String(64), primary_key=True),
    Column('piece', String(64), ForeignKey('pieces.code'), nullable=False),
    Column('backlog', Integer, nullable=False),
    Column('signature', String(64), nullable=False),
    Column('lower_days', Integer, nullable=False),
    Column('upper_days', Integer, nullable=False),
    Column('coverage', Float, nullable=False),
    Column('evidence', JSON, nullable=False),
    CheckConstraint('lower_days >= 1 and upper_days >= lower_days'),
    CheckConstraint('coverage between 0 and 1'),
    CheckConstraint('backlog between 0 and 24'),
)
