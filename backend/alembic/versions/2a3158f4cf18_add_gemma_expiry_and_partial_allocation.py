"""add_gemma_expiry_and_partial_allocation

Revision ID: 2a3158f4cf18
Revises: 828b7ccd2497
Create Date: 2026-10-31 12:56:09.953378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2a3158f4cf18'
down_revision: Union[str, Sequence[str], None] = '828b7ccd2497'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema safely preserving existing data."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # 1. Create food_safety_rules table if not present
    if 'food_safety_rules' not in existing_tables:
        op.create_table(
            'food_safety_rules',
            sa.Column('rule_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('food_category', sa.String(length=100), nullable=False),
            sa.Column('product_type', sa.String(length=150), nullable=False),
            sa.Column('storage_condition', sa.String(length=50), nullable=False),
            sa.Column('temperature_min_c', sa.Numeric(precision=5, scale=2), nullable=True),
            sa.Column('temperature_max_c', sa.Numeric(precision=5, scale=2), nullable=True),
            sa.Column('max_holding_hours', sa.Numeric(precision=8, scale=2), nullable=False),
            sa.Column('source_name', sa.String(length=150), nullable=False),
            sa.Column('source_url', sa.Text(), nullable=True),
            sa.Column('rule_version', sa.String(length=50), server_default='FSSAI-2023-V1', nullable=False),
            sa.Column('requires_manual_verification', sa.Boolean(), server_default='0', nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
            sa.PrimaryKeyConstraint('rule_id')
        )
        op.create_index('idx_rule_category_storage', 'food_safety_rules', ['food_category', 'storage_condition'])
        op.create_index('idx_rule_product_type', 'food_safety_rules', ['product_type'])

    # 2. Add columns to food_batches if not present
    fb_cols = [c['name'] for c in inspector.get_columns('food_batches')]
    if 'food_description' not in fb_cols:
        op.add_column('food_batches', sa.Column('food_description', sa.Text(), nullable=True))
    if 'user_expiry_time' not in fb_cols:
        op.add_column('food_batches', sa.Column('user_expiry_time', sa.DateTime(), nullable=True))
    if 'effective_expiry_time' not in fb_cols:
        op.add_column('food_batches', sa.Column('effective_expiry_time', sa.DateTime(), nullable=True))
    if 'packaging_expiry_time' not in fb_cols:
        op.add_column('food_batches', sa.Column('packaging_expiry_time', sa.DateTime(), nullable=True))
    if 'storage_condition' not in fb_cols:
        op.add_column('food_batches', sa.Column('storage_condition', sa.String(length=50), server_default='ambient', nullable=False))
    if 'storage_temperature' not in fb_cols:
        op.add_column('food_batches', sa.Column('storage_temperature', sa.Numeric(precision=5, scale=2), nullable=True))
    if 'expiry_validation_status' not in fb_cols:
        op.add_column('food_batches', sa.Column('expiry_validation_status', sa.String(length=50), server_default='verified', nullable=False))
    if 'expiry_rule_applied' not in fb_cols:
        op.add_column('food_batches', sa.Column('expiry_rule_applied', sa.String(length=255), nullable=True))
    if 'image_url' not in fb_cols:
        op.add_column('food_batches', sa.Column('image_url', sa.Text(), nullable=True))

    # 3. Add columns to pickup_requests if not present
    pr_cols = [c['name'] for c in inspector.get_columns('pickup_requests')]
    if 'requested_quantity' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('requested_quantity', sa.Numeric(precision=10, scale=2), server_default='1.00', nullable=False))
    if 'unit' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('unit', sa.String(length=50), server_default='units', nullable=False))

    # 4. Backfill existing records
    op.execute("UPDATE food_batches SET user_expiry_time = expiry_time, effective_expiry_time = expiry_time WHERE user_expiry_time IS NULL")
    op.execute("UPDATE pickup_requests pr JOIN food_batches fb ON pr.batch_id = fb.batch_id SET pr.requested_quantity = fb.quantity, pr.unit = fb.unit WHERE pr.requested_quantity IS NULL OR pr.requested_quantity = 0 OR pr.requested_quantity = 1.00")


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('pickup_requests', 'unit')
    op.drop_column('pickup_requests', 'requested_quantity')
    op.drop_column('food_batches', 'image_url')
    op.drop_column('food_batches', 'expiry_rule_applied')
    op.drop_column('food_batches', 'expiry_validation_status')
    op.drop_column('food_batches', 'storage_temperature')
    op.drop_column('food_batches', 'storage_condition')
    op.drop_column('food_batches', 'packaging_expiry_time')
    op.drop_column('food_batches', 'effective_expiry_time')
    op.drop_column('food_batches', 'user_expiry_time')
    op.drop_column('food_batches', 'food_description')
    op.drop_index('idx_rule_product_type', table_name='food_safety_rules')
    op.drop_index('idx_rule_category_storage', table_name='food_safety_rules')
    op.drop_table('food_safety_rules')
