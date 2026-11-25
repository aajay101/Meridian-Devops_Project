
"""Initial PostgreSQL schema

Revision ID: 1ea32a95d0e1
Revises:
Create Date: 2026-11-24 13:15:54.393000

"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision = "1ea32a95d0e1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create the initial Meridian PostgreSQL schema."""

    op.create_table(
        "reminder_run",
        sa.Column("run_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("run_date"),
    )

    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=120), nullable=False),
        sa.Column("phone_number", sa.String(length=10), nullable=True),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("phone_number"),
    )

    op.create_table(
        "company_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("company_name", sa.String(length=120), nullable=False),
        sa.Column("hr_contact", sa.String(length=120), nullable=False),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("approval_status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "student_profile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("branch", sa.String(length=80), nullable=False),
        sa.Column("cgpa", sa.Float(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("resume_path", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "export_job",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.String(length=255), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profile.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_export_job_task_id",
        "export_job",
        ["task_id"],
        unique=True,
    )

    op.create_table(
        "placement_drive",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_profile_id", sa.Integer(), nullable=False),
        sa.Column("job_title", sa.String(length=120), nullable=False),
        sa.Column("job_description", sa.Text(), nullable=False),
        sa.Column("eligibility_branches", sa.Text(), nullable=False),
        sa.Column("eligibility_branch", sa.String(length=80), nullable=False),
        sa.Column("eligibility_cgpa", sa.Float(), nullable=False),
        sa.Column("eligibility_year", sa.Integer(), nullable=False),
        sa.Column("eligibility_year_mode", sa.String(length=10), nullable=False),
        sa.Column(
            "application_deadline",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["company_profile_id"],
            ["company_profile.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "application",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("student_profile_id", sa.Integer(), nullable=False),
        sa.Column("drive_id", sa.Integer(), nullable=False),
        sa.Column("application_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("resume_path", sa.String(length=255), nullable=True),
        sa.Column(
            "interview_datetime",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column("interview_location", sa.String(length=255), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("selection_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("offer_status", sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(["drive_id"], ["placement_drive.id"]),
        sa.ForeignKeyConstraint(
            ["student_profile_id"],
            ["student_profile.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "student_profile_id",
            "drive_id",
            name="uq_student_drive",
        ),
    )


def downgrade():
    """Remove the initial Meridian PostgreSQL schema."""

    op.drop_table("application")
    op.drop_table("placement_drive")

    op.drop_index(
        "ix_export_job_task_id",
        table_name="export_job",
    )

    op.drop_table("export_job")
    op.drop_table("student_profile")
    op.drop_table("company_profile")
    op.drop_table("user")
    op.drop_table("reminder_run")
