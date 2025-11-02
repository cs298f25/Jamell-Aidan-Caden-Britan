from flask import Flask, render_template

app = Flask(__name__)


@app.route('/auth')
def auth():
    return render_template('authorization/index.html')


if __name__ == '__main__':
    app.run(port=8000, debug=True)
