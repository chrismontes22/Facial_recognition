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

def detect_faces_in_image(image_path: str) -> tuple:
    """Loads the image and uses MTCNN in RGB form for higher facial recognition accuracy."""
    img = cv2.imread(image_path)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    detector = MTCNN()
    detected_faces = detector.detect_faces(img_rgb)
    return img, detected_faces

def draw_rectangles(img: cv2.Mat, detected_faces: list) -> tuple:
    """Draws rectangles around detected faces with padding and returns updated image and face coordinates."""
    faces = []
    for face in detected_faces:
        x, y, width, height = face['box']
        x = max(0, x - 11)
        y = max(0, y - 11)
        width += 22
        height += 22
        faces.append((x, y, width, height))
        cv2.rectangle(img, (x, y), (x + width, y + height), (255, 0, 0), 2)
    return img, faces

def detect_and_draw_faces(image_path: str) -> tuple:
    """Detects faces in the image at the given path and draws rectangles around them."""
    img, detected_faces = detect_faces_in_image(image_path)
    return draw_rectangles(img, detected_faces)

def crop_and_save_face(img: cv2.Mat, x: int, y: int, width: int, height: int) -> str:
    """Crops and saves a face from the image."""
    cropped_face = img[y:y + height, x:x + width]
    cv2.imwrite('static/cropped.jpg', cropped_face)
    return 'static/cropped.jpg'

def initialize_driver() -> webdriver.Firefox:
    """Initializes Firefox WebDriver."""
    options = Options()
    service = Service('geckodriver.exe')
    return webdriver.Firefox(service=service, options=options)

def search_with_cropped_face(driver: webdriver.Firefox, cropped_face_path: str) -> str:
    """Uploads the cropped face image to Google Images and searches."""
    driver.get('https://images.google.com/')
    cam_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Search by image' and @role='button']"))
    )
    cam_button.click()
    
    return upload_and_search(driver, cropped_face_path)

def upload_and_search(driver: webdriver.Firefox, cropped_face_path: str) -> str:
    """Uploads the image and performs the search."""
    file_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
    )
    time.sleep(3)
    file_input.send_keys(os.path.join(os.getcwd(), "static", "cropped.jpg"))
    
    return finalize_search(driver)

def finalize_search(driver: webdriver.Firefox) -> str:
    """Finalizes the search by entering a search term and submitting."""
    time.sleep(5)
    search_bar = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='APjFqb']"))
    )
    search_bar.clear()
    search_bar.send_keys("LinkedIn")
    search_bar.send_keys(Keys.RETURN)
    time.sleep(10)
    driver.quit()
    
    return jsonify({"message": "Face image saved successfully and searched on google!", "face_path": "static/cropped.jpg"})

@app.route("/")
def home() -> str:
    """Loads and renders the home page HTML."""
    return render_template('workingindex.html')

@app.route("/capture", methods=["POST"])
def capture_image() -> str:
    """Captures image from request, saves it, and redirects to face detection."""
    try:
        if 'image' not in request.files:
            return 'No image captured', 400
        file = request.files['image']
        file.save('static/main_pic.jpg')
        return redirect(url_for('face_detection'))
    except Exception as e:
        print(f"Error capturing image: {e}")
        return 'Error capturing image', 500

@app.route("/upload", methods=["POST"])
def upload_image() -> str:
    """Uploads image from request, saves it, and redirects to face detection."""
    try:
        if 'image' not in request.files:
            return 'No image uploaded', 400
        file = request.files['image']
        file.save('static/main_pic.jpg')
        return redirect(url_for('face_detection'))
    except Exception as e:
        print(f"Error uploading image: {e}")
        return 'Error uploading image', 500

@app.route('/face_detection')
def face_detection() -> str:
    """Detects faces in the saved image, draws rectangles, and renders result."""
    image_path = 'static/main_pic.jpg'
    img, faces = detect_and_draw_faces(image_path)
    cv2.imwrite('static/detected_faces.jpg', img)
    return render_template('index.html', faces=faces)

@app.route('/select_face', methods=['POST'])
def select_face() -> str:
    """Selects a face from the detected faces, crops and saves it, and performs a Google search."""
    face_index = int(request.form['face_index'])
    image_path = 'static/main_pic.jpg'
    img = cv2.imread(image_path)
    faces = request.form.getlist('faces')
    x, y, width, height = map(int, faces[face_index].split(','))
    cropped_face_path = crop_and_save_face(img, x, y, width, height)
    
    driver = initialize_driver()
    return search_with_cropped_face(driver, cropped_face_path)

if __name__ == "__main__":
    app.run(debug=True)
