"""initial schema

Revision ID: f62c242df6ae
Revises: 
Create Date: 2026-03-31 14:41:37.636104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f62c242df6ae'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "ideas",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("source_url", sa.String(500), nullable=True),
    )
    op.create_index("ix_ideas_id", "ideas", ["id"])

    op.create_table(
        "analysis",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("idea_id", sa.Integer(), sa.ForeignKey("ideas.id"), unique=True, nullable=False),
        sa.Column("problem", sa.Text(), nullable=True),
        sa.Column("failure_type", sa.String(50), nullable=True),
        sa.Column("current_opportunity", sa.String(20), nullable=True),
        sa.Column("pain_score", sa.Integer(), nullable=True),
        sa.Column("paying_capacity", sa.Integer(), nullable=True),
        sa.Column("mvp_ease", sa.Integer(), nullable=True),
        sa.Column("tech_advantage", sa.Integer(), nullable=True),
        sa.Column("total_score", sa.Float(), nullable=True),
    )
    op.create_index("ix_analysis_id", "analysis", ["id"])

    op.create_table(
        "execution",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("idea_id", sa.Integer(), sa.ForeignKey("ideas.id"), unique=True, nullable=False),
        sa.Column("mvp_plan", sa.Text(), nullable=True),
        sa.Column("stack", sa.Text(), nullable=True),
        sa.Column("monetization", sa.Text(), nullable=True),
        sa.Column("estimated_days", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), server_default="pending"),
    )
    op.create_index("ix_execution_id", "execution", ["id"])


def downgrade() -> None:
    op.drop_table("execution")
    op.drop_table("analysis")
    op.drop_table("ideas")
