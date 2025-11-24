import os
from flask import Flask, render_template, request, abort, jsonify, Response
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from src.database import database
from src.database import storageAws

load_dotenv()
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
BUCKET_NAME = os.getenv('BUCKET_NAME')


@app.route('/auth')
def auth():
    username = request.args.get('username', '').strip()
    if not username:
        abort(400, description="Username parameter is required")
    database.get_or_create_user(username)
    return render_template('authorization/index.html', username=username)


@app.route('/', methods=['GET'])
def login():
    return render_template('login/index.html')


@app.route('/image/<path:s3_key>')
def serve_image(s3_key):
    """Proxy S3 images through Flask to hide credentials"""
    s3 = storageAws.get_client()
    try:
        response = s3.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        image_data = response['Body'].read()
        content_type = response.get('ContentType', 'image/jpeg')
        return Response(image_data, mimetype=content_type)
    except ClientError as e:
        print(f"Error fetching image: {e}")
        abort(404)


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
    success = storageAws.upload_image_direct(BUCKET_NAME, file.stream, s3_key)
    if success:
        database.add_image(username, s3_key)
        proxy_url = f"/image/{s3_key}"
        return jsonify({'message': 'Upload successful', 'url': proxy_url}), 200
    else:
        return jsonify({'error': 'Failed to upload to S3'}), 500


@app.route('/api/images', methods=['GET'])
def get_images():
    username = request.args.get('username')
    category = request.args.get('category')
    if not username:
        return jsonify([]), 200
    s3_keys = database.get_images_by_username(username)
    if category:
        s3_keys = [key for key in s3_keys if f"/{category}/" in key]
    proxy_urls = [f"/image/{key}" for key in s3_keys]
    return jsonify(proxy_urls)


@app.route('/api/images/delete', methods=['DELETE'])
def delete_image():
    username = request.json.get('username')
    category = request.json.get('category')
    image_name = request.json.get('image_name')
    if not username or not category or not image_name:
        return jsonify({'error': 'Username, category, and image_name required'}), 400
    s3_key = f"{username}/{category}/{image_name}"
    s3_deleted = storageAws.delete_image(BUCKET_NAME, s3_key)
    db_deleted = database.delete_image_by_username(username, s3_key)
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
    if os.path.exists(database.DB_NAME):
        os.remove(database.DB_NAME)
        print(f"Removed old database file: {database.DB_NAME}")

    database.init_db()
    storageAws.delete_bucket(BUCKET_NAME)
    print(f"Deleted bucket {BUCKET_NAME}")

    if storageAws.create_bucket(BUCKET_NAME):
        print(f"Bucket {BUCKET_NAME} ready (private, proxied through Flask)")

    app.run(port=8000, debug=True)