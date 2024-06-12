from flask import Flask, url_for, send_from_directory

app = Flask(__name__)

@app.route('/test-url')
def test_url():
    image_url = url_for('static', filename='images/andon.png')
    return f"Image URL: {image_url}"

@app.route('/show-image')
def show_image():
    return send_from_directory('static/images', 'andon.png')

if __name__ == '__main__':
    app.run(debug=True, port=5007)
