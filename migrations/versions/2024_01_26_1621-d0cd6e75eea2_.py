"""empty message

Revision ID: d0cd6e75eea2
Revises: 4b359d1a6081
Create Date: 2024-01-26 16:21:57.097754

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "d0cd6e75eea2"
down_revision = "4b359d1a6081"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "game",
        sa.Column(
            "result",
            sa.Enum("checkmate", "draw", "resign", "abandoned", name="result"),
            nullable=True,
        ),
    )
    op.drop_column("game", "outcome")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "game",
        sa.Column(
            "outcome",
            postgresql.ENUM("checkmate", "draw", "abandoned", name="result"),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.drop_column("game", "result")
    # ### end Alembic commands ###
