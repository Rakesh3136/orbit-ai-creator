from alembic import op
import sqlalchemy as sa

revision = "0001_networks_channels"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "networks",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("default_locale", sa.String(20), server_default="en", nullable=False),
        sa.Column("status", sa.String(20), server_default="active", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('active','paused','archived')", name="ck_networks_status"),
    )
    op.create_table(
        "channels",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("network_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("slug", sa.String(80), nullable=False),
        sa.Column("description", sa.String(1000)),
        sa.Column("niche", sa.String(160)),
        sa.Column("primary_language", sa.String(20), server_default="en", nullable=False),
        sa.Column("target_regions", sa.JSON(), server_default="[]", nullable=False),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("youtube_channel_id", sa.String(128)),
        sa.Column("credential_ref", sa.String(255)),
        sa.Column("policy", sa.JSON(), server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["network_id"], ["networks.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("network_id", "slug", name="uq_channels_network_slug"),
        sa.UniqueConstraint("youtube_channel_id", name="uq_channels_youtube_channel_id"),
        sa.CheckConstraint("status IN ('draft','active','paused','archived')", name="ck_channels_status"),
    )
    op.create_index("ix_channels_network_id", "channels", ["network_id"])

def downgrade():
    op.drop_index("ix_channels_network_id", table_name="channels")
    op.drop_table("channels")
    op.drop_table("networks")
