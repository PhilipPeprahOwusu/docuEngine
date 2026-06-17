"""add_api_keys_table

Revision ID: c833ad07a543
Revises: fcce94bce04c
Create Date: 2026-06-16 17:53:01.804252

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c833ad07a543'
down_revision = 'fcce94bce04c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table('api_keys',
    sa.Column('key_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('org_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('encrypted_key', sa.Text(), nullable=False),
    sa.Column('key_preview', sa.String(length=20), nullable=False),
    sa.Column('model_name', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], ['organizations.org_id'], ),
    sa.PrimaryKeyConstraint('key_id')
    )
    op.create_index(op.f('ix_api_keys_org_id'), 'api_keys', ['org_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_api_keys_org_id'), table_name='api_keys')
    op.drop_table('api_keys')
