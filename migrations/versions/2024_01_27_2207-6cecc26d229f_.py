"""empty message

Revision ID: 6cecc26d229f
Revises: 
Create Date: 2024-01-27 22:07:06.862128

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6cecc26d229f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Need to add manually
    from sqlalchemy.schema import Sequence, CreateSequence
    op.execute(CreateSequence(Sequence('ply_seq')))

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "game",
        sa.Column("white_id", sa.Integer(), nullable=True),
        sa.Column("black_id", sa.Integer(), nullable=True),
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
        sa.Column("fen", sa.String(), nullable=False),
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
        sa.Column(
            "ply",
            sa.Integer(),
            server_default=sa.text("nextval('ply_seq')"),
            nullable=False,
        ),
        sa.Column("move", sa.String(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["game_id"],
            ["game.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # Need to add manually
    from sqlalchemy.schema import Sequence, DropSequence
    op.execute(DropSequence(Sequence('ply_seq')))

    op.drop_table("move")
    op.drop_table("game")
    op.drop_table("user")
