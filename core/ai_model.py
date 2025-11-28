"""
    1. Import các thư viện cần thiết
"""
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing import image
import numpy as np
from PIL import Image

"""
    2. Định nghĩa lớp Trích xuất ra các đặc trưng ảnh để so sánh với vector dữ liệu từ CSDL
"""
class FeatureExtractor:
    def __init__(self):
        # Load model MobileNetV2
        # include_top=False để lấy ra các đặc trưng thay vì nhãn của ảnh đầu vào
        # Pooling='avg' để output ra vector 1 chiều
        self.model = MobileNetV2(weights='imagenet', include_top=False, pooling='avg')
        print("MobileNetV2 loaded successfully.")

    def extract(self, img):
        """
        Input: img là đối tượng PIL Image hoặc numpy array từ OpenCV
        Output: Vector đặc trưng (numpy array)
        """

        # Resize về 224x224 theo chuẩn model 
        if isinstance(img, np.ndarray):
            img = Image.fromarray(img) # chuyển mảng np về đối tượng Image (mục đích: tương thích với PIL)
        img = img.resize((224, 224))

        x = image.img_to_array(img) # Chuyển lại về array sau khi resize
        x = np.expand_dims(x, axis=0) # mở rộng chiều dữ liệu 3 (ảnh màu) -> 4 (batch)
        x = preprocess_input(x) # chuẩn hóa pixel (màu ảnh) theo kiểu thích hợp MobileNetV2 nhất
        
        feature = self.model.predict(x) # predict đầu ra
        return feature.flatten() # Trả về vector 1 chiều

# if __name__ == "__main__":
#     fe = FeatureExtractor()
#     print("Model ready!")