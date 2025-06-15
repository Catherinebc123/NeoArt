from flask import Flask, render_template, request, send_file
import cv2
import os
import uuid

from flask import Flask, render_template, request, send_file, session
from flask import redirect, url_for

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Secret key required to use sessions
app.secret_key = 'your_secret_key_here'

def cartoonify(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray_blur, 255,
                                  cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(img, 9, 250, 250)
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    output_path = os.path.join('static', 'cartoon.png')
    cv2.imwrite(output_path, cartoon)
    return output_path

def grayscale(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    output_path = os.path.join('static', 'gray.png')
    cv2.imwrite(output_path, gray)
    return output_path

def pencil_sketch(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inv = 255 - gray
    blur = cv2.GaussianBlur(inv, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256)
    output_path = os.path.join('static', 'sketch.png')
    cv2.imwrite(output_path, sketch)
    return output_path


def digital_art(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, (800, 800))  # Optional resize for consistent results
    
    # Apply stylization effect
    digital = cv2.stylization(img, sigma_s=150, sigma_r=0.25)

    output_path = os.path.join('static', 'digital_art.png')
    cv2.imwrite(output_path, digital)
    return output_path






@app.route('/', methods=['GET', 'POST'])
def index():
    result_image = None
    if request.method == 'POST':
        file = request.files['image']
        effect = request.form['effect']
        if file:
            filename = str(uuid.uuid4()) + "_" + file.filename
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if effect == 'cartoon':
                result_image = cartoonify(file_path)
            elif effect == 'gray':
                result_image = grayscale(file_path)
            elif effect == 'sketch':
                result_image = pencil_sketch(file_path)
            elif effect == 'digital':
                result_image = digital_art(file_path)

            # Save processed image path to session
            session['last_processed'] = result_image

    return render_template('index.html', cartoon=result_image)


@app.route('/download')
def download():
    path = session.get('last_processed')
    if path and os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "No image processed yet!", 404

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.mkdir('uploads')
    app.run(debug=True)