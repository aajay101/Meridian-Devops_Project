from flask import Blueprint, jsonify

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("/health")
def health():
    return jsonify({"status": "ok", "scope": "jobs"})
