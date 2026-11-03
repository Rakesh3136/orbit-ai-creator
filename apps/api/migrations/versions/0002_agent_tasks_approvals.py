from alembic import op
import sqlalchemy as sa

revision = "0002_agent_tasks_approvals"
down_revision = "0001_networks_channels"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "agent_tasks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("network_id", sa.Uuid(), nullable=False),
        sa.Column("channel_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.String(80), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("instruction", sa.Text(), nullable=False),
        sa.Column("status", sa.String(30), server_default="queued", nullable=False),
        sa.Column("external_action", sa.Boolean(), server_default=sa.false(), nullable=False),
        sa.Column("result", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["network_id"], ["networks.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["channel_id"], ["channels.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('queued','awaiting_approval','running','completed','failed','cancelled')", name="ck_agent_tasks_status"),
    )
    op.create_index("ix_agent_tasks_network_created", "agent_tasks", ["network_id", "created_at"])
    op.create_table(
        "approvals",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("decision_note", sa.String(1000)),
        sa.Column("decided_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["task_id"], ["agent_tasks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id"),
        sa.CheckConstraint("status IN ('pending','approved','rejected')", name="ck_approvals_status"),
    )

def downgrade():
    op.drop_table("approvals")
    op.drop_index("ix_agent_tasks_network_created", table_name="agent_tasks")
    op.drop_table("agent_tasks")
