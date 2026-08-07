"""
Backend Verification Script — DO NOT MODIFY ANY CODE.
This script only reads and tests the existing implementation.
"""
import json
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import PlacementDrive, StudentProfile, User, CompanyProfile, Application, db
from utils.validators import validate_branches, check_eligibility, get_eligible_branches

app = create_app()

passed = 0
failed = 0


def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {label}")
    else:
        failed += 1
        print(f"  FAIL  {label}")
        if detail:
            print(f"        {detail}")


# =============================================================
# 1. DATABASE VERIFICATION
# =============================================================
section("1. DATABASE VERIFICATION")

with app.app_context():
    import sqlite3
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    db_path = uri.replace("sqlite:///", "")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(placement_drive)")
    columns = [col[1] for col in cursor.fetchall()]
    check("eligibility_branches column exists", "eligibility_branches" in columns)
    check("eligibility_branch column exists (deprecated)", "eligibility_branch" in columns)

    cursor.execute(
        "SELECT id, job_title, eligibility_branch, eligibility_branches, "
        "eligibility_cgpa, eligibility_year, eligibility_year_mode, status "
        "FROM placement_drive"
    )
    drives = cursor.fetchall()
    print(f"\n  Found {len(drives)} drive(s):")
    for d in drives:
        print(f"\n  Drive {d[0]}: {d[1]}")
        print(f"    eligibility_branch  (deprecated): {d[2]}")
        print(f"    eligibility_branches (new):       {d[3]}")
        print(f"    CGPA: {d[4]}  Year: {d[5]}  Mode: {d[6]}  Status: {d[7]}")
        try:
            parsed = json.loads(d[3])
            print(f"    JSON valid: Yes, {len(parsed)} branch(es)")
        except Exception as e:
            print(f"    JSON valid: NO! Error: {e}")

    cursor.execute("SELECT id FROM placement_drive WHERE eligibility_branches = '[]'")
    empty = cursor.fetchall()
    check("No drives with empty eligibility_branches", len(empty) == 0,
          f"{len(empty)} drives have empty array" if empty else "")

    conn.close()


# =============================================================
# 2. API VERIFICATION
# =============================================================
section("2. API VERIFICATION")

with app.app_context():
    client = app.test_client()

    # --- Login as company ---
    print("\n  Logging in as company (hr@techcorp.com)...")
    resp = client.post("/api/auth/login", json={
        "email": "hr@techcorp.com",
        "password": "Company123"
    }, content_type="application/json")
    login_data = resp.get_json()
    check("Company login succeeds", login_data.get("success") is True,
          f"Response: {login_data}")

    # --- GET /api/company/drives ---
    print("\n  --- GET /api/company/drives ---")
    resp = client.get("/api/company/drives")
    data = resp.get_json()
    check("GET /api/company/drives returns success", data.get("success") is True)
    drives_list = data.get("drives", [])
    check("Returns drives list", len(drives_list) > 0)
    if drives_list:
        d = drives_list[0]
        check("Drive has eligibility_branches (list)", isinstance(d.get("eligibility_branches"), list),
              f"Got: {type(d.get('eligibility_branches'))}")
        check("Drive has eligibility_branch (deprecated)", isinstance(d.get("eligibility_branch"), str),
              f"Got: {type(d.get('eligibility_branch'))}")
        print(f"    Sample: branches={d['eligibility_branches']}, branch={d['eligibility_branch']}")

    # --- GET /api/company/drives/<id> ---
    print("\n  --- GET /api/company/drives/<id> ---")
    if drives_list:
        drive_id = drives_list[0]["drive_id"]
        resp = client.get(f"/api/company/drives/{drive_id}")
        data = resp.get_json()
        check("GET /api/company/drives/<id> returns success", data.get("success") is True)
        drv = data.get("drive", {})
        check("Response has eligibility_branches (list)", isinstance(drv.get("eligibility_branches"), list))
        check("Response has eligibility_branch (deprecated)", isinstance(drv.get("eligibility_branch"), str))
        check("eligibility_branch == first element of eligibility_branches",
              drv.get("eligibility_branch") == (drv.get("eligibility_branches") or [None])[0])
        print(f"    branches={drv.get('eligibility_branches')}, branch={drv.get('eligibility_branch')}")

    # --- POST /api/company/drives (create) ---
    print("\n  --- POST /api/company/drives (create with 2 branches) ---")
    resp = client.post("/api/company/drives", json={
        "job_title": "Test Multi-Branch Drive",
        "job_description": "Testing multi-branch eligibility",
        "eligibility_branches": [
            "Computer Science (CSE)",
            "Information Technology (IT)"
        ],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "eligibility_year_mode": "minimum",
        "application_deadline": "2026-12-31T23:59:59+00:00"
    }, content_type="application/json")
    data = resp.get_json()
    check("POST /api/company/drives returns success", data.get("success") is True,
          f"Response: {data}")
    new_drive_id = data.get("drive_id")
    check("Response includes drive_id", new_drive_id is not None)

    # Verify the created drive in DB
    if new_drive_id:
        drive = db.session.get(PlacementDrive, new_drive_id)
        check("Created drive has eligibility_branches as JSON",
              drive.eligibility_branches.startswith("["),
              f"Got: {drive.eligibility_branches}")
        parsed = json.loads(drive.eligibility_branches)
        check("eligibility_branches contains 2 branches", len(parsed) == 2)
        check("eligibility_branch (deprecated) == first element",
              drive.eligibility_branch == parsed[0],
              f"branch={drive.eligibility_branch}, first={parsed[0]}")
        print(f"    DB: eligibility_branches={drive.eligibility_branches}")
        print(f"    DB: eligibility_branch={drive.eligibility_branch}")

    # --- PUT /api/company/drives/<id> (edit to 3 branches) ---
    print("\n  --- PUT /api/company/drives/<id> (edit to 3 branches) ---")
    if new_drive_id:
        resp = client.put(f"/api/company/drives/{new_drive_id}", json={
            "eligibility_branches": [
                "Computer Science (CSE)",
                "Information Technology (IT)",
                "Electronics & Communication Engineering (ECE)"
            ],
        }, content_type="application/json")
        data = resp.get_json()
        check("PUT /api/company/drives/<id> returns success", data.get("success") is True,
              f"Response: {data}")
        drive = db.session.get(PlacementDrive, new_drive_id)
        parsed = json.loads(drive.eligibility_branches)
        check("Updated eligibility_branches has 3 branches", len(parsed) == 3)
        check("eligibility_branch updated to first element",
              drive.eligibility_branch == parsed[0])
        print(f"    DB after edit: branches={drive.eligibility_branches}")

        # Cleanup - delete the test drive
        client.delete(f"/api/company/drives/{new_drive_id}")

    # --- Login as student ---
    print("\n  Logging in as student (anon64057@gmail.com)...")
    resp = client.post("/api/auth/login", json={
        "email": "anon64057@gmail.com",
        "password": "Student123"
    }, content_type="application/json")
    login_data = resp.get_json()
    check("Student login succeeds", login_data.get("success") is True,
          f"Response: {login_data}")

    # --- GET /api/student/drives ---
    print("\n  --- GET /api/student/drives ---")
    resp = client.get("/api/student/drives")
    data = resp.get_json()
    check("GET /api/student/drives returns success", data.get("success") is True)
    s_drives = data.get("drives", [])
    check("Returns drives list", len(s_drives) > 0)
    if s_drives:
        d = s_drives[0]
        check("Drive has eligibility_branches (list)", isinstance(d.get("eligibility_branches"), list))
        check("Drive has eligibility_branch (deprecated)", isinstance(d.get("eligibility_branch"), str))
        print(f"    Sample: branches={d['eligibility_branches']}, branch={d['eligibility_branch']}")

    # --- GET /api/student/drives/<id> ---
    print("\n  --- GET /api/student/drives/<id> ---")
    if s_drives:
        sid = s_drives[0]["drive_id"]
        resp = client.get(f"/api/student/drives/{sid}")
        data = resp.get_json()
        check("GET /api/student/drives/<id> returns success", data.get("success") is True)
        drv = data.get("drive", {})
        check("Response has eligibility_branches (list)", isinstance(drv.get("eligibility_branches"), list))
        check("Response has eligibility_branch (deprecated)", isinstance(drv.get("eligibility_branch"), str))

    # --- Login as admin ---
    print("\n  Logging in as admin...")
    resp = client.post("/api/auth/login", json={
        "email": "admin@placement.local",
        "password": "admin123"
    }, content_type="application/json")
    check("Admin login succeeds", resp.get_json().get("success") is True)

    # --- GET /api/admin/drives ---
    print("\n  --- GET /api/admin/drives ---")
    resp = client.get("/api/admin/drives")
    data = resp.get_json()
    check("GET /api/admin/drives returns success", data.get("success") is True)
    a_drives = data.get("drives", [])
    check("Returns drives list", len(a_drives) > 0)
    if a_drives:
        d = a_drives[0]
        check("Drive has eligibility_branches (list)", isinstance(d.get("eligibility_branches"), list))
        check("Drive has eligibility_branch (deprecated)", isinstance(d.get("eligibility_branch"), str))
        print(f"    Sample: branches={d['eligibility_branches']}, branch={d['eligibility_branch']}")

    # --- GET /api/admin/drive/<id> ---
    print("\n  --- GET /api/admin/drive/<id> ---")
    if a_drives:
        aid = a_drives[0]["drive_id"]
        resp = client.get(f"/api/admin/drive/{aid}")
        data = resp.get_json()
        check("GET /api/admin/drive/<id> returns success", data.get("success") is True)
        drv = data.get("drive", {})
        check("Response has eligibility_branches (list)", isinstance(drv.get("eligibility_branches"), list))
        check("Response has eligibility_branch (deprecated)", isinstance(drv.get("eligibility_branch"), str))

    # --- All admin list endpoints ---
    for endpoint in ["/api/admin/drives/pending", "/api/admin/drives/approved",
                     "/api/admin/drives/rejected", "/api/admin/drives/closed"]:
        resp = client.get(endpoint)
        data = resp.get_json()
        drives_list = data.get("drives", [])
        has_both = all(
            isinstance(d.get("eligibility_branches"), list) and isinstance(d.get("eligibility_branch"), str)
            for d in drives_list
        ) if drives_list else True
        check(f"GET {endpoint} has both fields", has_both)


# =============================================================
# 3. ELIGIBILITY VERIFICATION
# =============================================================
section("3. ELIGIBILITY VERIFICATION")

with app.app_context():
    class MockStudent:
        def __init__(self, branch, cgpa, year):
            self.branch = branch
            self.cgpa = cgpa
            self.year = year

    class MockDrive:
        def __init__(self, branches, cgpa, year, mode):
            self.eligibility_branches = json.dumps(branches)
            self.eligibility_cgpa = cgpa
            self.eligibility_year = year
            self.eligibility_year_mode = mode

    # Scenario 1: Branch match
    print("\n  Scenario 1: IT student, eligible branches=[CSE, IT]")
    student = MockStudent("Information Technology (IT)", 8.5, 3)
    drive = MockDrive(["Computer Science (CSE)", "Information Technology (IT)"], 8.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Student is eligible", len(violations) == 0, f"violations={violations}")

    # Scenario 2: Branch mismatch
    print("\n  Scenario 2: ECE student, eligible branches=[CSE, IT]")
    student = MockStudent("Electronics & Communication Engineering (ECE)", 8.5, 3)
    drive = MockDrive(["Computer Science (CSE)", "Information Technology (IT)"], 8.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Student is NOT eligible", "branch" in violations, f"violations={violations}")

    # Scenario 3: CGPA check
    print("\n  Scenario 3: CGPA check")
    student = MockStudent("Computer Science (CSE)", 6.5, 3)
    drive = MockDrive(["Computer Science (CSE)"], 8.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Low CGPA rejected", "cgpa" in violations, f"violations={violations}")

    student = MockStudent("Computer Science (CSE)", 8.5, 3)
    drive = MockDrive(["Computer Science (CSE)"], 8.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Sufficient CGPA passes", "cgpa" not in violations, f"violations={violations}")

    # Scenario 4: Year mode = exact
    print("\n  Scenario 4a: Year mode = exact")
    student = MockStudent("Computer Science (CSE)", 8.5, 2)
    drive = MockDrive(["Computer Science (CSE)"], 7.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Exact: year 2 != year 3 => ineligible", "year" in violations, f"violations={violations}")

    student = MockStudent("Computer Science (CSE)", 8.5, 3)
    drive = MockDrive(["Computer Science (CSE)"], 7.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Exact: year 3 == year 3 => eligible", "year" not in violations, f"violations={violations}")

    # Scenario 4: Year mode = minimum
    print("\n  Scenario 4b: Year mode = minimum")
    student = MockStudent("Computer Science (CSE)", 8.5, 4)
    drive = MockDrive(["Computer Science (CSE)"], 7.0, 3, "minimum")
    violations = check_eligibility(student, drive)
    check("Minimum: year 4 >= year 3 => eligible", "year" not in violations, f"violations={violations}")

    student = MockStudent("Computer Science (CSE)", 8.5, 2)
    drive = MockDrive(["Computer Science (CSE)"], 7.0, 3, "minimum")
    violations = check_eligibility(student, drive)
    check("Minimum: year 2 < year 3 => ineligible", "year" in violations, f"violations={violations}")

    # Scenario 5: All checks pass with full branch names
    print("\n  Scenario 5: All checks pass (full branch names)")
    student = MockStudent("Information Technology (IT)", 8.5, 3)
    drive = MockDrive(
        ["Computer Science (CSE)", "Information Technology (IT)", "Electronics & Communication Engineering (ECE)"],
        8.0, 3, "exact"
    )
    violations = check_eligibility(student, drive)
    check("All criteria met", len(violations) == 0, f"violations={violations}")

    # Scenario 6: Multiple failures
    print("\n  Scenario 6: Multiple failures")
    student = MockStudent("Mechanical Engineering (ME)", 6.0, 1)
    drive = MockDrive(["Computer Science (CSE)", "Information Technology (IT)"], 8.0, 3, "exact")
    violations = check_eligibility(student, drive)
    check("Branch + CGPA + Year all fail", len(violations) == 3, f"violations={violations}")
    check("branch in violations", "branch" in violations)
    check("cgpa in violations", "cgpa" in violations)
    check("year in violations", "year" in violations)


# =============================================================
# 4. SEARCH VERIFICATION
# =============================================================
section("4. SEARCH VERIFICATION")

with app.app_context():
    client = app.test_client()

    # Login as student
    resp = client.post("/api/auth/login", json={
        "email": "anon64057@gmail.com",
        "password": "Student123"
    }, content_type="application/json")

    # Search "CSE"
    print("\n  Search for 'CSE':")
    resp = client.get("/api/student/drives?q=CSE")
    data = resp.get_json()
    results = data.get("drives", [])
    print(f"    Found {len(results)} drive(s)")
    for d in results:
        branches = d.get("eligibility_branches", [])
        print(f"      Drive {d['drive_id']}: {d['job_title']} -> branches={branches}")
    cse_match = any("CSE" in str(d.get("eligibility_branches", [])) for d in results)
    check("Search 'CSE' returns drives with CSE branch", len(results) > 0 and cse_match)

    # Search "Information Technology"
    print("\n  Search for 'Information Technology':")
    resp = client.get("/api/student/drives?q=Information Technology")
    data = resp.get_json()
    results = data.get("drives", [])
    print(f"    Found {len(results)} drive(s)")
    for d in results:
        branches = d.get("eligibility_branches", [])
        print(f"      Drive {d['drive_id']}: {d['job_title']} -> branches={branches}")
    it_match = any("Information Technology" in str(d.get("eligibility_branches", [])) for d in results)
    check("Search 'Information Technology' returns IT drives", len(results) > 0 and it_match)

    # Search "ECE"
    print("\n  Search for 'ECE':")
    resp = client.get("/api/student/drives?q=ECE")
    data = resp.get_json()
    results = data.get("drives", [])
    print(f"    Found {len(results)} drive(s)")
    for d in results:
        branches = d.get("eligibility_branches", [])
        print(f"      Drive {d['drive_id']}: {d['job_title']} -> branches={branches}")
    check("Search 'ECE' returns without error", isinstance(results, list))


# =============================================================
# 5. VALIDATION
# =============================================================
section("5. VALIDATION")

with app.app_context():
    print("\n  Testing validate_branches() function:")

    check("Empty list rejected", validate_branches([]) is False)
    check("String rejected", validate_branches("CSE") is False)
    check("None rejected", validate_branches(None) is False)
    check("Integer rejected", validate_branches(123) is False)
    check("Invalid branch rejected", validate_branches(["Invalid Branch XYZ"]) is False)
    check("Duplicates rejected", validate_branches(["Computer Science (CSE)", "Computer Science (CSE)"]) is False)
    check("Single valid branch accepted", validate_branches(["Computer Science (CSE)"]) is True)
    check("Multiple valid branches accepted",
          validate_branches(["Computer Science (CSE)", "Information Technology (IT)"]) is True)

    # Test via API
    print("\n  Testing via API:")
    client = app.test_client()
    client.post("/api/auth/login", json={
        "email": "hr@techcorp.com",
        "password": "Company123"
    }, content_type="application/json")

    # Empty branch list
    resp = client.post("/api/company/drives", json={
        "job_title": "Test",
        "job_description": "Test",
        "eligibility_branches": [],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59+00:00"
    }, content_type="application/json")
    data = resp.get_json()
    check("API rejects empty branch list", data.get("error") == "invalid_branches",
          f"Got: {data}")

    # Duplicate branches
    resp = client.post("/api/company/drives", json={
        "job_title": "Test",
        "job_description": "Test",
        "eligibility_branches": [
            "Computer Science (CSE)",
            "Computer Science (CSE)"
        ],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59+00:00"
    }, content_type="application/json")
    data = resp.get_json()
    check("API rejects duplicate branches", data.get("error") == "invalid_branches",
          f"Got: {data}")

    # Invalid branch
    resp = client.post("/api/company/drives", json={
        "job_title": "Test",
        "job_description": "Test",
        "eligibility_branches": ["Fake Branch"],
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59+00:00"
    }, content_type="application/json")
    data = resp.get_json()
    check("API rejects invalid branch", data.get("error") == "invalid_branches",
          f"Got: {data}")

    # Non-array input
    resp = client.post("/api/company/drives", json={
        "job_title": "Test",
        "job_description": "Test",
        "eligibility_branches": "CSE",
        "eligibility_cgpa": 7.0,
        "eligibility_year": 3,
        "application_deadline": "2026-12-31T23:59:59+00:00"
    }, content_type="application/json")
    data = resp.get_json()
    check("API rejects non-array input", data.get("error") == "invalid_branches",
          f"Got: {data}")


# =============================================================
# 6. BACKWARD COMPATIBILITY
# =============================================================
section("6. BACKWARD COMPATIBILITY")

with app.app_context():
    client = app.test_client()

    # Admin — most comprehensive response
    client.post("/api/auth/login", json={
        "email": "admin@placement.local",
        "password": "admin123"
    }, content_type="application/json")

    resp = client.get("/api/admin/drives")
    data = resp.get_json()
    drives = data.get("drives", [])
    if drives:
        d = drives[0]
        check("Admin: eligibility_branch is string", isinstance(d.get("eligibility_branch"), str))
        check("Admin: eligibility_branches is list", isinstance(d.get("eligibility_branches"), list))
        check("Admin: eligibility_branch == eligibility_branches[0]",
              d.get("eligibility_branch") == (d.get("eligibility_branches") or [None])[0],
              f"branch={d.get('eligibility_branch')}, branches[0]={(d.get('eligibility_branches') or [None])[0]}")

    # Company
    client.post("/api/auth/login", json={
        "email": "hr@techcorp.com",
        "password": "Company123"
    }, content_type="application/json")

    resp = client.get("/api/company/drives")
    data = resp.get_json()
    drives = data.get("drives", [])
    if drives:
        d = drives[0]
        check("Company: eligibility_branch is string", isinstance(d.get("eligibility_branch"), str))
        check("Company: eligibility_branches is list", isinstance(d.get("eligibility_branches"), list))
        check("Company: eligibility_branch == eligibility_branches[0]",
              d.get("eligibility_branch") == (d.get("eligibility_branches") or [None])[0])

    # Student
    client.post("/api/auth/login", json={
        "email": "anon64057@gmail.com",
        "password": "Student123"
    }, content_type="application/json")

    resp = client.get("/api/student/drives")
    data = resp.get_json()
    drives = data.get("drives", [])
    if drives:
        d = drives[0]
        check("Student: eligibility_branch is string", isinstance(d.get("eligibility_branch"), str))
        check("Student: eligibility_branches is list", isinstance(d.get("eligibility_branches"), list))
        check("Student: eligibility_branch == eligibility_branches[0]",
              d.get("eligibility_branch") == (d.get("eligibility_branches") or [None])[0])

    print("\n  Backward compatibility: Old frontend using eligibility_branch will still work.")
    print("  New frontend using eligibility_branches will also work.")


# =============================================================
# 7. FINAL VERDICT
# =============================================================
section("7. FINAL VERDICT")

total = passed + failed
print(f"\n  Total checks: {total}")
print(f"  Passed:       {passed}")
print(f"  Failed:       {failed}")

if failed == 0:
    print("\n  RESULT: ALL CHECKS PASSED")
    print("  Backend is PRODUCTION-READY for frontend integration.")
else:
    print(f"\n  RESULT: {failed} CHECK(S) FAILED")
    print("  Review failures above before proceeding.")
