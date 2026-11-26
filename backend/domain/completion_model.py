from sqlalchemy import Column, DateTime, ForeignKey, String, Table

from core.db import metadata


completions = Table('completions', metadata,
    Column('code', String(64), primary_key=True),
    Column('piece', String(64), ForeignKey('pieces.code'), nullable=False),
    Column('ticket', String(64), ForeignKey('promise_tickets.code'), nullable=False, unique=True),
    Column('completed_day', String(160), nullable=False),
    Column('recorded_at', DateTime, nullable=False),
)
