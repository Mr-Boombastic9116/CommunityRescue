"""add_verification_matching_timeline

Revision ID: 3b4269e5df29
Revises: 2a3158f4cf18
Create Date: 2026-10-31 14:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '3b4269e5df29'
down_revision: Union[str, Sequence[str], None] = '2a3158f4cf18'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # 1. Update pickup_requests with OTP and QR fields
    pr_cols = [c['name'] for c in inspector.get_columns('pickup_requests')]
    if 'pickup_otp_hash' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('pickup_otp_hash', sa.String(length=128), nullable=True))
    if 'pickup_otp_expires_at' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('pickup_otp_expires_at', sa.DateTime(), nullable=True))
    if 'pickup_attempts_count' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('pickup_attempts_count', sa.Integer(), server_default='0', nullable=False))
    if 'delivery_otp_hash' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('delivery_otp_hash', sa.String(length=128), nullable=True))
    if 'delivery_otp_expires_at' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('delivery_otp_expires_at', sa.DateTime(), nullable=True))
    if 'delivery_attempts_count' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('delivery_attempts_count', sa.Integer(), server_default='0', nullable=False))
    if 'qr_token' not in pr_cols:
        op.add_column('pickup_requests', sa.Column('qr_token', sa.String(length=64), nullable=True))
        op.create_index('idx_req_qr_token', 'pickup_requests', ['qr_token'])

    # 2. Update ngo_partners with smart matching fields
    ngo_cols = [c['name'] for c in inspector.get_columns('ngo_partners')]
    if 'preferred_categories' not in ngo_cols:
        op.add_column('ngo_partners', sa.Column('preferred_categories', sa.String(length=255), server_default='Cooked Meals, Bakery & Bread, Raw Food/Produce', nullable=True))
    if 'capacity_servings' not in ngo_cols:
        op.add_column('ngo_partners', sa.Column('capacity_servings', sa.Integer(), server_default='100', nullable=True))
    if 'operating_hours' not in ngo_cols:
        op.add_column('ngo_partners', sa.Column('operating_hours', sa.String(length=100), server_default='09:00 - 21:00', nullable=True))
    if 'is_active' not in ngo_cols:
        op.add_column('ngo_partners', sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False))

    # 3. Update delivery_logs with optional batch_id
    dl_cols = [c['name'] for c in inspector.get_columns('delivery_logs')]
    if 'batch_id' not in dl_cols:
        op.add_column('delivery_logs', sa.Column('batch_id', sa.Integer(), nullable=True))
        op.create_index('idx_log_batch', 'delivery_logs', ['batch_id'])

    # 4. Update notifications with metadata
    notif_cols = [c['name'] for c in inspector.get_columns('notifications')]
    if 'notification_type' not in notif_cols:
        op.add_column('notifications', sa.Column('notification_type', sa.String(length=50), nullable=True))
        op.create_index('idx_notif_type', 'notifications', ['notification_type'])
    if 'reference_id' not in notif_cols:
        op.add_column('notifications', sa.Column('reference_id', sa.Integer(), nullable=True))
    if 'role_target' not in notif_cols:
        op.add_column('notifications', sa.Column('role_target', sa.String(length=20), nullable=True))

def downgrade() -> None:
    pass

