"""empty message

Revision ID: b95d3bdcaccf
Revises:
Create Date: 2024-01-30 23:21:45.738015

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b95d3bdcaccf"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game",
        sa.Column("white_id", sa.Integer(), nullable=True),
        sa.Column("black_id", sa.Integer(), nullable=True),
        sa.Column("fen", sa.String(), nullable=False),
        sa.Column(
            "stage",
            sa.Enum("waiting", "playing", "ended", name="stage"),
            nullable=False,
        ),
        sa.Column(
            "result",
            sa.Enum("checkmate", "draw", "resign", "abandoned", name="result"),
            nullable=True,
        ),
        sa.Column("winner", sa.Enum("white", "black", name="color"), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["black_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["white_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "move",
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("ply", sa.Integer(), nullable=False),
        sa.Column("src", sa.String(length=2), nullable=False),
        sa.Column("dest", sa.String(length=2), nullable=False),
        sa.Column("promo", sa.String(length=1), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["game_id"],
            ["game.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("move")
    op.drop_table("game")
    op.drop_table("user")
    # ### end Alembic commands ###