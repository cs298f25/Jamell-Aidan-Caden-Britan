from flask import Flask, render_template
app = Flask(__name__)

# Placeholder image URLs to use across pages
IMAGES = [
    "https://picsum.photos/id/1015/600/400",
    "https://picsum.photos/id/1016/600/400",
    "https://picsum.photos/id/1024/600/400",
    "https://picsum.photos/id/1025/600/400",
    "https://picsum.photos/id/1035/600/400",
    "https://picsum.photos/id/1041/600/400",
    "https://picsum.photos/id/1050/600/400",
    "https://picsum.photos/id/1069/600/400",
    "https://picsum.photos/id/1074/600/400",
    "https://picsum.photos/id/1084/600/400",
]

@app.route('/auth')
def auth():
    return render_template('authorization/index.html')

@app.route('/login')
def login():
    return render_template('login/index.html')

@app.route('/images')
def image_links():
    return render_template('images/links.html', images=IMAGES)

@app.route('/gallery')
def image_grid():
    return render_template('images/grid.html', images=IMAGES)


if __name__ == '__main__':
    app.run(port=8000, debug=True)
