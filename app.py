from flask import Flask, jsonify, request
from models import db, User, Beat, Text, Page, PageBlock
from schemas import UserSchema, BeatSchema, TextSchema, PageSchema, PageBlocksSchema
from flask_cors import CORS
from marshmallow import ValidationError
from functools import wraps
import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, get_jwt, current_user
from datetime import timedelta
from sqlalchemy import or_



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'd1d327b3d97cd29371ae2d15ff396b20c19205903ba705a383120716e720ab38')
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}}, supports_credentials=True)
jwt = JWTManager(app)


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db?check_same_thread=False'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drum_website.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


user_schema = UserSchema()
beat_schema = BeatSchema()
text_schema = TextSchema()
page_schema = PageSchema()
page_block_schema = PageBlocksSchema()


with app.app_context():
    db.create_all()


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        claims = get_jwt()
        if claims['role'] != 'admin':
            return jsonify(msg='You are not allowed to see this, you are not an admin!'), 403
        return fn(*args, **kwargs)
    return wrapper


@app.route('/', methods=['GET'])
def home():
    return 'It works!'


# create register route that registers a user
@app.route('/register', methods=['POST'])
def register():
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409

    new_user = User(
        username=data['username'],
        email=data['email'],
        level=data['level']
    )
    new_user.set_password(data['password'])

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User added successfully'})


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get('identifier')  # could be email or username
    password = data.get('password')

    if not identifier or not password:
        return jsonify({"message": "Username/email and password required"}), 400

    user = User.query.filter(
        or_(User.email == identifier, User.username == identifier)
    ).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": "user"},
                                           expires_delta=timedelta(hours=1))

        return jsonify({
            "token": access_token,
            "user": user.to_dict()
        }), 200

    return jsonify({"message": "Invalid username/email or password"}), 401


@app.route('/users', methods=['GET'])
def users():
    users = User.query.all()
    return jsonify([user_schema.dump(user) for user in users])


@app.route('/beats', methods=['POST'])
@jwt_required()
def add_beat():
    try:
        data = beat_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    new_beat = Beat(
        beat_name=data['beat_name'],
        genre=data['genre'],
        bpm=data['bpm'],
        beat_schema=data['beat_schema'],
        user_id=data['user_id']
    )

    db.session.add(new_beat)
    db.session.commit()
    return jsonify({'message': 'beat added successfully'}), 200


@app.route('/beats', methods=['GET'])
@jwt_required()
def get_beats():
    user_id = int(get_jwt_identity())
    beats = Beat.query.filter_by(user_id=user_id).all()
    return jsonify([beat_schema.dump(beat) for beat in beats])


@app.route('/beats/<int:id>', methods=['GET'])
@jwt_required()
def get_beat_by_id(id):
    beat = Beat.query.get(id)
    if not beat:
        return jsonify({'message': 'Beat not found'}), 404
    return beat_schema.dump(beat), 200


@app.route('/beats/<int:id>', methods=['PUT'])
def update_beat(id):
    beat = Beat.query.get_or_404(id)
    data = request.get_json()
    beat.beat_name = data.get("beat_name", beat.beat_name)
    beat.genre = data.get("genre", beat.genre)
    beat.beat_schema = data.get("beat_schema", beat.beat_schema)
    beat.bpm = data.get("bpm", beat.bpm)
    db.session.commit()
    return jsonify({"message": "Beat updated successfully!"})


@app.route('/texts', methods=['GET'])
@jwt_required()
def get_texts():
    user_id = int(get_jwt_identity())
    texts = Text.query.filter_by(user_id=user_id).all()
    return jsonify([text.to_dict() for text in texts])


@app.route('/texts', methods=['POST'])
@jwt_required()
def add_text():
    try:
        data = text_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    new_text = Text(
        content=data["content"],
        user_id=data['user_id']
    )

    db.session.add(new_text)
    db.session.commit()
    return jsonify({'message': 'text added successfully'}), 200


@app.route('/texts/<int:id>', methods=['GET'])
@jwt_required()
def get_text_by_id(id):
    text = Text.query.get(id)
    if not text:
        return jsonify({'message': 'Text not found'}), 404
    return text_schema.dump(text), 200


@app.route('/pages', methods=['GET'])
@jwt_required()
def get_pages():
    user_id = int(get_jwt_identity())
    pages = Page.query.filter_by(user_id=user_id).all()
    return jsonify([page_schema.dump(page) for page in pages])


@app.route('/pages', methods=['POST'])
@jwt_required()
def add_pages():
    try:
        data = page_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    new_page = Page(
        title=data["title"],
        user_id=data['user_id']
    )

    db.session.add(new_page)
    db.session.commit()
    print(new_page)
    return jsonify({'message': 'page added successfully', "page": new_page.to_dict()}), 200


@app.route('/page_blocks', methods=['GET'])
@jwt_required()
def get_page_blocks():
    page_blocks = PageBlock.query.all()
    return jsonify([page_block_schema.dump(page_block) for page_block in page_blocks])


@app.route('/page_blocks', methods=['POST'])
def add_page_blocks():
    try:
        data = page_block_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    new_page_block = PageBlock(
        block_type=data["block_type"],
        block_id=data["block_id"],
        position=data["position"],
        page_id=data["page_id"]
    )

    db.session.add(new_page_block)
    db.session.commit()
    return jsonify({'message': 'page_block added successfully'}), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found!'}, 404
    db.session.delete(user)
    db.session.commit()
    return {'message': f'User {user_id} deleted!'}


@app.route('/beats/<int:beat_id>', methods=['DELETE'])
def delete_beat(beat_id):
    beat = Beat.query.get(beat_id)
    if not beat:
        return {'error': 'Beat not found!'}, 404
    db.session.delete(beat)
    db.session.commit()
    return {'message': f'Beat {beat_id} deleted!'}


@app.route('/texts/<int:text_id>', methods=['DELETE'])
def delete_text(text_id):
    text = Text.query.get(text_id)
    if not text:
        return {'error': 'Text not found!'}, 404
    db.session.delete(text)
    db.session.commit()
    return {'message': f'Text {text_id} deleted!'}


@app.route('/pages/<int:page_id>', methods=['DELETE'])
def delete_page(page_id):
    page = Page.query.get(page_id)
    if not page:
        return {'error': 'Page not found!'}, 404
    db.session.delete(page)
    db.session.commit()
    return {'message': f'Page {page_id} deleted!'}


@app.route('/page_blocks/<int:block_id>', methods=['DELETE'])
def delete_page_block(block_id):
    block = PageBlock.query.get(block_id)
    if not block:
        return {'error': 'PageBlock not found!'}, 404
    db.session.delete(block)
    db.session.commit()
    return {'message': f'PageBlock {block_id} deleted!'}


@app.route('/pages/<int:id>', methods=['GET'])
def get_page_by_id(id):
    page = Page.query.get(id)
    if not page:
        return {'error': 'Page not found!'}, 404
    response = {
        "title": page.title,
        "id": page.id,
        "blocks": [
            {
                "block_id": block.block_id,
                "block_type": block.block_type,
                "position": block.position
            }
            for block in page.blocks
        ]
    }
    return jsonify(response)







if __name__ == "__main__":
    app.run(debug=True)
