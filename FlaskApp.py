from flask import Flask, render_template, request, jsonify, redirect, url_for
from mtcnn import MTCNN
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time


app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB

selected_face = None

def detect_and_draw_faces(image_path, scale_factor=1.0, padding=11):
    global selected_face
    
    # Load the image
    img = cv2.imread(image_path)
    
    # Convert the image to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Initialize MTCNN detector
    detector = MTCNN()
    
    # Detect faces
    detected_faces = detector.detect_faces(img_rgb)
    faces = []
    
    # Draw rectangles around all detected faces
    for face in detected_faces:
        x, y, width, height = face['box']
        
        # Scale the dimensions (scaled based on individual face size)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        # Adjust the coordinates to keep the rectangle centered
        x = int(x - (new_width - width) / 2)
        y = int(y - (new_height - height) / 2)
        
        # Add padding
        x = max(0, x - padding)
        y = max(0, y - padding)
        new_width = new_width + 2 * padding
        new_height = new_height + 2 * padding
        
        # Store the adjusted face coordinates
        faces.append((x, y, new_width, new_height))
        
        # Draw rectangles that are proportional to face sizes
        cv2.rectangle(img, (x, y), (x + new_width, y + new_height), (255, 0, 0), 2)
    
    return img, faces

@app.route("/")
def home():
    return render_template('workingindex.html')

@app.route("/capture", methods=["POST"])
def capture_image():
    try:
        if 'image' not in request.files:
            return 'No image captured', 400
        file = request.files['image']
        if file.filename == '':
            return 'No image selected', 400
        file.save('static/main_pic.jpg')
        return redirect(url_for('face_detection'))
    except Exception as e:
        print(f"Error capturing image: {e}")
        return 'Error capturing image', 500

@app.route("/upload", methods=["POST"])
def upload_image():
    try:
        if 'image' not in request.files:
            return 'No image uploaded', 400
        file = request.files['image']
        if file.filename == '':
            return 'No selected file', 400
        file.save('static/main_pic.jpg')
        return redirect(url_for('face_detection'))
    except Exception as e:
        print(f"Error uploading image: {e}")
        return 'Error uploading image', 500

@app.route('/face_detection')
def face_detection():
    # Path to the image
    image_path = 'static/main_pic.jpg'
    
    # Detect and draw faces on the image
    img, faces = detect_and_draw_faces(image_path)
    
    # Save the image with detected faces
    cv2.imwrite('static/detected_faces.jpg', img)
    
    return render_template('index.html', faces=faces)

@app.route('/select_face', methods=['POST'])
def select_face():
    global selected_face
    
    # Get the selected face coordinates from the form
    face_index = int(request.form['face_index'])
    image_path = 'static/main_pic.jpg'
    
    # Load the original image
    img_original = cv2.imread(image_path)
    
    # Retrieve the selected face coordinates
    faces = request.form.getlist('faces')
    x, y, width, height = map(int, faces[face_index].split(','))
    
    # Crop the selected face from the original image
    cropped_face = img_original[y:y + height, x:x + width]
    
    # Save the cropped face image directly to the file path
    cropped_face_path = 'static\cropped.jpg'
    cv2.imwrite(cropped_face_path, cropped_face)

    # Initialize Firefox WebDriver with headless mode
    options = Options()
    #options.add_argument("-headless") #Remove first hashtag to hide browser movement
    service = Service('geckodriver.exe')
    driver = webdriver.Firefox(service=service, options=options)

    # Open Google Images
    driver.get('https://images.google.com/')

    # Wait for the cam button to be clickable and click it
    cam_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Search by image' and @role='button']"))
    )
    cam_button.click()

    # Directly interact with the file input element
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    time.sleep(3)
    file_input.send_keys(os.path.join(os.getcwd(), "static\cropped.jpg"))

    # Wait for the upload to complete
    time.sleep(5)

    # Locate the search bar using the provided XPath
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='APjFqb']"))
    )

    # Type "LinkedIn" into the search bar and submit the search
    search_bar.clear()
    search_bar.send_keys("LinkedIn")
    search_bar.send_keys(Keys.RETURN)

    # Wait for a few seconds to see the results
    time.sleep(10)

    driver.quit()
    
    return jsonify({"message": "Face image saved successfully and searched on google!", "face_path": cropped_face_path})

if __name__ == "__main__":
    app.run(debug=True)
