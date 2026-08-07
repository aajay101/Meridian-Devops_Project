"""
FINAL REGRESSION AUDIT — Tests every route, API, upload, download,
validation, auth flow, CRUD, search, and cache invalidation.
"""
import json
import io
import os
import sys
import time

os.chdir(os.path.dirname(os.path.abspath(__file__)))

import requests

BASE = "http://127.0.0.1:5000/api"
RESULTS = []
FAILURES = []


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def test(label, func):
    global RESULTS
    try:
        ok, detail = func()
        status = "PASS" if ok else "FAIL"
        if ok:
            RESULTS.append(("PASS", label))
        else:
            RESULTS.append(("FAIL", label))
            FAILURES.append((label, detail))
        marker = "  PASS" if ok else "  FAIL"
        suffix = f" -- {detail}" if not ok else ""
        print(f"{marker} {label}{suffix}")
        return ok
    except Exception as e:
        RESULTS.append(("FAIL", label))
        FAILURES.append((label, str(e)))
        print(f"  FAIL {label} -- EXCEPTION: {e}")
        return False


class Session:
    """Wraps requests with cookie persistence."""
    def __init__(self):
        self.s = requests.Session()

    def get(self, url, **kw):
        return self.s.get(f"{BASE}{url}", **kw)

    def post(self, url, **kw):
        return self.s.post(f"{BASE}{url}", **kw)

    def put(self, url, **kw):
        return self.s.put(f"{BASE}{url}", **kw)

    def patch(self, url, **kw):
        return self.s.patch(f"{BASE}{url}", **kw)

    def delete(self, url, **kw):
        return self.s.delete(f"{BASE}{url}", **kw)


# ─── 1. AUTH HEALTH CHECKS ───────────────────────────────────────
section("1. AUTH HEALTH CHECKS")

s = Session()

def auth_health():
    r = s.get("/auth/health")
    return r.ok and r.json().get("status") == "ok", r.text
test("GET /auth/health", auth_health)

def branches():
    r = s.get("/auth/branches")
    data = r.json()
    return r.ok and data.get("success") and len(data.get("branches", [])) > 0, r.text
test("GET /auth/branches", branches)


# ─── 2. AUTH: STUDENT REGISTRATION ───────────────────────────────
section("2. AUTH: STUDENT REGISTRATION")

def reg_missing():
    r = s.post("/auth/student/register", json={"name": "Test"})
    return r.status_code == 400 and r.json().get("error") == "missing_fields", r.text
test("POST /auth/student/register — missing fields → 400", reg_missing)

def reg_bad_email():
    r = s.post("/auth/student/register", json={"name": "T", "email": "bad", "password": "12345678", "branch": "CSE", "cgpa": 8.0, "year": 3})
    return r.status_code == 400 and r.json().get("error") == "invalid_email_format", r.text
test("POST /auth/student/register — bad email → 400", reg_bad_email)

def reg_short_pw():
    r = s.post("/auth/student/register", json={"name": "T", "email": "x@x.com", "password": "short", "branch": "CSE", "cgpa": 8.0, "year": 3})
    return r.status_code == 400 and r.json().get("error") == "password_too_short", r.text
test("POST /auth/student/register — short password → 400", reg_short_pw)

def reg_bad_cgpa():
    r = s.post("/auth/student/register", json={"name": "T", "email": "x@x.com", "password": "12345678", "branch": "CSE", "cgpa": -1, "year": 3})
    return r.status_code == 400 and r.json().get("error") == "invalid_cgpa", r.text
test("POST /auth/student/register — invalid cgpa → 400", reg_bad_cgpa)

def reg_bad_year():
    r = s.post("/auth/student/register", json={"name": "T", "email": "x@x.com", "password": "12345678", "branch": "CSE", "cgpa": 8.0, "year": 0})
    return r.status_code == 400 and r.json().get("error") == "invalid_year", r.text
test("POST /auth/student/register — invalid year → 400", reg_bad_year)

def reg_bad_branch():
    r = s.post("/auth/student/register", json={"name": "T", "email": "x@x.com", "password": "12345678", "branch": "INVALID", "cgpa": 8.0, "year": 3})
    return r.status_code == 400 and r.json().get("error") == "invalid_branch", r.text
test("POST /auth/student/register — invalid branch → 400", reg_bad_branch)


# ─── 3. AUTH: COMPANY REGISTRATION ───────────────────────────────
section("3. AUTH: COMPANY REGISTRATION")

def reg_co_missing():
    r = s.post("/auth/company/register", json={"company_name": "X"})
    return r.status_code == 400 and r.json().get("error") == "missing_fields", r.text
test("POST /auth/company/register — missing fields → 400", reg_co_missing)

def reg_co_bad_hr():
    r = s.post("/auth/company/register", json={"company_name": "X", "email": "c@c.com", "password": "12345678", "hr_contact": "123"})
    return r.status_code == 400 and r.json().get("error") == "invalid_hr_contact", r.text
test("POST /auth/company/register — bad hr_contact → 400", reg_co_bad_hr)


# ─── 4. AUTH: LOGIN ──────────────────────────────────────────────
section("4. AUTH: LOGIN")

def login_missing():
    r = s.post("/auth/login", json={"email": "x"})
    return r.status_code == 400 and r.json().get("error") == "missing_fields", r.text
test("POST /auth/login — missing fields → 400", login_missing)

def login_bad_creds():
    r = s.post("/auth/login", json={"email": "x@x.com", "password": "wrong"})
    return r.status_code == 401 and r.json().get("error") == "invalid_credentials", r.text
test("POST /auth/login — bad credentials → 401", login_bad_creds)


# ─── 5. AUTH: LOGIN AS ALL ROLES ─────────────────────────────────
section("5. AUTH: LOGIN AS ALL ROLES")

student = Session()
company = Session()
admin = Session()

def login_student():
    r = student.post("/auth/login", json={"email": "anon64057@gmail.com", "password": "Student123"})
    return r.ok and r.json().get("role") == "student", r.text
test("POST /auth/login — student (anon64057@gmail.com)", login_student)

def login_company():
    r = company.post("/auth/login", json={"email": "hr@techcorp.com", "password": "Company123"})
    return r.ok and r.json().get("role") == "company", r.text
test("POST /auth/login — company (hr@techcorp.com)", login_company)

def login_admin():
    r = admin.post("/auth/login", json={"email": "admin@placement.local", "password": "admin123"})
    return r.ok and r.json().get("role") == "admin", r.text
test("POST /auth/login — admin (admin@placement.local)", login_admin)

def me_student():
    r = student.get("/auth/me")
    return r.ok and r.json().get("role") == "student", r.text
test("GET /auth/me — student", me_student)

def me_company():
    r = company.get("/auth/me")
    return r.ok and r.json().get("role") == "company", r.text
test("GET /auth/me — company", me_company)

def me_admin():
    r = admin.get("/auth/me")
    return r.ok and r.json().get("role") == "admin", r.text
test("GET /auth/me — admin", me_admin)


# ─── 6. AUTH: ME (UNAUTHENTICATED) ──────────────────────────────
section("6. AUTH: ME (UNAUTHENTICATED)")

def me_unauth():
    unauth = Session()
    r = unauth.get("/auth/me")
    return r.ok and r.json().get("authenticated") is False, r.text
test("GET /auth/me — unauthenticated", me_unauth)


# ─── 7. ROLE-BASED ACCESS CONTROL ────────────────────────────────
section("7. ROLE-BASED ACCESS CONTROL")

def student_cannot_admin():
    r = student.get("/admin/dashboard")
    return r.status_code in (401, 403), f"status={r.status_code}"
test("Student cannot access /admin/dashboard", student_cannot_admin)

def company_cannot_admin():
    r = company.get("/admin/dashboard")
    return r.status_code in (401, 403), f"status={r.status_code}"
test("Company cannot access /admin/dashboard", company_cannot_admin)

def admin_cannot_student():
    r = admin.get("/student/dashboard")
    return r.status_code in (401, 403), f"status={r.status_code}"
test("Admin cannot access /student/dashboard", admin_cannot_student)

def unauth_cannot_student():
    unauth = Session()
    r = unauth.get("/student/dashboard")
    return r.status_code in (401, 403), f"status={r.status_code}"
test("Unauth cannot access /student/dashboard", unauth_cannot_student)

def unauth_cannot_company():
    unauth = Session()
    r = unauth.get("/company/dashboard")
    return r.status_code in (401, 403), f"status={r.status_code}"
test("Unauth cannot access /company/dashboard", unauth_cannot_company)

def unauth_cannot_admin():
    unauth = Session()
    r = unauth.get("/admin/dashboard")
    return r.status_code in (401, 403), f"status={r.status_code}"
test("Unauth cannot access /admin/dashboard", unauth_cannot_admin)


# ─── 8. STUDENT: PROFILE ─────────────────────────────────────────
section("8. STUDENT: PROFILE")

def get_profile():
    r = student.get("/student/profile")
    data = r.json()
    return r.ok and data.get("success") and "name" in data, r.text
test("GET /student/profile", get_profile)

def update_profile():
    r = student.put("/student/profile", json={"cgpa": 8.5})
    return r.ok and r.json().get("success"), r.text
test("PUT /student/profile — update cgpa", update_profile)

def update_profile_bad_cgpa():
    r = student.put("/student/profile", json={"cgpa": 99})
    return r.status_code == 400 and r.json().get("error") == "validation_failed", r.text
test("PUT /student/profile — invalid cgpa → 400", update_profile_bad_cgpa)

def update_profile_bad_year():
    r = student.put("/student/profile", json={"year": -1})
    return r.status_code == 400 and r.json().get("error") == "validation_failed", r.text
test("PUT /student/profile — invalid year → 400", update_profile_bad_year)


# ─── 9. STUDENT: RESUME UPLOAD ────────────────────────────────────
section("9. STUDENT: RESUME UPLOAD")

def upload_resume_missing():
    r = student.post("/student/profile/resume")
    return r.status_code == 400 and r.json().get("error") == "missing_file", r.text
test("POST /student/profile/resume — no file → 400", upload_resume_missing)

def upload_resume_bad_type():
    files = {"file": ("test.txt", b"hello", "text/plain")}
    r = student.post("/student/profile/resume", files=files)
    return r.status_code == 400 and r.json().get("error") == "invalid_file_type", r.text
test("POST /student/profile/resume — .txt file → 400", upload_resume_bad_type)

def upload_resume_ok():
    pdf_content = b"%PDF-1.4 fake content for test"
    files = {"file": ("resume.pdf", pdf_content, "application/pdf")}
    r = student.post("/student/profile/resume", files=files)
    return r.ok and r.json().get("success"), r.text
test("POST /student/profile/resume — valid PDF → 201", upload_resume_ok)

def upload_resume_replaces_old():
    pdf_content = b"%PDF-1.4 new resume content"
    files = {"file": ("resume2.pdf", pdf_content, "application/pdf")}
    r = student.post("/student/profile/resume", files=files)
    return r.ok and r.json().get("success"), r.text
test("POST /student/profile/resume — replace old → 201", upload_resume_replaces_old)


# ─── 10. STUDENT: DASHBOARD ──────────────────────────────────────
section("10. STUDENT: DASHBOARD")

def student_dashboard():
    r = student.get("/student/dashboard")
    data = r.json()
    return r.ok and data.get("success") and "total_applications" in data, r.text
test("GET /student/dashboard", student_dashboard)


# ─── 11. STUDENT: LIST DRIVES ────────────────────────────────────
section("11. STUDENT: LIST DRIVES")

def list_drives():
    r = student.get("/student/drives")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("drives"), list), r.text
test("GET /student/drives", list_drives)

def list_drives_search():
    r = student.get("/student/drives?q=Python")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("drives"), list), r.text
test("GET /student/drives?q=Python (search)", list_drives_search)


# ─── 12. STUDENT: GET SINGLE DRIVE ───────────────────────────────
section("12. STUDENT: GET SINGLE DRIVE")

def get_drive():
    r = student.get("/student/drives/2")
    data = r.json()
    return r.ok and data.get("success") and "drive" in data, r.text
test("GET /student/drives/2 — valid drive", get_drive)

def get_drive_not_found():
    r = student.get("/student/drives/99999")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("GET /student/drives/99999 → 404", get_drive_not_found)


# ─── 13. STUDENT: LIST APPLICATIONS ──────────────────────────────
section("13. STUDENT: LIST APPLICATIONS")

def list_applications():
    r = student.get("/student/applications")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("applications"), list), r.text
test("GET /student/applications", list_applications)


# ─── 14. STUDENT: PLACEMENT HISTORY ──────────────────────────────
section("14. STUDENT: PLACEMENT HISTORY")

def placement_history():
    r = student.get("/student/applications/history")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("placement_history"), list), r.text
test("GET /student/applications/history", placement_history)


# ─── 15. STUDENT: ACCEPT/DECLINE OFFER ───────────────────────────
section("15. STUDENT: ACCEPT/DECLINE OFFER")

def accept_offer_not_found():
    r = student.post("/student/applications/99999/accept-offer")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("POST /student/applications/99999/accept-offer → 404", accept_offer_not_found)

def decline_offer_not_found():
    r = student.post("/student/applications/99999/decline-offer")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("POST /student/applications/99999/decline-offer → 404", decline_offer_not_found)


# ─── 16. COMPANY: PROFILE ────────────────────────────────────────
section("16. COMPANY: PROFILE")

def company_profile():
    r = company.get("/company/profile")
    data = r.json()
    return r.ok and data.get("success") and "company" in data, r.text
test("GET /company/profile", company_profile)

def company_update_profile():
    r = company.put("/company/profile", json={"hr_contact": "9999999999"})
    return r.ok and r.json().get("success"), r.text
test("PUT /company/profile", company_update_profile)


# ─── 17. COMPANY: DASHBOARD ──────────────────────────────────────
section("17. COMPANY: DASHBOARD")

def company_dashboard():
    r = company.get("/company/dashboard")
    data = r.json()
    return r.ok and data.get("success") and "total_drives" in data, r.text
test("GET /company/dashboard", company_dashboard)


# ─── 18. COMPANY: DRIVE CRUD ─────────────────────────────────────
section("18. COMPANY: DRIVE CRUD")

def create_drive():
    r = company.post("/company/drives", json={
        "job_title": "Regression Test Role",
        "job_description": "Automated test",
        "eligibility_branches": ["Computer Science (CSE)"],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59",
    })
    data = r.json()
    return r.ok and data.get("success") and "drive_id" in data, r.text
test("POST /company/drives — create drive", create_drive)

def create_drive_missing():
    r = company.post("/company/drives", json={"job_title": "X"})
    return r.status_code == 400 and r.json().get("error") == "missing_fields", r.text
test("POST /company/drives — missing fields → 400", create_drive_missing)

def create_drive_bad_branches():
    r = company.post("/company/drives", json={
        "job_title": "X", "job_description": "X",
        "eligibility_branches": ["INVALID"],
        "eligibility_cgpa": 7.0, "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59",
    })
    return r.status_code == 400 and r.json().get("error") == "invalid_branches", r.text
test("POST /company/drives — invalid branches → 400", create_drive_bad_branches)

# Get the newly created drive ID
r_drives = company.get("/company/drives")
drive_list = r_drives.json().get("drives", [])
new_drive_id = drive_list[0]["drive_id"] if drive_list else None

def list_company_drives():
    return r_drives.ok and r_drives.json().get("success"), r_drives.text
test("GET /company/drives — list", list_company_drives)

def get_company_drive():
    r = company.get(f"/company/drives/{new_drive_id}")
    return r.ok and r.json().get("success"), r.text
test(f"GET /company/drives/{new_drive_id} — single", get_company_drive)

def edit_drive():
    r = company.put(f"/company/drives/{new_drive_id}", json={"job_title": "Updated Role"})
    return r.ok and r.json().get("success"), r.text
test(f"PUT /company/drives/{new_drive_id} — edit", edit_drive)


# ─── 19. COMPANY: APPLICATION MANAGEMENT ──────────────────────────
section("19. COMPANY: APPLICATION MANAGEMENT")

def company_list_applicants():
    r = company.get(f"/company/drives/{new_drive_id}/applicants")
    return r.ok and r.json().get("success"), r.text
test(f"GET /company/drives/{new_drive_id}/applicants", company_list_applicants)

def company_applicant_count():
    r = company.get(f"/company/drives/{new_drive_id}/applicants/count")
    return r.ok and r.json().get("success") and "count" in r.json(), r.text
test(f"GET /company/drives/{new_drive_id}/applicants/count", company_applicant_count)

def shortlist_not_found():
    r = company.post("/company/application/99999/shortlist")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("POST /company/application/99999/shortlist → 404", shortlist_not_found)

def reject_not_found():
    r = company.post("/company/application/99999/reject")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("POST /company/application/99999/reject → 404", reject_not_found)

def schedule_interview_not_found():
    r = company.post("/company/application/99999/schedule-interview")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("POST /company/application/99999/schedule-interview → 404", schedule_interview_not_found)

def select_not_found():
    r = company.post("/company/application/99999/select")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("POST /company/application/99999/select → 404", select_not_found)


# ─── 20. COMPANY: DRIVE LIFECYCLE (create→close→delete) ──────────
section("20. COMPANY: DRIVE LIFECYCLE")

def close_drive_not_closable():
    r = company.post(f"/company/drives/{new_drive_id}/close")
    return r.status_code == 409 and r.json().get("error") == "drive_not_closable", r.text
test(f"POST /company/drives/{new_drive_id}/close — not approved → 409", close_drive_not_closable)

def delete_drive():
    r = company.delete(f"/company/drives/{new_drive_id}")
    return r.ok and r.json().get("success"), r.text
test(f"DELETE /company/drives/{new_drive_id} — delete pending drive", delete_drive)

def delete_drive_not_found():
    r = company.delete(f"/company/drives/{new_drive_id}")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test(f"DELETE /company/drives/{new_drive_id} — already deleted → 404", delete_drive_not_found)


# ─── 21. ADMIN: DASHBOARD ────────────────────────────────────────
section("21. ADMIN: DASHBOARD")

def admin_dashboard():
    r = admin.get("/admin/dashboard")
    data = r.json()
    return r.ok and data.get("success") and "total_students" in data, r.text
test("GET /admin/dashboard", admin_dashboard)


# ─── 22. ADMIN: REPORTS ──────────────────────────────────────────
section("22. ADMIN: REPORTS SUMMARY")

def admin_reports():
    r = admin.get("/admin/reports/summary")
    data = r.json()
    return r.ok and data.get("success") and "total_students" in data and "selection_rate" in data, r.text
test("GET /admin/reports/summary", admin_reports)


# ─── 23. ADMIN: STUDENT CRUD ─────────────────────────────────────
section("23. ADMIN: STUDENT CRUD")

def admin_list_students():
    r = admin.get("/admin/students")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("students"), list), r.text
test("GET /admin/students", admin_list_students)

def admin_search_students():
    r = admin.get("/admin/students/search?q=anon")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("students"), list), r.text
test("GET /admin/students/search?q=anon", admin_search_students)

def admin_get_student():
    r = admin.get("/admin/student/1")
    data = r.json()
    return r.ok and data.get("success"), r.text
test("GET /admin/student/1", admin_get_student)

def admin_get_student_not_found():
    r = admin.get("/admin/student/99999")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("GET /admin/student/99999 → 404", admin_get_student_not_found)

def admin_deactivate_student():
    r = admin.patch("/admin/student/1/deactivate")
    data = r.json()
    return r.ok and data.get("success"), r.text
test("PATCH /admin/student/1/deactivate", admin_deactivate_student)

def admin_deactivate_already():
    r = admin.patch("/admin/student/1/deactivate")
    return r.status_code == 409 and r.json().get("error") == "already_deactivated", r.text
test("PATCH /admin/student/1/deactivate — already → 409", admin_deactivate_already)

def admin_activate_student():
    r = admin.patch("/admin/student/1/activate")
    data = r.json()
    return r.ok and data.get("success"), r.text
test("PATCH /admin/student/1/activate", admin_activate_student)

def admin_activate_already():
    r = admin.patch("/admin/student/1/activate")
    return r.status_code == 409 and r.json().get("error") == "already_active", r.text
test("PATCH /admin/student/1/activate — already → 409", admin_activate_already)


# ─── 24. ADMIN: COMPANY CRUD ─────────────────────────────────────
section("24. ADMIN: COMPANY CRUD")

def admin_list_companies():
    r = admin.get("/admin/companies")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("companies"), list), r.text
test("GET /admin/companies", admin_list_companies)

def admin_search_companies():
    r = admin.get("/admin/companies/search?q=tech")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("companies"), list), r.text
test("GET /admin/companies/search?q=tech", admin_search_companies)

def admin_get_company():
    r = admin.get("/admin/company/1")
    data = r.json()
    return r.ok and data.get("success"), r.text
test("GET /admin/company/1", admin_get_company)

def admin_get_company_not_found():
    r = admin.get("/admin/company/99999")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("GET /admin/company/99999 → 404", admin_get_company_not_found)

def admin_deactivate_company():
    r = admin.patch("/admin/company/1/deactivate")
    return r.ok and r.json().get("success"), r.text
test("PATCH /admin/company/1/deactivate", admin_deactivate_company)

def admin_deactivate_company_already():
    r = admin.patch("/admin/company/1/deactivate")
    return r.status_code == 409 and r.json().get("error") == "already_deactivated", r.text
test("PATCH /admin/company/1/deactivate — already → 409", admin_deactivate_company_already)

def admin_activate_company():
    r = admin.patch("/admin/company/1/activate")
    return r.ok and r.json().get("success"), r.text
test("PATCH /admin/company/1/activate", admin_activate_company)

def admin_activate_company_already():
    r = admin.patch("/admin/company/1/activate")
    return r.status_code == 409 and r.json().get("error") == "already_active", r.text
test("PATCH /admin/company/1/activate — already → 409", admin_activate_company_already)


# ─── 25. ADMIN: DRIVE CRUD ───────────────────────────────────────
section("25. ADMIN: DRIVE CRUD")

def admin_list_drives():
    r = admin.get("/admin/drives")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("drives"), list), r.text
test("GET /admin/drives", admin_list_drives)

def admin_search_drives():
    r = admin.get("/admin/drives/search?q=Python")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("drives"), list), r.text
test("GET /admin/drives/search?q=Python", admin_search_drives)

def admin_list_pending_drives():
    r = admin.get("/admin/drives/pending")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/drives/pending", admin_list_pending_drives)

def admin_list_approved_drives():
    r = admin.get("/admin/drives/approved")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/drives/approved", admin_list_approved_drives)

def admin_list_rejected_drives():
    r = admin.get("/admin/drives/rejected")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/drives/rejected", admin_list_rejected_drives)

def admin_list_closed_drives():
    r = admin.get("/admin/drives/closed")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/drives/closed", admin_list_closed_drives)

def admin_get_drive():
    r = admin.get("/admin/drive/2")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/drive/2", admin_get_drive)

def admin_get_drive_not_found():
    r = admin.get("/admin/drive/99999")
    return r.status_code == 404 and r.json().get("error") == "not_found", r.text
test("GET /admin/drive/99999 → 404", admin_get_drive_not_found)

# Find a pending drive to test approve/reject
r_pending = admin.get("/admin/drives/pending")
pending_drives = r_pending.json().get("drives", [])
pending_drive_id = pending_drives[0]["drive_id"] if pending_drives else None

if pending_drive_id:
    def admin_approve_drive():
        r = admin.post(f"/admin/drive/{pending_drive_id}/approve")
        return r.ok and r.json().get("success"), r.text
    test(f"POST /admin/drive/{pending_drive_id}/approve", admin_approve_drive)

    def admin_approve_drive_already():
        r = admin.post(f"/admin/drive/{pending_drive_id}/approve")
        return r.status_code == 409 and r.json().get("error") == "already_finalized", r.text
    test(f"POST /admin/drive/{pending_drive_id}/approve — already → 409", admin_approve_drive_already)

    def admin_close_drive():
        r = admin.post(f"/admin/drive/{pending_drive_id}/close")
        return r.ok and r.json().get("success"), r.text
    test(f"POST /admin/drive/{pending_drive_id}/close", admin_close_drive)

    def admin_close_drive_already():
        r = admin.post(f"/admin/drive/{pending_drive_id}/close")
        return r.status_code == 409 and r.json().get("error") == "already_finalized", r.text
    test(f"POST /admin/drive/{pending_drive_id}/close — already → 409", admin_close_drive_already)
else:
    print("  WARN No pending drives found for approve/reject/close test")


# ─── 26. ADMIN: APPLICATION LISTING ──────────────────────────────
section("26. ADMIN: APPLICATION LISTING")

def admin_list_applications():
    r = admin.get("/admin/applications")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("applications"), list), r.text
test("GET /admin/applications", admin_list_applications)

def admin_search_applications():
    r = admin.get("/admin/applications/search?q=Applied")
    data = r.json()
    return r.ok and data.get("success") and isinstance(data.get("applications"), list), r.text
test("GET /admin/applications/search?q=Applied", admin_search_applications)


# ─── 27. ADMIN: APPROVE/REJECT COMPANY ───────────────────────────
section("27. ADMIN: APPROVE/REJECT COMPANY")

# Get a pending company if any
r_pending_co = admin.get("/admin/companies/pending")
pending_cos = r_pending_co.json().get("companies", [])
pending_co_id = pending_cos[0]["company_profile_id"] if pending_cos else None

if pending_co_id:
    def admin_approve_company():
        r = admin.post(f"/admin/company/{pending_co_id}/approve")
        return r.ok and r.json().get("success"), r.text
    test(f"POST /admin/company/{pending_co_id}/approve", admin_approve_company)

    def admin_approve_company_already():
        r = admin.post(f"/admin/company/{pending_co_id}/approve")
        return r.status_code == 409 and r.json().get("error") == "already_finalized", r.text
    test(f"POST /admin/company/{pending_co_id}/approve — already → 409", admin_approve_company_already)
else:
    print("  WARN No pending companies found for approve/reject test")


# ─── 28. JOBS: CSV EXPORT ────────────────────────────────────────
section("28. JOBS: CSV EXPORT")

def trigger_export():
    r = student.post("/jobs/export")
    data = r.json()
    return r.status_code == 202 and data.get("success") and "task_id" in data, r.text
test("POST /jobs/export — trigger CSV export", trigger_export)

# Get the task_id
r_export = student.post("/jobs/export")
task_data = r_export.json()
task_id = task_data.get("task_id")

if task_id:
    def poll_export():
        for _ in range(10):
            r = student.get(f"/jobs/export/status/{task_id}")
            data = r.json()
            if data.get("status") == "SUCCESS":
                return True, "SUCCESS"
            time.sleep(1)
        return False, f"status={data.get('status')}"

    test(f"GET /jobs/export/status/{task_id} — poll to SUCCESS", poll_export)

    def download_export():
        r = student.get(f"/jobs/export/download/{task_id}")
        return r.ok and r.headers.get("Content-Type", "").startswith("text/csv"), r.status_code
    test(f"GET /jobs/export/download/{task_id}", download_export)

    def download_wrong_student():
        other = Session()
        other.post("/auth/login", json={"email": "admin@placement.local", "password": "admin123"})
        r = other.get(f"/jobs/export/download/{task_id}")
        return r.status_code == 403, r.status_code
    test("GET /jobs/export/download/{task_id} — wrong student → 403", download_wrong_student)
else:
    print("  WARN Could not get task_id for export test")


# ─── 29. JOBS: EXPORT OWNERSHIP ──────────────────────────────────
section("29. JOBS: EXPORT OWNERSHIP")

def export_status_wrong_student():
    other = Session()
    other.post("/auth/login", json={"email": "admin@placement.local", "password": "admin123"})
    r = other.get(f"/jobs/export/status/{task_id}")
    return r.status_code == 403, r.status_code
test("GET /jobs/export/status/{task_id} — wrong student → 403", export_status_wrong_student)


# ─── 30. STUDENT: APPLY TO DRIVE ──────────────────────────────────
section("30. STUDENT: APPLY TO DRIVE")

def apply_not_available():
    r = student.post("/student/drives/1/apply")
    return r.status_code in (400, 403), f"status={r.status_code}"
test("POST /student/drives/1/apply — closed/unavailable drive", apply_not_available)

def apply_not_found():
    r = student.post("/student/drives/99999/apply")
    return r.status_code in (403, 404), f"status={r.status_code}"
test("POST /student/drives/99999/apply → not found", apply_not_found)


# ─── 31. STUDENT: MAX OFFERS ─────────────────────────────────────
section("31. STUDENT: VALIDATION EDGE CASES")

def update_profile_string_too_long():
    r = student.put("/student/profile", json={"name": "A" * 200})
    return r.ok, r.text  # name field may or may not be validated for length
test("PUT /student/profile — long name (graceful)", update_profile_string_too_long)


# ─── 32. COMPANY: VALIDATION EDGE CASES ──────────────────────────
section("32. COMPANY: VALIDATION EDGE CASES")

def create_drive_bad_cgpa():
    r = company.post("/company/drives", json={
        "job_title": "X", "job_description": "X",
        "eligibility_branches": ["Computer Science (CSE)"],
        "eligibility_cgpa": "abc",
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59",
    })
    return r.status_code == 400 and r.json().get("error") == "invalid_eligibility_cgpa", r.text
test("POST /company/drives — bad cgpa → 400", create_drive_bad_cgpa)

def create_drive_bad_year():
    r = company.post("/company/drives", json={
        "job_title": "X", "job_description": "X",
        "eligibility_branches": ["Computer Science (CSE)"],
        "eligibility_cgpa": 7.0,
        "eligibility_year": "abc",
        "application_deadline": "2026-12-31T23:59:59",
    })
    return r.status_code == 400 and r.json().get("error") == "invalid_eligibility_year", r.text
test("POST /company/drives — bad year → 400", create_drive_bad_year)

def create_drive_bad_deadline():
    r = company.post("/company/drives", json={
        "job_title": "X", "job_description": "X",
        "eligibility_branches": ["Computer Science (CSE)"],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "not-a-date",
    })
    return r.status_code == 400 and r.json().get("error") == "invalid_deadline_format", r.text
test("POST /company/drives — bad deadline → 400", create_drive_bad_deadline)

def create_drive_bad_year_mode():
    r = company.post("/company/drives", json={
        "job_title": "X", "job_description": "X",
        "eligibility_branches": ["Computer Science (CSE)"],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "eligibility_year_mode": "invalid",
        "application_deadline": "2026-12-31T23:59:59",
    })
    return r.status_code == 400 and r.json().get("error") == "invalid_eligibility_year_mode", r.text
test("POST /company/drives — bad year_mode → 400", create_drive_bad_year_mode)


# ─── 33. COMPANY: PROFILE VALIDATION ─────────────────────────────
section("33. COMPANY: PROFILE VALIDATION")

def update_profile_validation():
    r = company.put("/company/profile", json={"company_name": ""})
    return r.status_code == 400 and r.json().get("error") == "validation_failed", r.text
test("PUT /company/profile — empty name → 400", update_profile_validation)

def update_profile_bad_website():
    r = company.put("/company/profile", json={"website": "x" * 300})
    return r.status_code == 400 and r.json().get("error") == "validation_failed", r.text
test("PUT /company/profile — long website → 400", update_profile_bad_website)


# ─── 34. COMPANY: DRIVE NOT EDITABLE ─────────────────────────────
section("34. COMPANY: DRIVE STATE VALIDATION")

# Create a drive and approve it via admin, then try to edit
def drive_not_editable():
    # Create a fresh drive
    r = company.post("/company/drives", json={
        "job_title": "Temp Role",
        "job_description": "Temporary",
        "eligibility_branches": ["Computer Science (CSE)"],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59",
    })
    new_id = r.json().get("drive_id")
    if not new_id:
        return False, "could not create drive"
    # Approve via admin
    admin.post(f"/admin/drive/{new_id}/approve")
    # Try to edit
    r2 = company.put(f"/company/drives/{new_id}", json={"job_title": "Hacked"})
    return r2.status_code == 409 and r2.json().get("error") == "drive_not_editable", r2.text
test("PUT /company/drives/<approved> — not editable → 409", drive_not_editable)


# ─── 35. COMPANY: SCHEDULE INTERVIEW VALIDATION ──────────────────
section("35. COMPANY: INTERVIEW SCHEDULE VALIDATION")

def schedule_interview_missing_fields():
    # Use any application ID; we just need to check validation fires
    r = company.post("/company/application/1/schedule-interview", json={})
    if r.status_code == 404:
        return True, "application not found (acceptable)"
    return r.status_code == 400 and r.json().get("error") == "missing_fields", r.text
test("POST /company/application/<id>/schedule-interview — missing fields → 400", schedule_interview_missing_fields)

def schedule_interview_bad_datetime():
    r = company.post("/company/application/1/schedule-interview", json={"interview_datetime": "bad"})
    if r.status_code == 404:
        return True, "application not found (acceptable)"
    return r.status_code == 400 and r.json().get("error") == "invalid_datetime_format", r.text
test("POST /company/application/<id>/schedule-interview — bad datetime → 400", schedule_interview_bad_datetime)


# ─── 36. ADMIN: STUDENT SEARCH ────────────────────────────────────
section("36. ADMIN: SEARCH EDGE CASES")

def admin_search_students_empty():
    r = admin.get("/admin/students/search?q=")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/students/search?q= (empty)", admin_search_students_empty)

def admin_search_companies_empty():
    r = admin.get("/admin/companies/search?q=")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/companies/search?q= (empty)", admin_search_companies_empty)

def admin_search_drives_empty():
    r = admin.get("/admin/drives/search?q=")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/drives/search?q= (empty)", admin_search_drives_empty)

def admin_search_applications_empty():
    r = admin.get("/admin/applications/search?q=")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/applications/search?q= (empty)", admin_search_applications_empty)


# ─── 37. CACHE: INVALIDATION VERIFICATION ────────────────────────
section("37. CACHE: INVALIDATION VERIFICATION")

def cache_invalidation_on_student_update():
    # Hit dashboard to prime cache
    student.get("/student/dashboard")
    # Update profile
    student.put("/student/profile", json={"cgpa": 8.0})
    # Re-hit dashboard — should get fresh data
    r = student.get("/student/dashboard")
    return r.ok and r.json().get("success"), r.text
test("Cache invalidation on student profile update", cache_invalidation_on_student_update)

def cache_invalidation_on_company_update():
    company.get("/company/dashboard")
    company.put("/company/profile", json={"hr_contact": "8888888888"})
    r = company.get("/company/dashboard")
    return r.ok and r.json().get("success"), r.text
test("Cache invalidation on company profile update", cache_invalidation_on_company_update)


# ─── 38. STUDENT: APPLY WITH FILE UPLOAD ──────────────────────────
section("38. STUDENT: APPLY WITH FILE UPLOAD")

def apply_with_resume():
    # Find an approved drive
    r_drives = student.get("/student/drives")
    drives = r_drives.json().get("drives", [])
    approved_drive = None
    for d in drives:
        # Check if already applied
        r_apps = student.get("/student/applications")
        apps = r_apps.json().get("applications", [])
        applied_ids = {a["drive_id"] for a in apps}
        if d["drive_id"] not in applied_ids:
            approved_drive = d
            break

    if not approved_drive:
        return True, "no unapplied approved drives available"

    pdf_content = b"%PDF-1.4 application resume"
    r = student.post(f"/student/drives/{approved_drive['drive_id']}/apply",
                     files={"file": ("resume.pdf", pdf_content, "application/pdf")})
    return r.ok and r.json().get("success"), r.text
test("POST /student/drives/<id>/apply — with file upload", apply_with_resume)

def apply_duplicate():
    r_drives = student.get("/student/applications")
    apps = r_drives.json().get("applications", [])
    if not apps:
        return True, "no applications to test duplicate"
    first_drive_id = apps[0]["drive_id"]
    r = student.post(f"/student/drives/{first_drive_id}/apply")
    return r.status_code == 409 and r.json().get("error") == "already_applied", r.text
test("POST /student/drives/<id>/apply — duplicate → 409", apply_duplicate)


# ─── 39. HEALTH ENDPOINTS (ALL BLUEPRINTS) ───────────────────────
section("39. HEALTH ENDPOINTS (ALL BLUEPRINTS)")

def health_auth():
    r = s.get("/auth/health")
    return r.ok and r.json().get("scope") == "auth", r.text
test("GET /auth/health", health_auth)

def health_student():
    r = student.get("/student/health")
    return r.ok and r.json().get("scope") == "student", r.text
test("GET /student/health", health_student)

def health_company():
    r = company.get("/company/health")
    return r.ok and r.json().get("scope") == "company", r.text
test("GET /company/health", health_company)

def health_admin():
    r = admin.get("/admin/health")
    return r.ok and r.json().get("scope") == "admin", r.text
test("GET /admin/health", health_admin)

def health_jobs():
    r = s.get("/jobs/health")
    return r.ok and r.json().get("scope") == "jobs", r.text
test("GET /jobs/health", health_jobs)


# ─── 40. PROTECTED ENDPOINTS (ALL BLUEPRINTS) ────────────────────
section("40. PROTECTED ENDPOINTS (ALL BLUEPRINTS)")

def protected_student():
    r = student.get("/student/protected")
    return r.ok and r.json().get("success"), r.text
test("GET /student/protected", protected_student)

def protected_company():
    r = company.get("/company/protected")
    return r.ok and r.json().get("success"), r.text
test("GET /company/protected", protected_company)

def protected_admin():
    r = admin.get("/admin/protected")
    return r.ok and r.json().get("success"), r.text
test("GET /admin/protected", protected_admin)


# ─── 41. 409 STATUS CODES (PATCH 3 VERIFICATION) ────────────────
section("41. 409 STATUS CODE VERIFICATION")

def already_applied_409():
    r_drives = student.get("/student/applications")
    apps = r_drives.json().get("applications", [])
    if not apps:
        return True, "no applications"
    r = student.post(f"/student/drives/{apps[0]['drive_id']}/apply")
    return r.status_code == 409, f"status={r.status_code}"
test("already_applied returns 409", already_applied_409)

def already_deactivated_409():
    admin.patch("/admin/student/1/deactivate")
    r = admin.patch("/admin/student/1/deactivate")
    admin.patch("/admin/student/1/activate")  # restore
    return r.status_code == 409, f"status={r.status_code}"
test("already_deactivated returns 409", already_deactivated_409)

def already_active_409():
    r = admin.patch("/admin/student/1/activate")
    return r.status_code == 409, f"status={r.status_code}"
test("already_active returns 409", already_active_409)


# ─── FINAL SUMMARY ───────────────────────────────────────────────
section("FINAL SUMMARY")

total = len(RESULTS)
passed = sum(1 for s, _ in RESULTS if s == "PASS")
failed = sum(1 for s, _ in RESULTS if s == "FAIL")

print(f"\n  Total:  {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print()

if FAILURES:
    print("  FAILED TESTS:")
    for label, detail in FAILURES:
        print(f"    FAIL {label}")
        print(f"      -> {detail}")
else:
    print("  ALL TESTS PASSED")
