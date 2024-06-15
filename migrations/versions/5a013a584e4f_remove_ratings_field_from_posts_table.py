"""Remove ratings field from posts table

Revision ID: 5a013a584e4f
Revises: ff532297a83c
Create Date: 2024-06-14 17:55:14.831120

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5a013a584e4f"
down_revision: Union[str, None] = "ff532297a83c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("posts", "rating")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "posts",
        sa.Column("rating", sa.INTEGER(), autoincrement=False, nullable=True),
    )
    # ### end Alembic commands ###
