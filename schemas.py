from marshmallow import Schema, fields, validate, validates, ValidationError


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    email = fields.Email(required=True, validate=validate.Length(min=1, max=100))
    level = fields.Str(required=True, validate=validate.OneOf(['beginner', 'intermediate', 'advanced']))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))


class TextSchema(Schema):
    id = fields.Int(dump_only=True)
    content = fields.Str(required=True, validate=validate.Length(min=1, max=500))
    user_id = fields.Int(required=True)


class PageBlocksSchema(Schema):
    id = fields.Int(dump_only=True)
    block_type = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    block_id = fields.Int(required=True)
    position = fields.Int(required=True)
    page_id = fields.Int(required=True)


class PageSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    user_id = fields.Int(required=True)


class BeatSchema(Schema):
    id = fields.Int(dump_only=True)
    beat_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    genre = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    bpm = fields.Int(required=True)
    beat_schema = fields.Dict(required=True)
    user_id = fields.Int(required=True)

    @validates('beat_schema')
    def validate_beat_schema(self, value):
        expected_instruments = ['kick', 'snare', 'high-hat', 'tom1', 'tom2']

        if not all(instrument in value for instrument in expected_instruments):
            raise ValidationError(f'beat schema must contain following instruments: {expected_instruments}')
        for instrument, beats in value.items():
            if not isinstance(beats, list):
                raise ValidationError(f'{instrument} must be a list of lists')
            for beat in beats:
                if not isinstance(beat, list):
                    raise ValidationError(f'{instrument} must be a list of lists.')
                for step in beat:
                    if not isinstance(step, int):
                        raise ValidationError(f'{instrument} must be a list of lists of integers.')



