# Các hàm lọc nhiễu, tách nền (OpenCV)
import cv2
import numpy as np
from PIL import Image

class ImagePreprocessor:
    @staticmethod
    def preprocess(image_input, target_size=(224, 224)):
        """
        Hàm xử lý tổng hợp: Resize -> Khử nhiễu
        
        Input: 
            image_input: Có thể là PIL Image hoặc Numpy Array
        Output: 
            Numpy array đã resize và khử nhiễu, sẵn sàng cho AI.
        """
        # Chuyển đổi PIL sang Numpy nếu cần
        if isinstance(image_input, Image.Image):
            image_array = np.array(image_input)
        else:
            image_array = image_input

        # 1. Resize về kích thước chuẩn của MobileNetV2 (224x224)
        resized = cv2.resize(image_array, target_size)
        
        # 2. Khử nhiễu (Gaussian Blur) - Giúp loại bỏ nhiễu hạt từ webcam
        denoised = cv2.GaussianBlur(resized, (3, 3), 0)
        
        return denoised

    @staticmethod
    def crop_center_square(image_array):
        """
        Cắt lấy phần trung tâm ảnh thành hình vuông trước khi resize
        để tránh bị méo hình.
        """
        h, w = image_array.shape[:2]
        min_dim = min(h, w)
        start_x = (w - min_dim) // 2
        start_y = (h - min_dim) // 2
        return image_array[start_y:start_y+min_dim, start_x:start_x+min_dim]