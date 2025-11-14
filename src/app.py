from flask import Flask, render_template, request, abort, jsonify
import os
from database import DatabaseStorage

# Create database directory if it doesn't exist

storage = DatabaseStorage("database/app.db")
def create_app(manager):
    app = Flask(__name__)

    # ---------------------
    # LOGIN PAGE
    # ---------------------
    @app.route('/', methods=['GET'])
    def login():
        return render_template('login/index.html')

    # ---------------------
    # AUTH PAGE (creates user)
    # ---------------------
    @app.route('/auth')
    def auth():
        username = request.args.get("username", "").strip()
        if not username:
            abort(400, "Username is required")

        manager.login_user(username)

        return render_template('authorization/index.html', username=username)

    # ---------------------
    # GALLERY PAGE
    # ---------------------
    @app.route('/gallery')
    def gallery():
        username = request.args.get("username")
        if not username:
            abort(400, "Missing username")

        images = manager.list_images(username)
        return render_template("images/grid.html", username=username, images=images)

    # ---------------------
    # IMAGE API ENDPOINT
    # ---------------------
    @app.route('/links')
    def links():
        username = request.args.get("username")
        if not username:
            abort(400, "Missing username")

        images = manager.list_images(username)
        return jsonify({"images": images})

    # ---------------------
    # UPLOAD IMAGE
    # ---------------------
    @app.route('/upload', methods=['POST'])
    def upload():
        username = request.form.get("username")
        image_url = request.form.get("image_url")

        if not username or not image_url:
            abort(400, "Missing username or image_url")

        image_id = manager.add_image(username, image_url)
        return jsonify({"image_id": image_id})

    return app


# ------------------------
# START THE APPLICATION
# ------------------------
if __name__ == "__main__":
    from database import DatabaseStorage, UserManager

    storage = DatabaseStorage("database/app.db")
    manager = UserManager(storage)

    app = create_app(manager)
    app.run(port=8000, debug=True)

