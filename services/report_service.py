import calendar
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from flask import current_app
from sqlalchemy import func

from models import Application, PlacementDrive


def _configured_timezone():
    try:
        timezone_name = current_app.config.get("CELERY_TIMEZONE", "Asia/Kolkata")
    except RuntimeError:
        timezone_name = "Asia/Kolkata"
    try:
        return ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError):
        return timezone.utc


def _get_previous_month(reference_date=None):
    local_timezone = _configured_timezone()
    if reference_date is None:
        reference_date = datetime.now(local_timezone)
    elif reference_date.tzinfo is None:
        reference_date = reference_date.replace(tzinfo=local_timezone)
    else:
        reference_date = reference_date.astimezone(local_timezone)
    month = reference_date.month - 1
    year = reference_date.year
    if month == 0:
        month = 12
        year -= 1
    return year, month


def _month_date_range(year, month):
    local_timezone = _configured_timezone()
    start_local = datetime(year, month, 1, tzinfo=local_timezone)
    last_day = calendar.monthrange(year, month)[1]
    if month == 12:
        end_local = datetime(year + 1, 1, 1, tzinfo=local_timezone)
    else:
        end_local = datetime(year, month + 1, 1, tzinfo=local_timezone)
    return start_local.astimezone(timezone.utc), end_local.astimezone(timezone.utc)


def collect_monthly_stats(year, month):
    start, end = _month_date_range(year, month)

    drives_conducted = PlacementDrive.query.filter(
        PlacementDrive.created_at >= start,
        PlacementDrive.created_at < end,
        PlacementDrive.status.in_(["Approved", "Closed"]),
    ).count()

    students_applied = Application.query.filter(
        Application.application_date >= start,
        Application.application_date < end,
    ).with_entities(func.count(func.distinct(Application.student_profile_id))).scalar()

    students_selected = Application.query.filter(
        Application.selection_date >= start,
        Application.selection_date < end,
        Application.status == "Selected",
    ).with_entities(func.count(func.distinct(Application.student_profile_id))).scalar()

    offers_accepted = Application.query.filter(
        Application.selection_date >= start,
        Application.selection_date < end,
        Application.status == "Selected",
        Application.offer_status == "Accepted",
    ).count()

    offers_declined = Application.query.filter(
        Application.selection_date >= start,
        Application.selection_date < end,
        Application.status == "Selected",
        Application.offer_status == "Declined",
    ).count()

    offers_auto_declined = Application.query.filter(
        Application.selection_date >= start,
        Application.selection_date < end,
        Application.status == "Selected",
        Application.offer_status == "Auto Declined",
    ).count()

    offers_pending = Application.query.filter(
        Application.selection_date >= start,
        Application.selection_date < end,
        Application.status == "Selected",
        Application.offer_status == "Pending",
    ).count()

    month_name = calendar.month_name[month]

    return {
        "year": year,
        "month": month,
        "month_name": f"{month_name} {year}",
        "drives_conducted": drives_conducted,
        "students_applied": students_applied,
        "students_selected": students_selected,
        "offers_accepted": offers_accepted,
        "offers_declined": offers_declined,
        "offers_auto_declined": offers_auto_declined,
        "offers_pending": offers_pending,
    }


def build_monthly_report_html(stats):
    month_name = stats["month_name"]
    drives = stats["drives_conducted"]
    applied = stats["students_applied"]
    selected = stats["students_selected"]
    accepted = stats.get("offers_accepted", 0)
    declined = stats.get("offers_declined", 0)
    auto_declined = stats.get("offers_auto_declined", 0)
    pending = stats.get("offers_pending", 0)

    selection_rate = 0.0
    if applied > 0:
        selection_rate = (selected / applied) * 100

    acceptance_rate = 0.0
    if selected > 0:
        acceptance_rate = (accepted / selected) * 100

    html = (
        "<!DOCTYPE html>"
        "<html><head><meta charset='utf-8'></head>"
        "<body style='font-family: Arial, sans-serif; margin: 20px;'>"
        f"<h2 style='color: #2c3e50;'>Monthly Placement Activity Report — {month_name}</h2>"
        "<hr style='border: 1px solid #bdc3c7;'>"
        "<table style='width: 100%; border-collapse: collapse; margin-top: 20px;'>"
        "<tr style='background-color: #3498db; color: white;'>"
        "<th style='padding: 12px; text-align: left;'>Metric</th>"
        "<th style='padding: 12px; text-align: right;'>Count</th>"
        "</tr>"
        f"<tr style='background-color: #ecf0f1;'><td style='padding: 10px;'>Drives Conducted</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{drives}</td></tr>"
        f"<tr><td style='padding: 10px;'>Students Applied</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{applied}</td></tr>"
        f"<tr style='background-color: #ecf0f1;'><td style='padding: 10px;'>Students Selected</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{selected}</td></tr>"
        f"<tr><td style='padding: 10px;'>Selection Rate</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{selection_rate:.1f}%</td></tr>"
        f"<tr style='background-color: #ecf0f1;'><td style='padding: 10px;'>Offers Accepted</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{accepted}</td></tr>"
        f"<tr><td style='padding: 10px;'>Offers Declined</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{declined}</td></tr>"
        f"<tr style='background-color: #ecf0f1;'><td style='padding: 10px;'>Offers Auto Declined</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{auto_declined}</td></tr>"
        f"<tr><td style='padding: 10px;'>Offers Pending</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{pending}</td></tr>"
        f"<tr style='background-color: #ecf0f1;'><td style='padding: 10px;'>Acceptance Rate</td>"
        f"<td style='padding: 10px; text-align: right; font-weight: bold;'>{acceptance_rate:.1f}%</td></tr>"
        "</table>"
        "<hr style='border: 1px solid #bdc3c7; margin-top: 20px;'>"
        "<p style='color: #7f8c8d; font-size: 12px;'>"
        "This report was generated automatically by the Placement Portal.</p>"
        "</body></html>"
    )
    return html
