"""create call_logs table

Revision ID: 0001
Revises: 
Create Date: 2026-04-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "call_logs",
        sa.Column("id", sa.String, primary_key=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("language", sa.String(10)),
        sa.Column("transcript", sa.Text),
        sa.Column("summary", sa.Text),
        sa.Column("payment", sa.String(20)),
        sa.Column("rejection", sa.String(30)),
        sa.Column("sentiment", sa.String(10)),
        sa.Column("compliance", sa.Float),
        sa.Column("adherence", sa.String(15)),
        sa.Column("raw_response", sa.JSON),
    )

def downgrade():
    op.drop_table("call_logs")
