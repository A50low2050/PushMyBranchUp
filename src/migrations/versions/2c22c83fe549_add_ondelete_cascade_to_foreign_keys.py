"""add ondelete cascade to foreign keys

Revision ID: 2c22c83fe549
Revises: 9e1779c1efe1
Create Date: 2026-10-16 10:51:10.154830

SQLite не умеет изменять внешние ключи существующих таблиц
и не даёт им имен, поэтому drop_constraint(None) невозможен.
Каждая таблица пересоздаётся вручную: новая схема с ON DELETE CASCADE,
копирование данных, удаление старой таблицы, переименование.

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "2c22c83fe549"
down_revision: Union[str, Sequence[str], None] = "9e1779c1efe1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TS = sa.DateTime(timezone=True)
_SERVER_DEFAULT = sa.text("(CURRENT_TIMESTAMP)")


def _timestamp(name: str) -> sa.Column:
    return sa.Column(name, _TS, server_default=_SERVER_DEFAULT, nullable=False)


def _recreate_table(
    table: str,
    columns: list,
    foreign_keys: list,
    unique_constraints: list | None = None,
) -> None:
    """Пересоздать таблицу с новыми внешними ключами, сохранив данные."""
    new_table = f"{table}_new"
    op.create_table(
        new_table,
        *columns,
        *foreign_keys,
        sa.PrimaryKeyConstraint("id"),
        *(unique_constraints or []),
    )
    op.execute(f'INSERT INTO "{new_table}" SELECT * FROM "{table}"')
    op.drop_table(table)
    op.rename_table(new_table, table)


def upgrade() -> None:
    _recreate_table(
        "comments",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("post_id", sa.Integer(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        ],
    )

    _recreate_table(
        "likes",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("post_id", sa.Integer(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["post_id"], ["posts.id"], ondelete="CASCADE"),
        ],
        [
            sa.UniqueConstraint("user_id", "post_id", name="uq_likes_user_post"),
        ],
    )

    _recreate_table(
        "posts",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        ],
    )

    _recreate_table(
        "subscriptions",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("follower_id", sa.Integer(), nullable=False),
            sa.Column("followed_id", sa.Integer(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["followed_id"], ["users.id"], ondelete="CASCADE"),
        ],
        [
            sa.UniqueConstraint(
                "follower_id", "followed_id", name="uq_subscriptions_follower_followed"
            ),
        ],
    )

    _recreate_table(
        "tokens",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("hashed_data", sa.String(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("expires_at", _TS, nullable=False),
            sa.Column("access_jti", sa.String(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        ],
    )


def downgrade() -> None:
    _recreate_table(
        "tokens",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("hashed_data", sa.String(), nullable=False),
            sa.Column("owner_id", sa.Integer(), nullable=False),
            sa.Column("expires_at", _TS, nullable=False),
            sa.Column("access_jti", sa.String(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        ],
    )

    _recreate_table(
        "subscriptions",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("follower_id", sa.Integer(), nullable=False),
            sa.Column("followed_id", sa.Integer(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["follower_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["followed_id"], ["users.id"]),
        ],
        [
            sa.UniqueConstraint(
                "follower_id", "followed_id", name="uq_subscriptions_follower_followed"
            ),
        ],
    )

    _recreate_table(
        "posts",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("content", sa.Text(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        ],
    )

    _recreate_table(
        "likes",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("post_id", sa.Integer(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        ],
        [
            sa.UniqueConstraint("user_id", "post_id", name="uq_likes_user_post"),
        ],
    )

    _recreate_table(
        "comments",
        [
            sa.Column("id", sa.Integer(), autoincrement=True),
            sa.Column("content", sa.Text(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.Column("post_id", sa.Integer(), nullable=False),
            _timestamp("created_at"),
            _timestamp("updated_at"),
        ],
        [
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.ForeignKeyConstraint(["post_id"], ["posts.id"]),
        ],
    )
