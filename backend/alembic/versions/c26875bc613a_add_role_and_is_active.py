"""add role and is_active

Revision ID: c26875bc613a
Revises: 683e11ae5e16
Create Date: 2026-03-28 19:48:42.000000
"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c26875bc613a"
down_revision = "683e11ae5e16"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("role", sa.String(), server_default="student"))
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default="true"))
    # Если в таблице news ещё нет колонки author_id (связь с пользователем),
    # раскомментируйте следующую строку:
    # op.add_column('news', sa.Column('author_id', sa.UUID(), sa.ForeignKey('users.id')))


def downgrade():
    op.drop_column("users", "role")
    op.drop_column("users", "is_active")
    # op.drop_column('news', 'author_id')
