from marshmallow import Schema, fields, validate, validates, ValidationError


class CreateMonitorSchema(Schema):
    id = fields.String(
        required=True,
        validate=validate.Length(min=1, max=128),
    )
    timeout = fields.Integer(required=True, strict=True)
    alert_email = fields.Email(required=True)

    @validates("timeout")
    def validate_timeout(self, value, **kwargs):
        if value < 10:
            raise ValidationError("Must be at least 10 seconds.")
        if value > 86400:
            raise ValidationError("Cannot exceed 86400 seconds (24h).")
