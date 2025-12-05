import os
from flask import Flask, render_template, request, abort, jsonify
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from database import database
from database import storageAws

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
BUCKET_NAME = os.getenv('BUCKET_NAME','image-hosting-bucket')

def safe_init():
    """Initialize database and S3 bucket only if they don't exist"""
    if not os.path.exists(database.DB_NAME):
        print(f"Database not found. Initializing at {database.DB_NAME}")
        database.init_db()
    else:
        print(f"Database already exists at {database.DB_NAME}")
    print(f"Ensuring bucket {BUCKET_NAME} exists...")
    if storageAws.create_bucket(BUCKET_NAME):
        storageAws.make_bucket_public(BUCKET_NAME)
        print(f"Bucket {BUCKET_NAME} is ready")
safe_init()

@app.route('/auth')
def auth():
    username = request.args.get('username', '').strip()
    password = request.args.get('password', '').strip()
    if not username:
        abort(400, description="Username parameter is required")
    # If password is provided, authenticate (create or verify)
    if password:
        user = database.get_user(username)
        if user is None:
            # New user: create with hashed password
            password_hash = generate_password_hash(password)
            database.create_user(username, password_hash)
        else:
            # Existing user: verify password
            stored_hash = user.get('password') or ''
            if not check_password_hash(stored_hash, password):
                abort(401, description="Invalid username or password")
    else:
        # No password provided - check if user exists (for returning to auth page)
        user = database.get_user(username)
        if user is None:
            abort(404, description="User not found. Please log in with your password.")

    return render_template('authorization/index.html', username=username)


@app.route('/', methods=['GET'])
def login():
    return render_template('login/index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    username = request.form.get('username')
    category = request.form.get('category', 'uncategorized')
    if file.filename == '' or not username:
        return jsonify({'error': 'No selected file or username missing'}), 400
    filename = secure_filename(file.filename)
    s3_key = f"{username}/{category}/{filename}"
    success = storageAws.upload_image_direct(BUCKET_NAME, file, s3_key)
    if success:
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        database.add_image(username, s3_url)
        return jsonify({'message': 'Upload successful', 'url': s3_url}), 200
    else:
        return jsonify({'error': 'Failed to upload to S3'}), 500


@app.route('/api/images', methods=['GET'])
def get_images():
    username = request.args.get('username')
    category = request.args.get('category')
    if not username:
        return jsonify([]), 200
    images = database.get_images_by_username(username)
    if category:
        images = [img for img in images if f"/{category}/" in img]
    return jsonify(images)


@app.route('/api/images/delete', methods=['DELETE'])
def delete_image():
    username = request.json.get('username')
    category = request.json.get('category')
    image_name = request.json.get('image_name')
    if not username or not category or not image_name:
        return jsonify({'error': 'Username, category, and image_name required'}), 400
    s3_key = f"{username}/{category}/{image_name}"
    image_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
    s3_deleted = storageAws.delete_image(BUCKET_NAME, s3_key)
    db_deleted = database.delete_image_by_username(username, image_url)
    if s3_deleted and db_deleted:
        return jsonify({'message': 'Image deleted successfully'}), 200
    else:
        return jsonify({'error': 'Failed to delete image'}), 500


@app.route('/api/categories', methods=['GET'])
def get_categories():
    username = request.args.get('username')
    if not username:
        return jsonify([]), 200
    categories = database.get_categories_from_user(username)
    return jsonify(categories)


@app.route('/api/categories', methods=['POST'])
def create_category():
    username = request.json.get('username')
    category_name = request.json.get('category_name')
    if not username or not category_name:
        return jsonify({'error': 'Username and category_name required'}), 400
    result = database.create_category_for_user(username, category_name)
    status_code = 200 if result['success'] else 400
    return jsonify(result), status_code


@app.route('/gallery', methods=['GET'])
def image_grid():
    return render_template('images/grid.html')


@app.route('/links', methods=['GET'])
def images_api():
    return render_template('images/links.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True, use_reloader=False)