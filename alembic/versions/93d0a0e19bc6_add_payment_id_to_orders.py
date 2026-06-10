"""add_payment_id_to_orders

Revision ID: 93d0a0e19bc6
Revises: 001
Create Date: 2026-06-10 17:45:32.117521

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op  # type: ignore

# revision identifiers, used by Alembic.
revision: str = "93d0a0e19bc6"
down_revision: Union[str, Sequence[str], None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("orders", sa.Column("payment_id", sa.UUID(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "payment_id")
