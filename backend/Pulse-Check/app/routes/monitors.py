from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from app.schemas import CreateMonitorSchema
from app.services.monitor_service import MonitorService

monitors_bp = Blueprint("monitors", __name__)

create_schema = CreateMonitorSchema()


@monitors_bp.route("/monitors", methods=["POST"])
def create_monitor():
    body = request.get_json(silent=True)
    if not body:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        data = create_schema.load(body)
    except ValidationError as err:
        return jsonify({"error": "Validation failed.", "details": err.messages}), 400

    try:
        monitor = MonitorService.create_monitor(
            device_id=data["id"],
            timeout=data["timeout"],
            alert_email=data["alert_email"],
        )
    except ValueError as err:
        return jsonify({"error": str(err)}), 409

    return jsonify(monitor.to_dict()), 201