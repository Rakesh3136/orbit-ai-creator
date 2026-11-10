"""Add structured task input payloads for local production handoff."""
from alembic import op
import sqlalchemy as sa

revision = "0005_task_input_payload"
down_revision = "0004_agent_feedback"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("agent_tasks", sa.Column("input_payload", sa.JSON(), server_default=sa.text("'{}'"), nullable=False))

def downgrade():
    op.drop_column("agent_tasks", "input_payload")
