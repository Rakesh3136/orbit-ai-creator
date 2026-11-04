"""Add owner task evaluations and approval-gated lessons."""
from alembic import op
import sqlalchemy as sa

revision = "0004_agent_feedback"
down_revision = "0003_task_parent"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "agent_evaluations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("network_id", sa.Uuid(), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.String(80), nullable=False),
        sa.Column("skill_id", sa.String(160), nullable=False),
        sa.Column("skill_version", sa.String(40), nullable=False),
        sa.Column("registry_version", sa.String(40), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("correction", sa.Text(), nullable=True),
        sa.Column("lesson", sa.Text(), nullable=True),
        sa.Column("lesson_status", sa.String(20), server_default="none", nullable=False),
        sa.Column("reviewer_email", sa.String(254), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("decided_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("decision_note", sa.String(1000), nullable=True),
        sa.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_agent_evaluations_rating"),
        sa.CheckConstraint("lesson_status IN ('none','pending','approved','rejected')", name="ck_agent_evaluations_lesson_status"),
        sa.ForeignKeyConstraint(["task_id"], ["agent_tasks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["network_id"], ["networks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", name="uq_agent_evaluations_task_id"),
    )
    op.create_index("ix_agent_evaluations_scope_status", "agent_evaluations", ["network_id", "channel_id", "lesson_status"])


def downgrade():
    op.drop_index("ix_agent_evaluations_scope_status", table_name="agent_evaluations")
    op.drop_table("agent_evaluations")
