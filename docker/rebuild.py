
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

SERVICES = {
    "1": {
        "name": "Frontend",
        "services": ["frontend"],
    },
    "2": {
        "name": "Backend + Celery Worker + Celery Beat",
        "services": ["backend", "celery-worker", "celery-beat"],
    },
    "3": {
        "name": "PostgreSQL",
        "services": ["db"],
    },
    "4": {
        "name": "Redis",
        "services": ["redis"],
    },
    "5": {
        "name": "Celery Worker",
        "services": ["celery-worker"],
    },
    "6": {
        "name": "Celery Beat",
        "services": ["celery-beat"],
    },
}


def run_command(command):
    try:
        return subprocess.run(
            command,
            cwd=PROJECT_ROOT,
            check=False
        ).returncode == 0

    except FileNotFoundError:
        print("[ERROR] Docker CLI was not found.")
        return False


def check_docker():
    print("\n[INFO] Checking Docker Desktop / Engine...")

    try:
        result = subprocess.run(
            ["docker", "info"],
            cwd=PROJECT_ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False
        )

    except FileNotFoundError:
        print("[ERROR] Docker CLI is not installed or not in PATH.")
        return False

    if result.returncode != 0:
        print("[ERROR] Docker Engine is not running.")
        print("Please start Docker Desktop and try again.")
        return False

    print("[OK] Docker Engine is running.")
    return True


def main():
    print("\n========== MERIDIAN DOCKER REBUILDER ==========")

    # Check Docker before doing anything.
    if not check_docker():
        sys.exit(1)

    # Display service menu.
    print("\nSelect the service to rebuild:\n")

    for key, item in SERVICES.items():
        print(f"{key}. {item['name']}")

    print("0. Exit")

    choice = input("\nEnter your choice: ").strip()

    if choice == "0":
        print("Operation cancelled.")
        return

    if choice not in SERVICES:
        print("[ERROR] Invalid selection.")
        return

    selected = SERVICES[choice]
    services = selected["services"]

    print(f"\nSelected: {selected['name']}")
    print(f"Services affected: {', '.join(services)}")

    confirm = input("\nProceed with rebuild? (y/n): ").strip().lower()

    if confirm != "y":
        print("[INFO] Rebuild cancelled.")
        return

    # Build only the selected service image(s).
    print("\n[INFO] Building selected Docker image(s)...")

    build_success = run_command(
        ["docker", "compose", "build", *services]
    )

    if not build_success:
        print("\n[ERROR] Image build failed.")
        print("[INFO] Existing containers have not been recreated.")
        sys.exit(1)

    # Recreate only selected services.
    # --no-deps prevents unrelated services from being restarted.
    print("\n[INFO] Recreating selected container(s)...")

    recreate_success = run_command(
        [
            "docker",
            "compose",
            "up",
            "-d",
            "--no-deps",
            *services
        ]
    )

    if not recreate_success:
        print("\n[ERROR] Container recreation failed.")
        sys.exit(1)

    print("\n[SUCCESS] Rebuild completed.")
    print("[INFO] Final container status:\n")

    run_command(["docker", "compose", "ps"])


if __name__ == "__main__":
    main()
# docker compose up -d
# docker compose stop
# docker compose ps
