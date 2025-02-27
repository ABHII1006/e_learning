from marshmallow import Schema, fields

class SubjectSchema(Schema):
    id = fields.Int(required=True)
    topic = fields.Str(required=True)
    category = fields.Str(required=True)
    description = fields.Str(required=True)

