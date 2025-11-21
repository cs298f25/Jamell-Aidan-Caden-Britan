import os
from flask import Flask, render_template, request, abort, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from database import database
from database import storageAws  # Importing your provided file

# Load environment variables (for BUCKET_NAME if you put it in .env)
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max limit

# 1. DEFINE YOUR BUCKET NAME HERE
# You can change this string to whatever you want your bucket to be named.
BUCKET_NAME = os.getenv('BUCKET_NAME', 'jamell-flask-image-hosting-bucket-1025')

# Ensure local upload temp folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 2. INITIALIZE DATABASE AND S3 BUCKET
# We use the functions from storageAws.py to ensure the bucket exists and is public.
database.init_db()

# Try to create the bucket. If it exists, this might return False, which is fine.
storageAws.create_bucket(BUCKET_NAME) 
# Ensure the bucket policy allows public read access so users can see the images.
storageAws.make_bucket_public(BUCKET_NAME)

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

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    username = request.form.get('username')
    
    if file.filename == '' or not username:
        return jsonify({'error': 'No selected file or username missing'}), 400

    if file:
        filename = secure_filename(file.filename)
        local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(local_path)

        # 3. USE storageAws TO UPLOAD
        # storageAws.upload_image requires: bucket_name, file_path, object_name
        success = storageAws.upload_image(BUCKET_NAME, local_path, filename)
        
        # Clean up local file after upload attempt
        os.remove(local_path)

        if success:
            user_id = database.get_or_create_user(username)
            
            # Construct the public URL based on standard S3 naming
            # Note: This assumes the standard AWS S3 URL format.
            s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
            
            database.add_image(user_id, s3_url)
            return jsonify({'message': 'Upload successful', 'url': s3_url}), 200
        else:
            return jsonify({'error': 'Failed to upload to S3'}), 500

@app.route('/api/images', methods=['GET'])
def get_images():
    username = request.args.get('username')
    if not username:
        return jsonify([]), 200
    
    images = database.get_images_by_username(username)
    return jsonify(images)

@app.route('/gallery', methods=['GET'])
def image_grid():
    return render_template('images/grid.html')

@app.route('/links', methods=['GET'])
def images_api():
    return render_template('images/links.html')

if __name__ == '__main__':
    app.run(port=8000, debug=True)
