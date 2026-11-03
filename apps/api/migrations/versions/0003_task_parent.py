"""Add parent/child relationships for bounded CEO workflows."""
from alembic import op
import sqlalchemy as sa

revision = "0003_task_parent"
down_revision = "0002_agent_tasks_approvals"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("agent_tasks", sa.Column("parent_task_id", sa.Uuid(), nullable=True))
    op.create_foreign_key(
        "fk_agent_tasks_parent_task_id_agent_tasks",
        "agent_tasks", "agent_tasks", ["parent_task_id"], ["id"], ondelete="CASCADE"
    )
    op.create_index("ix_agent_tasks_parent", "agent_tasks", ["parent_task_id"])

def downgrade():
    op.drop_index("ix_agent_tasks_parent", table_name="agent_tasks")
    op.drop_constraint("fk_agent_tasks_parent_task_id_agent_tasks", "agent_tasks", type_="foreignkey")
    op.drop_column("agent_tasks", "parent_task_id")
