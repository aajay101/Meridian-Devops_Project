from datetime import datetime, timezone

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


def utc_now():
    return datetime.now(timezone.utc)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(30), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    student_profile = db.relationship(
        "StudentProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )
    company_profile = db.relationship(
        "CompanyProfile",
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False,
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class StudentProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    branch = db.Column(db.String(80), nullable=False)
    cgpa = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    resume_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    user = db.relationship("User", back_populates="student_profile")
    applications = db.relationship(
        "Application",
        back_populates="student_profile",
        cascade="all, delete-orphan",
    )


class CompanyProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    hr_contact = db.Column(db.String(120), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    approval_status = db.Column(db.String(30), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    user = db.relationship("User", back_populates="company_profile")
    placement_drives = db.relationship(
        "PlacementDrive",
        back_populates="company_profile",
        cascade="all, delete-orphan",
    )


class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("company_profile.id"),
        nullable=False,
    )
    job_title = db.Column(db.String(120), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    eligibility_branch = db.Column(db.String(80), nullable=False)
    eligibility_cgpa = db.Column(db.Float, nullable=False)
    eligibility_year = db.Column(db.Integer, nullable=False)
    application_deadline = db.Column(db.DateTime(timezone=True), nullable=False)
    status = db.Column(db.String(30), default="Pending", nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utc_now, nullable=False)

    company_profile = db.relationship("CompanyProfile", back_populates="placement_drives")
    applications = db.relationship(
        "Application",
        back_populates="drive",
        cascade="all, delete-orphan",
    )


class Application(db.Model):
    __table_args__ = (
        db.UniqueConstraint("student_profile_id", "drive_id", name="uq_student_drive"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_profile_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profile.id"),
        nullable=False,
    )
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
    application_date = db.Column(
        db.DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    status = db.Column(db.String(30), default="Applied", nullable=False)
    interview_datetime = db.Column(db.DateTime(timezone=True), nullable=True)
    interview_location = db.Column(db.String(255), nullable=True)
    remarks = db.Column(db.Text, nullable=True)
    selection_date = db.Column(db.DateTime(timezone=True), nullable=True)

    student_profile = db.relationship("StudentProfile", back_populates="applications")
    drive = db.relationship("PlacementDrive", back_populates="applications")
