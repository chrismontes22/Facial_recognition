import tkinter as tk
from tkinter import filedialog
import shutil
from mtcnn import MTCNN
import cv2

def select_file_and_save():
    # Create a root window and hide it
    root = tk.Tk()
    root.withdraw()

    # Open the file explorer dialog with file type restriction
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.webp;*.bmp")]
    )

    # Check if a file was selected
    if file_path:
        print("Selected file:", file_path)
        
        # Save the selected file as "main_pic.jpg"
        save_path = "test_pic.jpg"
        shutil.copy(file_path, save_path)
        print(f"File saved as '{save_path}'")
    else:
        print("No file selected.")

select_file_and_save()

selected_face = None

def mouse_callback(event, x, y, flags, param):
    global selected_face
    if event == cv2.EVENT_LBUTTONDOWN:
        for face in param['faces']:
            fx, fy, fwidth, fheight = face
            if fx <= x <= fx + fwidth and fy <= y <= fy + fheight:
                selected_face = face
                
                # Reload the original image to remove rectangles
                img_original = cv2.imread(param['image_path'])
                
                # Adjust the coordinates with the scale factor and padding
                new_width = int(fwidth * param['scale_factor'])
                new_height = int(fheight * param['scale_factor'])
                fx = int(fx - (new_width - fwidth) / 2)
                fy = int(fy - (new_height - fheight) / 2)
                fx = max(0, fx - param['padding'])
                fy = max(0, fy - param['padding'])
                new_width = new_width + 2 * param['padding']
                new_height = new_height + 2 * param['padding']
                
                # Crop the selected face from the original image
                cropped_face = img_original[fy:fy + new_height, fx:fx + new_width]
                cv2.imwrite('cropped.jpg', cropped_face)
                print("Selected face saved as 'cropped.jpg'")
                
                # Close the window
                cv2.destroyAllWindows()
                break

def detect_and_draw_faces(image_path, scale_factor, padding):  # Adjust the default scale_factor to 1.0
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
    
    # Set up mouse callback to select face
    cv2.namedWindow('Detected Faces')
    cv2.setMouseCallback('Detected Faces', mouse_callback, param={'faces': faces, 'image_path': image_path, 'scale_factor': scale_factor, 'padding': padding})
    
    # Display the image with the rectangles and wait for user interaction
    cv2.imshow('Detected Faces', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return img

# Example usage
image_path = 'test_pic.jpg'
detected_faces_image = detect_and_draw_faces(image_path, scale_factor=1.0, padding=11)  # Use default scale_factor of 1.0


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# Initialize Firefox WebDriver with headless mode
options = Options()
options.headless = True
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
file_input.send_keys(os.path.join(os.getcwd(), "cropped.jpg"))

# Wait for the upload to complete
time.sleep(5)

# Locate the search bar using the provided XPath
search_bar = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[@id='APjFqb']"))
)

# Type "LinkedIn" into the search bar and submit the search
search_bar.clear()
search_bar.send_keys("facebook")
search_bar.send_keys(Keys.RETURN)

# Wait for a few seconds to see the results
time.sleep(10)


# Close the browser
driver.quit()
