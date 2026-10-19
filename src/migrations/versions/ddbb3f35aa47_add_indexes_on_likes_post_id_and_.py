"""add_indexes_on_likes_post_id_and_subscriptions_followed_id

Revision ID: ddbb3f35aa47
Revises: e2a85329ec4f
Create Date: 2026-10-18 14:16:05.675889

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "ddbb3f35aa47"
down_revision: Union[str, Sequence[str], None] = "e2a85329ec4f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f("ix_likes_post_id"), "likes", ["post_id"], unique=False)
    op.create_index(
        op.f("ix_subscriptions_followed_id"),
        "subscriptions",
        ["followed_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_subscriptions_followed_id"), table_name="subscriptions")
    op.drop_index(op.f("ix_likes_post_id"), table_name="likes")
