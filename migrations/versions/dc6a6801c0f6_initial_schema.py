"""initial schema

Revision ID: dc6a6801c0f6
Revises: 
Create Date: 2026-01-19 01:57:05.216984
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'dc6a6801c0f6'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # USERS
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String, nullable=False),
        sa.Column('password_hash', sa.String, nullable=False),
        sa.Column('role', sa.String, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=True),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    # REGISTRATION DETAILS
    op.create_table(
        'registration_details',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('full_name', sa.String, nullable=False),
        sa.Column('phone', sa.String, nullable=False),
        sa.Column('address', sa.String),
        sa.Column('city', sa.String),
        sa.Column('state', sa.String),
        sa.Column('created_at', sa.DateTime),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id'),
    )

    # DONATIONS
    op.create_table(
        'donations',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, nullable=False),
        sa.Column('amount', sa.Float, nullable=False),
        sa.Column('status', sa.String),
        sa.Column('payment_reference', sa.String),
        sa.Column('created_at', sa.DateTime),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
    )


def downgrade() -> None:
    op.drop_table('donations')
    op.drop_table('registration_details')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
