"""add indexes on posts.user_id, comments.post_id, tokens.hashed_data

Revision ID: e2a85329ec4f
Revises: 2c22c83fe549
Create Date: 2026-10-16 11:43:23.788947

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e2a85329ec4f"
down_revision: Union[str, Sequence[str], None] = "2c22c83fe549"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(op.f("ix_comments_post_id"), "comments", ["post_id"], unique=False)
    op.create_index(op.f("ix_posts_user_id"), "posts", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_tokens_hashed_data"), "tokens", ["hashed_data"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_tokens_hashed_data"), table_name="tokens")
    op.drop_index(op.f("ix_posts_user_id"), table_name="posts")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
