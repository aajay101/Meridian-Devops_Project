"""
CSV export business logic.

Provides a single public function to export student application history to CSV.
"""
import csv
import glob
import logging
import os
import time
import uuid
from datetime import datetime

from flask import current_app

from models import Application, CompanyProfile, PlacementDrive, db

logger = logging.getLogger(__name__)

EXPORT_RETENTION_SECONDS = 7 * 24 * 60 * 60  # 7 days

CSV_FIELDNAMES = [
    "Student ID",
    "Student Name",
    "Company Name",
    "Drive Title",
    "Application Status",
    "Offer Status",
    "Application Date",
    "Selection Date",
]


def export_student_history(student_profile_id):
    """
    Export all placement applications for a student to a CSV file.

    Parameters:
        student_profile_id (int)

    Returns:
        dict {
            "filename": str,
            "filepath": str,
            "record_count": int,
            "download_url": str
        }

    Raises:
        ValueError — if student_profile_id is invalid
        IOError — if file write fails
    """
    logger.info("Export started for student_profile_id=%s", student_profile_id)
    applications = _query_application_history(student_profile_id)
    logger.info("Queried %d application(s) for student_profile_id=%s", len(applications), student_profile_id)
    filename = _build_csv_filename(student_profile_id)
    filepath = _write_csv_file(filename, applications)
    download_url = _build_download_url(filename)
    logger.info("CSV created: %s (%d records)", filename, len(applications))
    return {
        "filename": filename,
        "filepath": filepath,
        "record_count": len(applications),
        "download_url": download_url,
    }


def _build_download_url(filename):
    """
    Construct download URL for exported CSV.

    Parameters:
        filename (str)

    Returns:
        str — e.g. "http://127.0.0.1:5000/static/exports/export_5_1719403200.csv"
    """
    base_url = current_app.config.get("APP_BASE_URL", "http://127.0.0.1:5000")
    return f"{base_url}/static/exports/{filename}"


def _query_application_history(student_profile_id):
    """
    Query all placement applications for a student with JOINs.

    Parameters:
        student_profile_id (int)

    Returns:
        list of Row (Application, PlacementDrive, CompanyProfile)
    """
    results = (
        db.session.query(Application, PlacementDrive, CompanyProfile)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .join(CompanyProfile, PlacementDrive.company_profile_id == CompanyProfile.id)
        .filter(Application.student_profile_id == student_profile_id)
        .order_by(Application.application_date.asc())
        .all()
    )
    return results


def _build_csv_filename(student_profile_id):
    """
    Construct a unique CSV filename.

    Parameters:
        student_profile_id (int)

    Returns:
        str — e.g. "export_5_1719403200.csv"
    """
    timestamp = int(datetime.now().timestamp())
    return f"export_{student_profile_id}_{timestamp}_{uuid.uuid4().hex[:8]}.csv"


def _write_csv_file(filename, applications):
    """
    Write application data to a CSV file in static/exports/.

    Parameters:
        filename (str) — CSV filename
        applications (list of Row) — output of _query_application_history()

    Returns:
        str — absolute filepath

    Raises:
        IOError — if file write fails
    """
    export_dir = os.path.join(current_app.root_path, "static", "exports")
    os.makedirs(export_dir, exist_ok=True)
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=CSV_FIELDNAMES)
        writer.writeheader()
        for app_record, drive, company in applications:
            selection_date = ""
            if app_record.selection_date:
                selection_date = app_record.selection_date.strftime("%Y-%m-%d")
            student_name = app_record.student_profile.name if app_record.student_profile else ""
            offer_status = app_record.offer_status or ""
            app_date = ""
            if app_record.application_date:
                app_date = app_record.application_date.strftime("%Y-%m-%d")
            writer.writerow({
                "Student ID": app_record.student_profile_id,
                "Student Name": student_name,
                "Company Name": company.company_name,
                "Drive Title": drive.job_title,
                "Application Status": app_record.status,
                "Offer Status": offer_status,
                "Application Date": app_date,
                "Selection Date": selection_date,
            })

    return filepath


def cleanup_old_exports():
    """Delete export CSVs older than EXPORT_RETENTION_SECONDS.

    Only removes files matching export_*.csv in the static/exports/ directory.
    Never touches resumes, uploads, or unrelated files.
    Silently ignores permission errors or missing directories.
    """
    try:
        export_dir = os.path.join(current_app.root_path, "static", "exports")
    except RuntimeError:
        return

    if not os.path.isdir(export_dir):
        return

    now = time.time()
    removed = 0
    for filepath in glob.glob(os.path.join(export_dir, "export_*.csv")):
        try:
            if now - os.path.getmtime(filepath) > EXPORT_RETENTION_SECONDS:
                os.remove(filepath)
                removed += 1
        except OSError:
            continue

    if removed:
        logger.info("Cleaned up %d old export CSV(s)", removed)
