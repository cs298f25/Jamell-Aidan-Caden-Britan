from flask import Flask

app = Flask(__name__)

@app.route('/hello')
def send():
	return 'Hello World'

if __name__ == '__main__':
	app.run(port=8000)

