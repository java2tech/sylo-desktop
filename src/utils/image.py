import cv2
import base64

def cv2_to_base64(image):
    _, buffer = cv2.imencode('.png', image)
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str
