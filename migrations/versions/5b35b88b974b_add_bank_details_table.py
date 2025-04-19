"""add bank details table

Revision ID: 5b35b88b974c
Revises: abcd1234efgh
Create Date: 2025-03-12 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5b35b88b974c'
down_revision = 'abcd1234efgh'  # Update this to your latest migration id
branch_labels = None
depends_on = None


def upgrade():
    # Create bank_details table
    op.create_table('bank_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('account_holder', sa.String(length=100), nullable=True),
        sa.Column('bank_name', sa.String(length=100), nullable=True),
        sa.Column('account_number', sa.String(length=30), nullable=True),
        sa.Column('ifsc_code', sa.String(length=20), nullable=True),
        sa.Column('branch_name', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], name='fk_bank_details_user'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )


def downgrade():
    # Drop bank_details table
    op.drop_table('bank_details')