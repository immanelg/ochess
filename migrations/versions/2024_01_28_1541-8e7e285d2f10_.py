"""empty message

Revision ID: 8e7e285d2f10
Revises: 6cecc26d229f
Create Date: 2024-01-28 15:41:24.236084

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8e7e285d2f10"
down_revision = "6cecc26d229f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("move", "ply")

    from sqlalchemy.schema import DropSequence, Sequence
    op.execute(DropSequence(Sequence('ply_seq')))



def downgrade() -> None:
    op.add_column(
        "move",
        sa.Column(
            "ply",
            sa.INTEGER(),
            server_default=sa.text("nextval('ply_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
    )
    from sqlalchemy.schema import CreateSequence, Sequence
    op.execute(CreateSequence(Sequence('ply_seq')))

