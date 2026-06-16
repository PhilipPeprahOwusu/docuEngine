"""add_finalization_and_rbac_fields

Revision ID: fcce94bce04c
Revises:
Create Date: 2026-06-15 23:01:53.419877

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = 'fcce94bce04c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add columns to documents table
    op.add_column('documents', sa.Column('status', sa.String(50), server_default='pending', nullable=True))
    op.add_column('documents', sa.Column('finalized_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('documents', sa.Column('finalized_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('documents', sa.Column('signature_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('documents', sa.Column('final_pdf_url', sa.String(500), nullable=True))

    # Add foreign key for finalized_by
    op.create_foreign_key(
        'fk_documents_finalized_by_users',
        'documents', 'users',
        ['finalized_by'], ['user_id']
    )

    # Add columns to policy_exceptions table
    op.add_column('policy_exceptions', sa.Column('status', sa.String(50), server_default='pending', nullable=True))
    op.add_column('policy_exceptions', sa.Column('requested_by', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('policy_exceptions', sa.Column('rejection_reason', sa.Text(), nullable=True))

    # Add foreign key for requested_by
    op.create_foreign_key(
        'fk_policy_exceptions_requested_by_users',
        'policy_exceptions', 'users',
        ['requested_by'], ['user_id']
    )

    # Make approved_by nullable (since it's null until approval)
    op.alter_column('policy_exceptions', 'approved_by', nullable=True)


def downgrade() -> None:
    # Remove foreign keys first
    op.drop_constraint('fk_documents_finalized_by_users', 'documents', type_='foreignkey')
    op.drop_constraint('fk_policy_exceptions_requested_by_users', 'policy_exceptions', type_='foreignkey')

    # Remove columns from documents table
    op.drop_column('documents', 'final_pdf_url')
    op.drop_column('documents', 'signature_data')
    op.drop_column('documents', 'finalized_at')
    op.drop_column('documents', 'finalized_by')
    op.drop_column('documents', 'status')

    # Remove columns from policy_exceptions table
    op.drop_column('policy_exceptions', 'rejection_reason')
    op.drop_column('policy_exceptions', 'requested_by')
    op.drop_column('policy_exceptions', 'status')

    # Revert approved_by to not nullable
    op.alter_column('policy_exceptions', 'approved_by', nullable=False)
