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

@monitors_bp.route("/monitors/<string:monitor_id>/heartbeat", methods=["POST"])
def heartbeat(monitor_id):
    monitor = MonitorService.heartbeat(monitor_id)
    if not monitor:
        return jsonify({"error": f"Monitor '{monitor_id}' not found."}), 404

    return jsonify({
        "id": monitor.id,
        "status": monitor.status,
        "deadline": monitor.deadline.isoformat() + "Z" if monitor.deadline else None,
        "message": "Heartbeat received. Timer reset.",
    }), 200

@monitors_bp.route("/monitors/<string:monitor_id>/pause", methods=["POST"])
def pause_monitor(monitor_id):
    try:
        monitor = MonitorService.pause(monitor_id)
    except ValueError as err:
        return jsonify({"error": str(err)}), 400

    if not monitor:
        return jsonify({"error": f"Monitor '{monitor_id}' not found."}), 404

    return jsonify({
        "id": monitor.id,
        "status": monitor.status,
        "message": "Monitoring paused. Send a heartbeat to resume.",
    }), 200