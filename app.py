from flask import Flask, request, jsonify, render_template
import numpy as np
import PIL.Image
from PIL import ImageFilter
from keras.preprocessing.image import img_to_array, load_img
from keras.models import load_model
import os

# Initialize the Flask application
app = Flask(__name__)

# Load your trained model
MODEL_PATH = 'top_model.h5'
model = load_model(MODEL_PATH)

def process_image(image_path):
    
    pil_img = PIL.Image.open(image_path).convert('L')
    pil_img = pil_img.filter(ImageFilter.GaussianBlur(radius=3))  # Example preprocessing
    pil_img = pil_img.resize((105, 105))
    org_img = img_to_array(pil_img)
    org_img = np.expand_dims(org_img, axis=0)
    org_img = org_img.astype('float32') / 255
    return org_img

def predict_font(image_path):
    
    processed_image = process_image(image_path)
    prediction = model.predict_classes(processed_image)
    label = rev_conv_label(int(prediction[0]))
    return label

@app.route('/', methods=['GET'])
def index():
    """
    Render the main page.
    """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def upload():
    
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        # Save the file to a temporary folder
        file_path = os.path.join('uploads', file.filename)
        file.save(file_path)

        # Predict the font
        predicted_font = predict_font(file_path)

        # Remove the image after prediction
        os.remove(file_path)

        return jsonify({'predicted_font': predicted_font})

if __name__ == '__main__':
    app.run(debug=True)
