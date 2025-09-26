import cv2
import base64

def cv2_to_base64(image):
    ok, buffer = cv2.imencode('.png', image)
    if not ok:
        raise RuntimeError("cv2.imencode() 실패")
    img_str = base64.b64encode(buffer).decode('utf-8')
    return img_str
