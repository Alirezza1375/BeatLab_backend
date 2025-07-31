from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# create a User class that has id(primary_key), name, family_name and email(unique) as tables
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    level = db.Column(db.String(50), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "level": self.level
        }

    def __repr__(self):
        return f'<User {self.username}>'


# new table at db -> Text
class Text(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {"id": self.id,
                "content": self.content,
                "user_id": self.user_id
                }

    def __repr__(self):
        return f'<Text {self.id}>'


# new table at db -> Page_blocks
class PageBlock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    block_type = db.Column(db.String, nullable=False)
    block_id = db.Column(db.Integer, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    page = db.relationship('Page', back_populates='blocks')


# new table -> Pages
class Page(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    blocks = db.relationship('PageBlock', back_populates='page', cascade='all, delete-orphan')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "user_id": self.user_id
        }


class Beat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    beat_name = db.Column(db.String(50), nullable=False)
    # make it an Enum ()
    genre = db.Column(db.String(50), nullable=False)
    bpm = db.Column(db.Integer, nullable=False)
    beat_schema = db.Column(db.JSON, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {"id": self.id,
                "beat_name": self.beat_name,
                "genre": self.genre,
                "bpm": self.bpm,
                "beat_schema": self.beat_schema,
                "user_id": self.user_id
                }

    def __repr__(self):
        return f'<Beat {self.beat_name}>'




