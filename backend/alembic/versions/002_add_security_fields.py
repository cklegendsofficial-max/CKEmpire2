"""Add security fields to User table

Revision ID: 002
Revises: 001_initial_schema
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Add security fields to users table"""
    # Add security fields to users table
    op.add_column('users', sa.Column('failed_login_attempts', sa.Integer(), nullable=True, default=0))
    op.add_column('users', sa.Column('last_failed_login', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('account_locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('session_token_hash', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('two_factor_enabled', sa.Boolean(), nullable=True, default=False))
    op.add_column('users', sa.Column('two_factor_secret', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('last_security_audit', sa.DateTime(), nullable=True))


def downgrade():
    """Remove security fields from users table"""
    op.drop_column('users', 'last_security_audit')
    op.drop_column('users', 'two_factor_secret')
    op.drop_column('users', 'two_factor_enabled')
    op.drop_column('users', 'session_token_hash')
    op.drop_column('users', 'password_changed_at')
    op.drop_column('users', 'account_locked_until')
    op.drop_column('users', 'last_failed_login')
    op.drop_column('users', 'failed_login_attempts') 