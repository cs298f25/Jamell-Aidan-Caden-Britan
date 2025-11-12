from flask import Flask, render_template, request, abort, jsonify

app = Flask(__name__)

@app.route('/auth')
def auth():
    username = request.args.get('username', '').strip()
    if not username:
        abort(400, description="Username parameter is required")
    return render_template('authorization/index.html', username=username)

@app.route('/', methods=['GET'])
def login():
    return render_template('login/index.html')

#grid
@app.route('/gallery', methods=['GET'])
def image_grid():
    return render_template('images/grid.html')

# links
@app.route('/links', methods=['GET'])
def images_api():
    return render_template('images/links.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
