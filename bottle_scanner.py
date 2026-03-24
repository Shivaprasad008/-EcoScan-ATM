import cv2
import numpy as np

def scan_bottle(image_path):
    """
    Mock implementation of a bottle scanner using OpenCV.
    In a real scenario, this would use a pre-trained ML model (e.g. YOLO)
    or advanced contour detection to precisely identify a plastic bottle.
    
    Here, we'll do simple contour detection and return True if we find
    any contour that has a reasonable area.
    """
    try:
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return False, "Could not read image."
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian Blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge Detection
        edged = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Check if any contour has a significant area
        min_contour_area = 500  # Adjust as needed based on image size
        valid_contours = [c for c in contours if cv2.contourArea(c) > min_contour_area]
        
        if len(valid_contours) > 0:
            return True, "Plastic bottle detected successfully!"
        else:
            return False, "No valid bottle shape detected."
            
    except Exception as e:
        return False, str(e)
