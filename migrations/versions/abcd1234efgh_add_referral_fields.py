"""add_referral_fields

Revision ID: abcd1234efgh
Revises: 
Create Date: 2025-03-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy import inspect

# revision identifiers, used by Alembic
revision = 'abcd1234efgh'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Get inspector to check existing columns
    conn = op.get_bind()
    inspector = inspect(conn)
    user_columns = [column['name'] for column in inspector.get_columns('user')]
    
    # Add referral fields to the user table if they don't exist
    if 'referred_by' not in user_columns:
        op.add_column('user', sa.Column('referred_by', sa.Integer(), nullable=True))
    
    if 'referrals' not in user_columns:
        op.add_column('user', sa.Column('referrals', sa.Integer(), nullable=True, server_default='0'))
    
    # Only create the foreign key if it doesn't exist
    # SQLite doesn't support dropping foreign keys, so let's be cautious here
    # Check if foreign key already exists
    fks = inspector.get_foreign_keys('user')
    has_fk = any(fk['name'] == 'fk_user_referred_by' for fk in fks)
    
    if not has_fk and 'referred_by' in user_columns:
        # For SQLite, we skip this as it's already defined in the model
        # SQLite has very limited ALTER TABLE support
        print("Note: Skipping foreign key creation for SQLite - define in model instead")
    
    # Skip constraint modification for SQLite - transaction_type is just a string column
    # and the CHECK constraint would be enforced at the application level
    print("Note: Skipping constraint modification for SQLite")


def downgrade():
    # No need to drop columns that might already be gone
    # Foreign key handling is skipped for SQLite
    
    # Remove columns
    conn = op.get_bind()
    inspector = inspect(conn)
    user_columns = [column['name'] for column in inspector.get_columns('user')]
    
    if 'referrals' in user_columns:
        op.drop_column('user', 'referrals')
    
    if 'referred_by' in user_columns:
        op.drop_column('user', 'referred_by')
    
    # Skip constraint modification for SQLite
    print("Note: Skipping constraint reversion for SQLite")