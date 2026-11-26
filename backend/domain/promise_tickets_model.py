from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


promise_tickets = Table('promise_tickets', metadata,
    Column('code', String(64), primary_key=True),
    Column('piece', String(64), ForeignKey('pieces.code'), nullable=False),
    Column('estimate', String(64), ForeignKey('lead_windows.code'), nullable=False, unique=True),
    Column('bench', String(64), nullable=False),
    Column('start_day', String(160), nullable=False),
    Column('end_day', String(160), nullable=False),
    Column('state', String(160), nullable=False),
    Column('previous', String(64), ForeignKey('promise_tickets.code'), nullable=True, unique=True),
    Column('reason', String(160), nullable=True),
    CheckConstraint("state in ('现行','已修订')"),
    CheckConstraint('end_day >= start_day'),
)
