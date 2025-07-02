from flask import Flask, jsonify, request
from models import db, User, Beat, Text, Page, PageBlock
from schemas import UserSchema, BeatSchema, TextSchema, PageSchema, PageBlocksSchema
from flask_cors import CORS
from marshmallow import ValidationError


app = Flask(__name__)
CORS(app)


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///drum_website.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db?check_same_thread=False'
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


# create a test route to see everything works.
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

    new_user = User(
        name=data['name'],
        family_name=data['family_name'],
        email=data['email'],
        level=data['level']
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'user added successfully'})


@app.route('/users', methods=['GET'])
def users():
    users = User.query.all()
    return jsonify([user_schema.dump(user) for user in users])


@app.route('/beats', methods=['POST'])
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
def get_beats():
    beats = Beat.query.all()
    print(beats)
    return jsonify([beat_schema.dump(beat) for beat in beats])


# Add route to get only one beat (Get "/beats/<id>")


@app.route('/beats/<int:id>', methods=['GET'])
def get_beat_by_id(id):
    beat = Beat.query.get(id)
    if not beat:
        return jsonify({'message': 'Beat not found'}), 404
    return beat_schema.dump(beat), 200


@app.route('/texts', methods=['GET'])
def get_texts():
    texts = Text.query.all()
    print(texts)
    return jsonify([text.to_dict() for text in texts])


@app.route('/texts', methods=['POST'])
def add_text():
    try:
        data = text_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    new_text = Text(
        content=data["content"]
    )

    db.session.add(new_text)
    db.session.commit()
    return jsonify({'message': 'text added successfully'}), 200


@app.route('/pages', methods=['GET'])
def get_pages():
    pages = Page.query.all()
    return jsonify([page_schema.dump(page) for page in pages])

@app.route('/pages', methods=['POST'])
def add_pages():
    try:
        data = page_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'error': err.messages}), 400

    new_page = Page(
        title=data["title"]
    )

    db.session.add(new_page)
    db.session.commit()
    return jsonify({'message': 'page added successfully'}), 200


@app.route('/page_blocks', methods=['GET'])
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
                "id": block.id,
                "block_type": block.block_type
            }
            for block in page.blocks
        ]
    }
    return jsonify(response)







if __name__ == "__main__":
    app.run(debug=True)
