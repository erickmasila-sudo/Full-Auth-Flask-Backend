"""
Marshmallow schemas used to validate incoming request bodies.

These are intentionally simple (load-only) schemas: they validate shape
and required fields on the way in. Serialization back to JSON is handled
by each model's `to_dict()` method in models.py.
"""
from marshmallow import Schema, fields, validate


class SignupSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=1))
    password = fields.String(required=True, validate=validate.Length(min=6))


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class NoteCreateSchema(Schema):
    title = fields.String(required=True, validate=validate.Length(min=1))
    content = fields.String(required=True, validate=validate.Length(min=1))


class NoteUpdateSchema(Schema):
    # Partial update (PATCH): fields are optional, but if present must be non-empty.
    title = fields.String(required=False, validate=validate.Length(min=1))
    content = fields.String(required=False, validate=validate.Length(min=1))
